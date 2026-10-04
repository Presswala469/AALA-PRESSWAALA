from decimal import Decimal, ROUND_HALF_UP

from app.modules.invoices import repository as repo
from app.modules.orders.service import get as get_order
from app.modules.company.repository import get_company
from app.modules.payments import repository as payment_repo

_MONEY = Decimal('0.01')


def _money(value):
    return Decimal(str(value or 0)).quantize(_MONEY, rounding=ROUND_HALF_UP)


def _tax_breakup(taxable, rate, mode):
    tax = _money(taxable * rate / Decimal('100'))
    if mode == 'INTRA':
        cgst = _money(tax / 2)
        sgst = _money(tax - cgst)
        return tax, cgst, sgst, Decimal('0')
    if mode == 'INTER':
        return tax, Decimal('0'), Decimal('0'), tax
    return Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0')


def _customer_snapshot(order):
    # Keep this deterministic and avoid exposing extra customer data when it is unavailable.
    return {'customer_id': order.get('customer_id'), 'address_id': order.get('address_id')}


def _order_snapshot(order):
    return {
        'order_id': order.get('order_id'), 'service_code': order.get('service_code'),
        'pickup_slot_id': order.get('pickup_slot_id'), 'status': order.get('status'),
        'currency': order.get('currency'), 'payment_method': order.get('payment_method'),
        'subtotal': str(order.get('subtotal')), 'discount': str(order.get('discount')),
        'total': str(order.get('total')), 'items': order.get('items', []),
    }


def create(order_id, tax_amount=None, tax_type='GST', tax_mode='INTRA', payment_reference=None, tax_rate=None):
    order = get_order(order_id)
    if not order:
        raise ValueError('Order not found')
    existing = repo.by_order(order_id)
    if any(x.get('status') in {'DRAFT', 'ISSUED', 'PAID'} for x in existing):
        raise ValueError('Active invoice already exists for this order')
    legacy_fixed_tax = tax_rate is None and tax_amount is not None
    if tax_rate is None:
        tax_rate = Decimal('0')
    if tax_type == 'NONE':
        tax_rate = Decimal('0'); tax_mode = 'NONE'
    company = get_company()
    prefix = company.get('invoice_prefix') or 'APW'
    invoice_number = repo.next_invoice_number(prefix, order_id)
    subtotal = _money(order['subtotal'])
    discount = _money(order['discount'])
    taxable_total = _money(subtotal - discount)
    rate = Decimal(str(tax_rate))

    item_source = order.get('items') or []
    items = []
    order_discount_remaining = discount
    base_total = _money(sum((Decimal(str(x.get('quantity', 0))) * Decimal(str(x.get('unit_price', 0))) for x in item_source), Decimal('0')))
    for index, source in enumerate(item_source):
        qty = Decimal(str(source.get('quantity', 0)))
        unit = _money(source.get('unit_price', 0))
        line_base = _money(qty * unit)
        if index == len(item_source) - 1:
            line_discount = _money(order_discount_remaining)
        elif base_total > 0:
            line_discount = _money(discount * line_base / base_total)
            line_discount = min(line_discount, order_discount_remaining)
        else:
            line_discount = Decimal('0')
        order_discount_remaining = _money(order_discount_remaining - line_discount)
        line_taxable = _money(line_base - line_discount)
        line_tax, _, _, _ = _tax_breakup(line_taxable, rate, tax_mode)
        items.append({
            'garment_code': source.get('garment_code'),
            'description': source.get('garment_code') or 'Laundry service item',
            'quantity': qty, 'unit_price': unit, 'line_discount': line_discount,
            'taxable_amount': line_taxable, 'tax_rate': rate, 'tax_amount': line_tax,
            'line_total': _money(line_taxable + line_tax),
        })

    # If order has no line items, calculate tax against order taxable amount.
    # Preserve order-level commercial total and add only the newly calculated tax.
    if legacy_fixed_tax:
        tax_amount_value = _money(tax_amount)
        if tax_mode == 'INTRA':
            cgst = _money(tax_amount_value / 2); sgst = _money(tax_amount_value - cgst); igst = Decimal('0')
        elif tax_mode == 'INTER':
            cgst = Decimal('0'); sgst = Decimal('0'); igst = tax_amount_value
        else:
            cgst = Decimal('0'); sgst = Decimal('0'); igst = Decimal('0')
        tax_amount_value = tax_amount_value
        total = _money(order['total'] + tax_amount_value)
    else:
        tax_amount_value, cgst, sgst, igst = _tax_breakup(taxable_total, rate, tax_mode)
        total = _money(taxable_total + tax_amount_value)
    if payment_reference is None:
        payments = payment_repo.list_for_order(order_id)
        if payments:
            latest = payments[0]
            payment_reference = latest.get('provider_payment_id') or latest.get('payment_id')

    return repo.create({
        'order_id': order_id, 'invoice_number': invoice_number, 'company_snapshot': company,
        'customer_snapshot': _customer_snapshot(order), 'order_snapshot': _order_snapshot(order),
        'subtotal': subtotal, 'discount': discount, 'tax_amount': tax_amount_value, 'tax_rate': rate,
        'cgst_amount': cgst, 'sgst_amount': sgst, 'igst_amount': igst, 'tax_type': tax_type,
        'total': total, 'currency': order['currency'], 'payment_reference': payment_reference,
        'status': 'ISSUED',
    }, items)


def get(invoice_id): return repo.get(invoice_id)
def by_order(order_id): return repo.by_order(order_id)


def pdf(invoice_id: str) -> bytes:
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    invoice = get(invoice_id)
    if not invoice:
        raise ValueError('Invoice not found')
    company = invoice.get('company_snapshot') or {}
    buf = BytesIO(); c = canvas.Canvas(buf, pagesize=A4); _, height = A4; y = height - 50
    c.setFont('Helvetica-Bold', 16); c.drawString(40, y, company.get('display_name') or company.get('legal_name') or 'AALA PRESSWAALA'); y -= 24
    c.setFont('Helvetica', 9)
    for line in [company.get('registered_address'), company.get('city'), company.get('gstin')]:
        if line: c.drawString(40, y, str(line)); y -= 14
    y -= 10; c.setFont('Helvetica-Bold', 13); c.drawString(40, y, 'TAX INVOICE'); y -= 22; c.setFont('Helvetica', 10)
    fields = [
        ('Invoice', invoice.get('invoice_number')), ('Order', invoice.get('order_id')), ('Issued', invoice.get('issued_at')),
        ('Subtotal', invoice.get('subtotal')), ('Discount', invoice.get('discount')), ('Taxable', _money(invoice.get('subtotal')) - _money(invoice.get('discount'))),
        ('CGST', invoice.get('cgst_amount')), ('SGST', invoice.get('sgst_amount')), ('IGST', invoice.get('igst_amount')),
        ('Tax', invoice.get('tax_amount')), ('Total', invoice.get('total')), ('Payment', invoice.get('payment_reference')),
    ]
    for label, value in fields:
        c.drawString(40, y, f'{label}: {value}'); y -= 17
    c.setFont('Helvetica-Oblique', 8)
    if company.get('invoice_footer'): c.drawString(40, 55, str(company['invoice_footer'])[:140])
    c.showPage(); c.save(); return buf.getvalue()

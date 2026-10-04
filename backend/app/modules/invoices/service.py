from decimal import Decimal
from app.modules.invoices import repository as repo
from app.modules.orders.service import get as get_order
from app.modules.company.repository import get_company

def create(order_id, tax_amount=Decimal('0')):
    order=get_order(order_id)
    if not order: raise ValueError('Order not found')
    existing=repo.by_order(order_id)
    if existing: return existing[0]
    company=get_company()
    prefix=company.get('invoice_prefix') or 'APW'
    invoice_number=f"{prefix}-{order_id.replace('ORD-','')}"
    tax=Decimal(str(tax_amount)); total=Decimal(str(order['total']))+tax
    return repo.create({'order_id':order_id,'invoice_number':invoice_number,'company_snapshot':company,'subtotal':order['subtotal'],'discount':order['discount'],'tax_amount':tax,'total':total,'currency':order['currency']})
def get(invoice_id): return repo.get(invoice_id)
def by_order(order_id): return repo.by_order(order_id)




def pdf(invoice_id: str) -> bytes:
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    invoice = get(invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")
    company = invoice.get("company_snapshot") or {}
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, company.get("display_name") or company.get("legal_name") or "AALA PRESSWAALA")
    y -= 24
    c.setFont("Helvetica", 9)
    for line in [company.get("registered_address"), company.get("city"), company.get("gstin")]:
        if line:
            c.drawString(40, y, str(line)); y -= 14
    y -= 10
    c.setFont("Helvetica-Bold", 13); c.drawString(40, y, "TAX INVOICE"); y -= 22
    c.setFont("Helvetica", 10)
    fields = [
        ("Invoice", invoice.get("invoice_number")),
        ("Order", invoice.get("order_id")),
        ("Issued", invoice.get("issued_at")),
        ("Subtotal", invoice.get("subtotal")),
        ("Discount", invoice.get("discount")),
        ("Tax", invoice.get("tax_amount")),
        ("Total", invoice.get("total")),
    ]
    for label, value in fields:
        c.drawString(40, y, f"{label}: {value}"); y -= 17
    c.setFont("Helvetica-Oblique", 8)
    if company.get("invoice_footer"):
        c.drawString(40, 55, str(company["invoice_footer"])[:140])
    c.showPage(); c.save()
    return buf.getvalue()

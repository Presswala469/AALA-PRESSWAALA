-- Phase 6A: Invoice + Tax Engine
-- Additive migration; preserves existing invoice/payment/order data.

alter table if exists invoices
    add column if not exists customer_snapshot jsonb not null default '{}'::jsonb,
    add column if not exists order_snapshot jsonb not null default '{}'::jsonb,
    add column if not exists tax_rate numeric(7,4) not null default 0,
    add column if not exists cgst_amount numeric(12,2) not null default 0,
    add column if not exists sgst_amount numeric(12,2) not null default 0,
    add column if not exists igst_amount numeric(12,2) not null default 0,
    add column if not exists tax_type varchar(20) not null default 'GST',
    add column if not exists payment_reference varchar(160),
    add column if not exists status varchar(30) not null default 'ISSUED',
    add column if not exists updated_at timestamptz not null default now();

create index if not exists ix_invoices_status on invoices(status, issued_at desc);
create index if not exists ix_invoices_payment_reference on invoices(payment_reference) where payment_reference is not null;
create unique index if not exists ux_invoices_order_active
    on invoices(order_id)
    where status in ('DRAFT','ISSUED','PAID');

create table if not exists invoice_items (
    id bigserial primary key,
    invoice_item_id varchar(60) unique not null,
    invoice_id varchar(60) not null references invoices(invoice_id) on delete cascade,
    garment_code varchar(80),
    description varchar(255) not null,
    quantity numeric(12,3) not null check (quantity > 0),
    unit_price numeric(12,2) not null check (unit_price >= 0),
    line_discount numeric(12,2) not null default 0 check (line_discount >= 0),
    taxable_amount numeric(12,2) not null check (taxable_amount >= 0),
    tax_rate numeric(7,4) not null default 0,
    tax_amount numeric(12,2) not null default 0 check (tax_amount >= 0),
    line_total numeric(12,2) not null check (line_total >= 0),
    created_at timestamptz not null default now()
);
create index if not exists ix_invoice_items_invoice on invoice_items(invoice_id, id);

create table if not exists invoice_audit_events (
    id bigserial primary key,
    invoice_id varchar(60) not null references invoices(invoice_id) on delete cascade,
    action varchar(80) not null,
    actor_user_id uuid,
    old_values jsonb,
    new_values jsonb,
    created_at timestamptz not null default now()
);
create index if not exists ix_invoice_audit_invoice on invoice_audit_events(invoice_id, created_at desc);

-- Backfill existing invoice rows safely.
update invoices
set status = coalesce(nullif(status,''),'ISSUED'),
    customer_snapshot = coalesce(customer_snapshot,'{}'::jsonb),
    order_snapshot = coalesce(order_snapshot,'{}'::jsonb),
    updated_at = coalesce(updated_at, issued_at, now())
where status is null or status = ''
   or customer_snapshot is null
   or order_snapshot is null
   or updated_at is null;

insert into permissions(code, name) values
('invoice.read','Read invoices'),
('invoice.manage','Create and manage invoices')
on conflict(code) do nothing;

insert into role_permissions(role_id, permission_id)
select r.id, p.id from roles r cross join permissions p
where r.code in ('super_admin','admin') and p.code = 'invoice.manage'
on conflict do nothing;

insert into role_permissions(role_id, permission_id)
select r.id, p.id from roles r cross join permissions p
where r.code in ('super_admin','admin','station_manager','customer') and p.code = 'invoice.read'
on conflict do nothing;

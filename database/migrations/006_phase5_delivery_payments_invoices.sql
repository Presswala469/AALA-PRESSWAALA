create table if not exists delivery_jobs (
 id bigserial primary key, delivery_job_id varchar(60) unique not null, order_id varchar(60) not null,
 partner_id varchar(60) not null, status varchar(40) not null, assigned_at timestamptz,
 created_at timestamptz not null default now()
);
create index if not exists ix_delivery_jobs_order on delivery_jobs(order_id);
create index if not exists ix_delivery_jobs_partner on delivery_jobs(partner_id,status);

create table if not exists payments (
 id bigserial primary key, payment_id varchar(60) unique not null, order_id varchar(60) not null,
 method varchar(20) not null, amount numeric(12,2) not null, currency varchar(10) not null default 'INR',
 status varchar(30) not null, provider varchar(40) not null, provider_order_id varchar(120),
 provider_payment_id varchar(120), created_at timestamptz not null default now(), updated_at timestamptz
);
create index if not exists ix_payments_order on payments(order_id,created_at);

create table if not exists invoices (
 id bigserial primary key, invoice_id varchar(60) unique not null, order_id varchar(60) not null,
 invoice_number varchar(100) unique not null, company_snapshot jsonb not null,
 subtotal numeric(12,2) not null, discount numeric(12,2) not null default 0,
 tax_amount numeric(12,2) not null default 0, total numeric(12,2) not null,
 currency varchar(10) not null default 'INR', issued_at timestamptz not null default now()
);
create index if not exists ix_invoices_order on invoices(order_id,issued_at);

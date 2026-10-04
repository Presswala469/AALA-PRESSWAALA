-- Phase 8: controlled report/export audit
create table if not exists report_exports(id uuid primary key default gen_random_uuid(), report_name varchar(100) not null, format varchar(20) not null, filters jsonb, requested_by uuid references users(id) on delete set null, status varchar(20) not null default 'GENERATED', row_count integer not null default 0, created_at timestamptz not null default now());
create index if not exists ix_report_exports_created on report_exports(created_at desc);

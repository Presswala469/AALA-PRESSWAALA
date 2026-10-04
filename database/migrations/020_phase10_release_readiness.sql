-- Phase 10: release gate metadata
create table if not exists release_checklist(id uuid primary key default gen_random_uuid(), release_version varchar(50) not null, check_name varchar(120) not null, status varchar(20) not null, evidence text, checked_by uuid references users(id) on delete set null, checked_at timestamptz not null default now(), unique(release_version,check_name));
create index if not exists ix_release_checklist_version on release_checklist(release_version);

-- Phase 9: QA/security evidence registry
create table if not exists qa_test_runs(id uuid primary key default gen_random_uuid(), suite varchar(100) not null, result varchar(20) not null, passed integer not null default 0, failed integer not null default 0, environment varchar(50), evidence jsonb, executed_at timestamptz not null default now());
create index if not exists ix_qa_test_runs_executed on qa_test_runs(executed_at desc);

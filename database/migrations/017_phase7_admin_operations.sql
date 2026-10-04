-- Phase 7: operational admin control/audit support
create table if not exists admin_action_log(id uuid primary key default gen_random_uuid(), actor_user_id uuid references users(id) on delete set null, action varchar(80) not null, entity_type varchar(80), entity_id varchar(120), details jsonb, created_at timestamptz not null default now());
create index if not exists ix_admin_action_log_created on admin_action_log(created_at desc);
create index if not exists ix_admin_action_log_entity on admin_action_log(entity_type,entity_id);

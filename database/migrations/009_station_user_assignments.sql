-- AALA PRESSWAALA — Phase 8
-- Station User Assignment / Station Isolation
-- PostgreSQL / Supabase compatible

create table if not exists user_station_assignments (
    id bigserial primary key,
    user_id uuid not null references users(id) on delete cascade,
    station_code varchar(80) not null,
    active boolean not null default true,
    assigned_at timestamptz not null default now(),
    ended_at timestamptz,
    created_at timestamptz not null default now(),
    constraint chk_user_station_assignment_dates check (ended_at is null or ended_at >= assigned_at)
);
create unique index if not exists ux_user_active_station_assignment on user_station_assignments(user_id) where active=true;
create index if not exists ix_user_station_assignments_station on user_station_assignments(station_code);
create index if not exists ix_user_station_assignments_user on user_station_assignments(user_id);
create index if not exists ix_user_station_assignments_active on user_station_assignments(user_id, active);

-- AALA PRESSWAALA — Phase 7 Admin control, inventory, RBAC/audit
create table if not exists bags_boxes (
    id uuid primary key default gen_random_uuid(),
    inventory_id varchar(40) not null unique,
    item_type varchar(30) not null,
    item_code varchar(80),
    status varchar(30) not null default 'AVAILABLE',
    holder_type varchar(30),
    holder_id varchar(80),
    location varchar(120),
    remarks text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists ix_bags_boxes_status on bags_boxes(status);
create index if not exists ix_bags_boxes_holder on bags_boxes(holder_id);
create table if not exists inventory_movements (
    id uuid primary key default gen_random_uuid(),
    inventory_id varchar(40) not null,
    action varchar(50) not null,
    actor varchar(120),
    old_values jsonb,
    new_values jsonb,
    remarks text,
    evidence_url text,
    created_at timestamptz not null default now()
);
create index if not exists ix_inventory_movements_inventory on inventory_movements(inventory_id,created_at);
create table if not exists business_settings (
    key varchar(120) primary key,
    value jsonb not null,
    updated_by uuid references users(id) on delete set null,
    updated_at timestamptz not null default now()
);
create index if not exists ix_audit_logs_entity on audit_logs(entity_type,created_at desc);

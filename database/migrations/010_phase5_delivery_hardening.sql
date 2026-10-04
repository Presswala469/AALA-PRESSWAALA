-- AALA PRESSWAALA — Phase 5 Delivery Hardening
-- PostgreSQL / Supabase compatible

create table if not exists delivery_codes (
    id bigserial primary key,
    order_id varchar(60) not null,
    delivery_code_hash varchar(128) not null,
    active boolean not null default true,
    generated_at timestamptz not null default now(),
    used_at timestamptz,
    invalidated_at timestamptz,
    created_at timestamptz not null default now()
);
create unique index if not exists ux_delivery_codes_active_order
    on delivery_codes(order_id) where active = true;
create index if not exists ix_delivery_codes_order
    on delivery_codes(order_id, created_at desc);

create table if not exists delivery_events (
    id bigserial primary key,
    order_id varchar(60) not null,
    partner_id varchar(60) not null,
    delivery_mode varchar(40) not null,
    receiver_name varchar(150),
    receiver_mobile varchar(30),
    latitude numeric(10,7),
    longitude numeric(10,7),
    evidence_url text,
    house_number varchar(100),
    reason text,
    remarks text,
    delivered_at timestamptz not null default now(),
    created_at timestamptz not null default now()
);
create index if not exists ix_delivery_events_order
    on delivery_events(order_id, created_at desc);
create index if not exists ix_delivery_events_partner
    on delivery_events(partner_id, created_at desc);

alter table if exists hangers
    add column if not exists pending_since timestamptz;

create index if not exists ix_hangers_pending_since
    on hangers(status, pending_since);

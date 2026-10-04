create table if not exists partners (
 id uuid primary key default gen_random_uuid(), partner_id varchar(60) not null unique,
 employee_id varchar(60) not null unique, name varchar(150) not null, mobile_number varchar(30) not null,
 active boolean not null default true, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists partner_station_assignments (
 id bigserial primary key, partner_id varchar(60) not null references partners(partner_id),
 station_code varchar(80) not null, active boolean not null default true,
 assigned_at timestamptz not null default now(), ended_at timestamptz
);
create unique index if not exists ux_partner_active_assignment on partner_station_assignments(partner_id) where active=true;
create table if not exists partner_activity (
 id bigserial primary key, partner_id varchar(60) not null, order_id varchar(60), activity_type varchar(60) not null,
 latitude numeric(10,7), longitude numeric(10,7), quantity integer, evidence_url text, reason text, remarks text,
 created_at timestamptz not null default now()
);
create table if not exists station_receiving (
 id bigserial primary key, order_id varchar(60) not null unique, partner_id varchar(60) not null,
 station_code varchar(80), partner_handover_quantity integer not null check(partner_handover_quantity>=0),
 station_received_quantity integer not null check(station_received_quantity>=0), discrepancy boolean not null default false,
 reason text, remarks text, received_at timestamptz not null default now()
);
create table if not exists pickup_records (
 id bigserial primary key, order_id varchar(60) not null unique, partner_id varchar(60) not null,
 arrived_at timestamptz, latitude numeric(10,7), longitude numeric(10,7), handover_quantity integer,
 customer_confirmed boolean not null default false, bag_id varchar(80), completed_at timestamptz, notes text
);
create table if not exists garment_damage_evidence (
 id bigserial primary key, order_id varchar(60) not null, partner_id varchar(60) not null,
 item_ref varchar(80) not null, photo_url text not null, description text, created_at timestamptz not null default now()
);
create index if not exists ix_partner_activity_order on partner_activity(order_id,created_at);

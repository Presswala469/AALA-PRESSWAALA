-- AALA PRESSWAALA — Phase 1-5 completion support
-- Additive / PostgreSQL / Supabase compatible.
-- Aligns with the live schema verified during v1.17.

-- Customer identity binding for object-level authorization.
alter table if exists customers
    add column if not exists user_id uuid references users(id) on delete restrict;
create unique index if not exists ux_customers_user_id
    on customers(user_id) where user_id is not null;

update customers c
set user_id = u.id
from users u
where c.user_id is null
  and c.mobile_number = u.mobile_number;


-- Phase 1 profile and zone controls.
alter table if exists customers add column if not exists alternate_mobile varchar(20);
alter table if exists customers add column if not exists photo_url text;

create table if not exists zones (
    id uuid primary key default gen_random_uuid(),
    zone_code varchar(60) not null unique,
    name varchar(120) not null,
    city varchar(100),
    active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create table if not exists user_zone_assignments (
    id bigserial primary key,
    user_id uuid not null references users(id) on delete cascade,
    zone_id uuid not null references zones(id) on delete cascade,
    active boolean not null default true,
    assigned_at timestamptz not null default now(),
    ended_at timestamptz,
    created_at timestamptz not null default now()
);
create unique index if not exists ux_user_active_zone_assignment
    on user_zone_assignments(user_id,zone_id) where active=true;
create index if not exists ix_user_zone_assignment_zone
    on user_zone_assignments(zone_id,active);

-- Seed the permission vocabulary used by backend RBAC.
insert into permissions(code,name) values
('company.read','Read company configuration'),
('company.manage','Manage company configuration'),
('customer.read','Read customer records'),
('customer.manage','Manage customer records'),
('inventory.read','Read inventory'),
('inventory.manage','Manage inventory'),
('audit.read','Read audit logs'),
('company.documents.manage','Manage company documents'),
('station.read','Read assigned station operations'),
('station.manage','Manage assigned station operations'),
('partner.manage','Manage partner assignments'),
('delivery.manage','Manage delivery operations'),
('rating.create','Create customer rating')
on conflict(code) do nothing;

insert into role_permissions(role_id,permission_id)
select r.id,p.id from roles r cross join permissions p
where r.code='super_admin'
on conflict do nothing;

insert into role_permissions(role_id,permission_id)
select r.id,p.id from roles r join permissions p on p.code in ('company.read','company.manage','customer.read','customer.manage','inventory.read','inventory.manage','audit.read','company.documents.manage','station.read','station.manage','partner.manage','delivery.manage')
where r.code='admin'
on conflict do nothing;

insert into role_permissions(role_id,permission_id)
select r.id,p.id from roles r join permissions p on p.code in ('customer.read','inventory.read','station.read','station.manage','delivery.manage')
where r.code='station_manager'
on conflict do nothing;

insert into role_permissions(role_id,permission_id)
select r.id,p.id from roles r join permissions p on p.code in ('station.read','delivery.manage','rating.create')
where r.code='partner'
on conflict do nothing;

insert into role_permissions(role_id,permission_id)
select r.id,p.id from roles r join permissions p on p.code in ('rating.create')
where r.code='customer'
on conflict do nothing;

-- Historical order snapshots + configurable TAT timestamps.
alter table if exists orders add column if not exists customer_snapshot jsonb;
alter table if exists orders add column if not exists address_snapshot jsonb;
alter table if exists orders add column if not exists booking_snapshot jsonb;
alter table if exists orders add column if not exists tat_started_at timestamptz;
alter table if exists orders add column if not exists tat_due_at timestamptz;
alter table if exists orders add column if not exists tat_completed_at timestamptz;

create table if not exists service_tat_rules (
    id uuid primary key default gen_random_uuid(),
    service_code varchar(50) not null unique,
    target_minutes integer not null check(target_minutes > 0),
    urgent_threshold_minutes integer not null default 60 check(urgent_threshold_minutes >= 0),
    active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Station support requests required by Phase 4 operations.
create table if not exists station_support_requests (
    id uuid primary key default gen_random_uuid(),
    request_id varchar(60) not null unique,
    station_code varchar(80) not null,
    order_id varchar(60),
    request_type varchar(50) not null,
    description text not null,
    priority varchar(20) not null default 'NORMAL',
    status varchar(30) not null default 'OPEN',
    created_by uuid references users(id) on delete set null,
    resolved_by uuid references users(id) on delete set null,
    resolved_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists ix_station_support_station_status
    on station_support_requests(station_code,status,created_at desc);

-- Customer rating after successful delivery.
create table if not exists order_ratings (
    id uuid primary key default gen_random_uuid(),
    order_id varchar(60) not null unique,
    customer_id varchar(60) not null,
    stars integer not null check(stars between 1 and 5),
    comment text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists ix_order_ratings_customer
    on order_ratings(customer_id,created_at desc);

-- Delivery code expiry is configurable through the application setting.
alter table if exists delivery_codes
    add column if not exists expires_at timestamptz;
create index if not exists ix_delivery_codes_active_expiry
    on delivery_codes(order_id,active,expires_at);

-- AALA PRESSWAALA — Phase 1 customer/address persistence

create table if not exists customers (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete restrict,
    customer_id varchar(40) not null unique,
    global_customer_number bigint generated always as identity unique,
    name varchar(150) not null,
    mobile_number varchar(20) not null unique,
    email varchar(255),
    status varchar(30) not null default 'active',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists customer_addresses (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete restrict,
    label varchar(50) not null default 'Home',
    address_line text not null,
    city varchar(100) not null,
    state varchar(100) not null,
    pincode varchar(20) not null,
    building_society varchar(255),
    latitude numeric(10,7),
    longitude numeric(10,7),
    is_current boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ix_customer_addresses_customer on customer_addresses(customer_id);
create unique index if not exists ux_customer_current_address on customer_addresses(customer_id) where is_current=true;

create table if not exists customer_address_history (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete restrict,
    source_address_id uuid,
    address_snapshot jsonb not null,
    changed_at timestamptz not null default now(),
    changed_by uuid references users(id) on delete set null
);

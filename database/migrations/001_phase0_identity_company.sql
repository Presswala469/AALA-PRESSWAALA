-- AALA PRESSWAALA — Phase 0/1 persistence baseline
-- PostgreSQL / Supabase compatible

create extension if not exists pgcrypto;

create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    mobile_number varchar(20) not null,
    full_name varchar(150),
    email varchar(255),
    is_active boolean not null default true,
    mobile_verified_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create unique index if not exists ux_users_mobile on users(mobile_number);

create table if not exists roles (
    id uuid primary key default gen_random_uuid(),
    code varchar(50) not null unique,
    name varchar(100) not null,
    created_at timestamptz not null default now()
);

create table if not exists permissions (
    id uuid primary key default gen_random_uuid(),
    code varchar(100) not null unique,
    name varchar(150) not null,
    created_at timestamptz not null default now()
);

create table if not exists user_roles (
    user_id uuid not null references users(id) on delete cascade,
    role_id uuid not null references roles(id) on delete cascade,
    assigned_at timestamptz not null default now(),
    primary key(user_id, role_id)
);

create table if not exists role_permissions (
    role_id uuid not null references roles(id) on delete cascade,
    permission_id uuid not null references permissions(id) on delete cascade,
    assigned_at timestamptz not null default now(),
    primary key(role_id, permission_id)
);

create table if not exists sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    refresh_token_hash text,
    device_id varchar(255),
    platform varchar(30),
    expires_at timestamptz not null,
    revoked_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists company_profiles (
    id uuid primary key default gen_random_uuid(),
    legal_name varchar(255) not null,
    display_name varchar(255) not null,
    logo_url text,
    favicon_url text,
    registered_address text,
    service_address text,
    city varchar(100),
    state varchar(100),
    pincode varchar(20),
    gstin varchar(20),
    pan varchar(20),
    cin varchar(30),
    phone varchar(30),
    email varchar(255),
    website varchar(255),
    support_phone varchar(30),
    support_email varchar(255),
    invoice_prefix varchar(30),
    invoice_terms text,
    invoice_footer text,
    currency varchar(10) not null default 'INR',
    timezone varchar(50) not null default 'Asia/Kolkata',
    terms_url text,
    privacy_url text,
    refund_policy_url text,
    cancellation_policy_url text,
    version integer not null default 1,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists company_documents (
    id uuid primary key default gen_random_uuid(),
    company_profile_id uuid not null references company_profiles(id) on delete restrict,
    document_type varchar(80) not null,
    document_name varchar(255) not null,
    file_url text not null,
    version integer not null default 1,
    is_active boolean not null default true,
    uploaded_by uuid references users(id) on delete set null,
    uploaded_at timestamptz not null default now()
);

create table if not exists audit_logs (
    id uuid primary key default gen_random_uuid(),
    actor_user_id uuid references users(id) on delete set null,
    action varchar(50) not null,
    entity_type varchar(100) not null,
    entity_id uuid,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    device_id varchar(255),
    created_at timestamptz not null default now()
);

create table if not exists security_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete set null,
    event_type varchar(100) not null,
    success boolean not null default true,
    metadata jsonb,
    created_at timestamptz not null default now()
);

insert into roles(code, name) values
('super_admin', 'Super Admin'),
('admin', 'Admin'),
('station_manager', 'Station Manager'),
('partner', 'Partner / Picker'),
('customer', 'Customer')
on conflict (code) do nothing;

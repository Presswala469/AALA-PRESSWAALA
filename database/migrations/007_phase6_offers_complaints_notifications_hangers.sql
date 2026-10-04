create table if not exists offers (
 id bigserial primary key, offer_id varchar(60) unique not null, code varchar(40) unique not null, name varchar(150) not null,
 discount_type varchar(20) not null, discount_value numeric(12,2) not null, start_at timestamptz, end_at timestamptz,
 days jsonb not null default '[]'::jsonb, min_order numeric(12,2) not null default 0, max_discount numeric(12,2), priority integer not null default 0,
 enabled boolean not null default true, customer_type varchar(60), city varchar(100), station_code varchar(60), area varchar(120), building varchar(120), created_at timestamptz not null default now()
);
create index if not exists ix_offers_active_priority on offers(enabled,priority desc);

create table if not exists complaints (
 id bigserial primary key, complaint_id varchar(60) unique not null, order_id varchar(60) not null, customer_id varchar(60) not null,
 category varchar(80) not null, description text not null, status varchar(40) not null, assigned_to varchar(60), remarks text,
 created_at timestamptz not null default now(), updated_at timestamptz
);
create table if not exists complaint_events (
 id bigserial primary key, complaint_id varchar(60) not null, status varchar(40) not null, actor varchar(120), remarks text, created_at timestamptz not null default now()
);
create index if not exists ix_complaints_order on complaints(order_id,created_at);

create table if not exists notifications (
 id bigserial primary key, notification_id varchar(60) unique not null, recipient_id varchar(60) not null,
 channel varchar(20) not null, title varchar(200) not null, message text not null, data jsonb not null default '{}'::jsonb,
 status varchar(30) not null, created_at timestamptz not null default now(), updated_at timestamptz
);
create index if not exists ix_notifications_recipient on notifications(recipient_id,created_at desc);

create table if not exists hangers (
 id bigserial primary key, hanger_id varchar(60) unique not null, customer_id varchar(60) not null, order_id varchar(60), quantity integer not null default 1,
 status varchar(30) not null, created_at timestamptz not null default now(), updated_at timestamptz
);
create table if not exists hanger_return_requests (
 id bigserial primary key, return_request_id varchar(60) unique not null, customer_id varchar(60) not null, address_id varchar(60) not null,
 quantity integer not null, preferred_slot_id varchar(60), status varchar(30) not null, created_at timestamptz not null default now()
);
create table if not exists hanger_movements (
 id bigserial primary key, hanger_id varchar(60) not null, action varchar(50) not null, actor varchar(120), remarks text, created_at timestamptz not null default now()
);

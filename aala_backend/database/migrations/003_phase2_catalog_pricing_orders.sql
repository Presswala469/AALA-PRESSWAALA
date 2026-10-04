-- AALA PRESSWAALA — Phase 2 catalogue, pricing, pickup slots and order engine
create table if not exists services (
 id uuid primary key default gen_random_uuid(), code varchar(50) not null unique, name varchar(150) not null,
 description text, service_type varchar(40) not null default 'standard', active boolean not null default true,
 display_order integer not null default 0, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists garment_categories (
 id uuid primary key default gen_random_uuid(), code varchar(50) not null unique, name varchar(150) not null,
 small_garment boolean not null default false, active boolean not null default true, display_order integer not null default 0,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists service_availability (
 id uuid primary key default gen_random_uuid(), service_code varchar(50) not null, station_code varchar(80),
 area_code varchar(80), active boolean not null default true, created_at timestamptz not null default now(),
 unique(service_code,station_code,area_code)
);
create table if not exists garment_prices (
 id uuid primary key default gen_random_uuid(), service_code varchar(50) not null, garment_code varchar(50) not null,
 station_code varchar(80), unit_price numeric(12,2) not null check(unit_price >= 0), min_quantity integer not null default 1 check(min_quantity >= 1),
 express_surcharge numeric(12,2) not null default 0 check(express_surcharge >= 0), active boolean not null default true,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists ix_garment_prices_lookup on garment_prices(service_code,garment_code,station_code,active);
create table if not exists pickup_slots (
 id uuid primary key default gen_random_uuid(), slot_id varchar(50) not null unique, label varchar(100) not null,
 start_time time not null, end_time time not null, station_code varchar(80), max_orders integer not null default 20 check(max_orders > 0),
 active boolean not null default true, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists orders (
 id uuid primary key default gen_random_uuid(), order_id varchar(60) not null unique, customer_id varchar(60) not null,
 address_id varchar(60) not null, service_code varchar(50) not null, pickup_slot_id varchar(50) not null,
 status varchar(40) not null, currency varchar(10) not null default 'INR', subtotal numeric(12,2) not null,
 discount numeric(12,2) not null default 0, total numeric(12,2) not null, payment_method varchar(30) not null,
 offer_code varchar(80), notes text, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists order_items (
 id bigserial primary key, order_id varchar(60) not null references orders(order_id) on delete cascade,
 garment_code varchar(50) not null, quantity integer not null check(quantity > 0), unit_price numeric(12,2) not null,
 line_total numeric(12,2) not null
);
create table if not exists order_events (
 id bigserial primary key, order_id varchar(60) not null references orders(order_id) on delete cascade,
 event_type varchar(60) not null, from_status varchar(40), to_status varchar(40), actor varchar(120), reason text,
 created_at timestamptz not null default now()
);
create index if not exists ix_order_events_order on order_events(order_id,created_at);

insert into services(code,name,description,service_type,display_order) values
('STANDARD','Standard','Standard ironing service','standard',1),
('OVERNIGHT_EXPRESS','Overnight Express','Priority overnight service','overnight_express',2),
('TWO_HOUR_EXPRESS','2-hour Express','Priority two-hour service','two_hour_express',3)
on conflict(code) do nothing;
insert into garment_categories(code,name,small_garment,display_order) values
('SHIRT','Shirt',false,1),('TROUSER','Trouser',false,2),('T_SHIRT','T-Shirt',true,3),('HANDKERCHIEF','Handkerchief',true,4)
on conflict(code) do nothing;
insert into garment_prices(service_code,garment_code,unit_price) values
('STANDARD','SHIRT',15),('STANDARD','TROUSER',20),('STANDARD','T_SHIRT',10),('STANDARD','HANDKERCHIEF',5),
('OVERNIGHT_EXPRESS','SHIRT',25),('OVERNIGHT_EXPRESS','TROUSER',30),('OVERNIGHT_EXPRESS','T_SHIRT',20),('OVERNIGHT_EXPRESS','HANDKERCHIEF',10),
('TWO_HOUR_EXPRESS','SHIRT',35),('TWO_HOUR_EXPRESS','TROUSER',40),('TWO_HOUR_EXPRESS','T_SHIRT',30),('TWO_HOUR_EXPRESS','HANDKERCHIEF',15)
on conflict do nothing;
insert into pickup_slots(slot_id,label,start_time,end_time,max_orders) values
('MORNING','Morning','09:00','12:00',20),('AFTERNOON','Afternoon','12:00','16:00',20),('EVENING','Evening','16:00','20:00',20)
on conflict(slot_id) do nothing;

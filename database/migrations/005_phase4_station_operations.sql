create table if not exists station_arrivals (
 id bigserial primary key, order_id varchar(60) not null, partner_id varchar(60) not null,
 station_code varchar(80) not null, latitude numeric(10,7) not null, longitude numeric(10,7) not null,
 arrived_at timestamptz not null default now(), created_at timestamptz not null default now()
);
create index if not exists ix_station_arrivals_station on station_arrivals(station_code,arrived_at);

create table if not exists station_status_history (
 id bigserial primary key, order_id varchar(60) not null, station_code varchar(80) not null,
 status varchar(40) not null, reason text, remarks text, actor varchar(120), created_at timestamptz not null default now()
);
create index if not exists ix_station_status_history_order on station_status_history(order_id,created_at);
create index if not exists ix_station_status_history_station on station_status_history(station_code,status,created_at);

create table if not exists station_evidence (
 id bigserial primary key, order_id varchar(60) not null, station_code varchar(80) not null,
 evidence_type varchar(40) not null, evidence_url text not null, remarks text, actor varchar(120),
 created_at timestamptz not null default now()
);
create index if not exists ix_station_evidence_order on station_evidence(order_id,created_at);

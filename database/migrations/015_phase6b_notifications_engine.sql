-- Phase 6B: Production notification engine
-- Safe to run once. If an older 015 was already applied, the statements remain idempotent.

alter table if exists notifications
    add column if not exists event_type varchar(80),
    add column if not exists idempotency_key varchar(160),
    add column if not exists priority varchar(20) not null default 'NORMAL',
    add column if not exists provider varchar(40),
    add column if not exists provider_message_id varchar(200),
    add column if not exists attempt_count integer not null default 0,
    add column if not exists failure_code varchar(80),
    add column if not exists failure_reason text,
    add column if not exists sent_at timestamptz,
    add column if not exists delivered_at timestamptz,
    add column if not exists read_at timestamptz,
    add column if not exists next_retry_at timestamptz,
    add column if not exists max_attempts integer not null default 3;

create unique index if not exists ux_notifications_idempotency
    on notifications(idempotency_key) where idempotency_key is not null;
create index if not exists ix_notifications_status_created
    on notifications(status, created_at desc);
create index if not exists ix_notifications_event_type
    on notifications(event_type, created_at desc);
create index if not exists ix_notifications_recipient_status
    on notifications(recipient_id, status, created_at desc);

create table if not exists notification_devices (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    platform varchar(20) not null,
    token text not null,
    installation_id varchar(200),
    device_id varchar(200),
    app_version varchar(50),
    active boolean not null default true,
    last_seen_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint chk_notification_device_platform check (platform in ('ANDROID','IOS','WEB'))
);
alter table if exists notification_devices
    add column if not exists installation_id varchar(200),
    add column if not exists device_id varchar(200),
    add column if not exists app_version varchar(50);
create unique index if not exists ux_notification_devices_token on notification_devices(token);
create unique index if not exists ux_notification_devices_installation
    on notification_devices(installation_id) where installation_id is not null;
create index if not exists ix_notification_devices_user_active
    on notification_devices(user_id, active);
create index if not exists ix_notification_devices_last_seen
    on notification_devices(last_seen_at desc);

create table if not exists notification_preferences (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    event_type varchar(80) not null,
    channel varchar(20) not null,
    enabled boolean not null default true,
    updated_at timestamptz not null default now(),
    constraint chk_notification_preference_channel
        check (channel in ('IN_APP','PUSH','SMS','WHATSAPP','EMAIL'))
);
create unique index if not exists ux_notification_preferences_user_event_channel
    on notification_preferences(user_id, event_type, channel);

create table if not exists notification_attempts (
    id bigserial primary key,
    notification_id varchar(60) not null references notifications(notification_id) on delete cascade,
    attempt_no integer not null,
    target_token_hash varchar(128),
    provider varchar(40) not null,
    status varchar(30) not null,
    provider_message_id varchar(200),
    error_code varchar(80),
    error_message text,
    attempted_at timestamptz not null default now()
);
alter table if exists notification_attempts
    add column if not exists target_token_hash varchar(128);
create unique index if not exists ux_notification_attempt_no
    on notification_attempts(notification_id, attempt_no);
create index if not exists ix_notification_attempts_notification
    on notification_attempts(notification_id, attempted_at desc);

-- Event catalog documents the workflow event vocabulary used by the backend.
create table if not exists notification_event_types (
    event_type varchar(80) primary key,
    description text not null,
    default_channels varchar(200) not null,
    active boolean not null default true,
    created_at timestamptz not null default now()
);

insert into notification_event_types(event_type,description,default_channels) values
('REGISTRATION','Customer/partner registration or account activation','PUSH,IN_APP'),
('BOOKING','Booking confirmed','PUSH,IN_APP'),
('ASSIGNMENT','Pickup/delivery assignment','PUSH,IN_APP'),
('ARRIVAL_PICKUP','Partner arrival/pickup event','PUSH,IN_APP'),
('STATION_RECEIPT','Order received at station','PUSH,IN_APP'),
('STATUS','Order status update','PUSH,IN_APP'),
('READY','Order ready for delivery','PUSH,IN_APP'),
('OUT_FOR_DELIVERY','Order out for delivery','PUSH,IN_APP'),
('DELIVERED','Order delivered','PUSH,IN_APP'),
('INVOICE','Invoice generated','PUSH,IN_APP,EMAIL'),
('OFFERS','Offer/promotion','PUSH,IN_APP'),
('DELAY','Delay/TAT alert','PUSH,IN_APP'),
('SERVICE_AVAILABILITY','Service availability update','PUSH,IN_APP'),
('COMPLAINT','Complaint update','PUSH,IN_APP'),
('OTP','One-time password','SMS')
on conflict(event_type) do update set
    description=excluded.description,
    default_channels=excluded.default_channels,
    active=true;

insert into permissions(code, name) values
('notification.read','Read notification history'),
('notification.manage','Manage notification delivery'),
('notification.device.manage','Manage notification devices'),
('notification.preference.manage','Manage notification preferences')
on conflict(code) do nothing;

insert into role_permissions(role_id, permission_id)
select r.id, p.id from roles r cross join permissions p
where r.code in ('super_admin','admin')
  and p.code in ('notification.read','notification.manage','notification.device.manage','notification.preference.manage')
on conflict do nothing;

insert into role_permissions(role_id, permission_id)
select r.id, p.id from roles r cross join permissions p
where r.code in ('customer','partner','station_manager')
  and p.code in ('notification.read','notification.device.manage','notification.preference.manage')
on conflict do nothing;

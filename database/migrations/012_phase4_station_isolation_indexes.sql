-- Phase 4 hardening: station/partner isolation indexes
create index if not exists ix_user_station_assignments_active_station_user
    on user_station_assignments(station_code, user_id)
    where active = true;
create index if not exists ix_partner_station_assignments_active_station_partner
    on partner_station_assignments(station_id, partner_id)
    where is_active = true;
create unique index if not exists ux_user_one_active_station
    on user_station_assignments(user_id)
    where active = true;

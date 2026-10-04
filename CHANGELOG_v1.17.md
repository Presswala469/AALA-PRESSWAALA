# AALA PRESSWAALA Backend v1.17 — Station Schema Alignment

## Purpose
Align partner/station authorization code with the verified live Supabase schema.

## Verified live schema
- `stations.id` = UUID
- `stations.station_code` = varchar
- `partners.id` = UUID
- `partners.user_id` = UUID
- `partners.status` = varchar
- `partner_station_assignments.partner_id` = UUID
- `partner_station_assignments.station_id` = UUID
- `partner_station_assignments.is_active` = boolean
- `user_station_assignments.station_code` = varchar
- `user_station_assignments.active` = boolean

## Changes
- Partner identity resolution now returns `partners.id`.
- Partner create/list/get/assignment DB paths use live UUID partner identity.
- Partner station authorization joins `partner_station_assignments.station_id` to `stations.id`.
- Removed backend dependence on non-existent live columns `partners.partner_id`, `partners.active`, `partner_station_assignments.station_code`, and `partner_station_assignments.active`.
- Existing in-memory/test compatibility retained.
- No new Supabase migration is required for v1.17 because the required 012 indexes are already applied.

## Verification
- Full regression suite: 50 passed.
- FastAPI import: OK; 89 routes; Python compile: OK.
- `.env` is not included or modified.

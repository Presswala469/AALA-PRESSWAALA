# AALA PRESSWAALA Backend v1.16 — Station Isolation Hardened

- Enforced Station Manager access against `user_station_assignments` at API/data layer.
- Enforced Partner station assignment against `partner_station_assignments`.
- Partner station actions now use server-side partner identity plus station assignment.
- Station Manager order receipt/history reads resolve and validate the order's station.
- Evidence actor is derived from authenticated claims instead of trusting caller input.
- Added migration `012_station_isolation_hardening.sql`.
- Added station isolation regression tests.

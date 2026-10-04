# AALA PRESSWAALA Backend v1.14 — Delivery Hardening

## Included
- Station assignment migration `009_station_user_assignments.sql`.
- Persistent delivery-code storage using SHA-256 hashes; plaintext code is not stored in PostgreSQL.
- Active delivery code is invalidated after successful delivery.
- Delivery event persistence for standard and manual delivery.
- Standard delivery API requires receiver name and GPS coordinates.
- Manual delivery API requires reason, receiver details, evidence URL and GPS coordinates.
- Manual delivery changes the order to `DELIVERED` with an auditable manual-delivery event.
- Hanger `pending_since` tracking and RED alert calculation after more than 30 days pending.
- Existing test suite retained and extended.

## Verification
- `pytest -q` → 42 passed.
- Python compile/import verification passed.
- `.env` was not included or modified.

## Supabase
Run migration `010_phase5_delivery_hardening.sql` in Supabase SQL Editor after the already-applied `009_station_user_assignments.sql`.

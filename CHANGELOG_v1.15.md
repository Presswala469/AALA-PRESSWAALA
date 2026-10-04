# AALA PRESSWAALA Backend v1.15 — Partner Identity Binding

## Final hardening added
- Added `011_partner_identity_binding.sql`.
- Added server-side `partners.user_id` binding.
- Existing partner records are linked to matching users by mobile number when migration runs.
- Partner role is added to linked user accounts.
- Partner OTP login now preserves the highest existing operational role instead of always forcing `customer`.
- Partner endpoints reject caller-supplied partner IDs that do not match the authenticated partner identity.
- Delivery start/confirm/exception operations now enforce authenticated partner identity.
- Delivery job/code reads enforce object-level assignment for partner sessions.
- Partner list is self-scoped for partner sessions.
- Partner assignment lookup is identity-scoped.

## Verification
- 44 tests passed.
- FastAPI import passed.
- 89 routes.
- `.env` was not included or modified.

## Supabase
After v1.14 / migration 010, run:
`database/migrations/011_partner_identity_binding.sql`

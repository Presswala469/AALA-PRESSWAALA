# AALA PRESSWAALA — FINAL BACKEND RELEASE

Release: v1.14 Final Hardened

This package uses the v1.14 Delivery Hardened implementation as the authoritative backend codebase, while retaining the v1.12 project documentation and environment example for completeness.

## Included
- Complete backend application
- Existing Phase 0–7 migrations
- 009_station_user_assignments.sql
- 010_phase5_delivery_hardening.sql
- Delivery code persistence using SHA-256 hash
- Single-use delivery code invalidation after successful delivery
- Standard delivery receiver + GPS capture
- Evidence-based manual delivery exception
- Delivery event persistence/audit trail
- Hanger pending_since tracking and >30 day RED alert logic
- Full existing test suite plus delivery hardening tests
- Project README, rules, completion report, and .env.example

## Verification
- Pytest: 42 passed
- FastAPI import: verified
- Routes: 89
- No real .env file included or modified

## Supabase
Apply migrations in sequence. If 009 has already been applied, apply 010 next.

# AALA PRESSWAALA Backend v1.18.0

## Phase 1–5 Final Backend Closure
- Customer object-level authorization and user binding
- Order customer/address/booking snapshot fields
- Reorder API
- Configurable TAT rules
- Station support request lifecycle
- Post-delivery rating API
- Delivery code expiry with configurable TTL
- Live Supabase station/partner schema alignment retained
- Regression/security tests expanded to 56 passing tests

Migration added:
- `database/migrations/013_phase1_5_completion.sql`

Security:
- `.env` and environment secrets are excluded from this release.

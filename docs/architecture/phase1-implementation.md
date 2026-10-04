# AALA PRESSWAALA — Phase 1 Implementation

## Scope implemented in this development step
1. Customer OTP request/verification API boundary.
2. JWT session foundation with role claim.
3. Server-side role authorization dependency.
4. Runtime public company/branding configuration API.
5. Admin/Super Admin company-settings API boundary.
6. Customer creation with permanent Global Customer Number.
7. Customer address create/list API with one-current-address rule.
8. Phase 0/1 PostgreSQL/Supabase migration baseline retained.
9. Automated tests for health, readiness, OTP, company config, customer numbering and address current-state behavior.

## Important implementation status
The API/module boundaries are now coded and tested. The repository layer is still intentionally isolated from the production database connection so the next database wiring step can be completed against the client's actual Supabase environment without rewriting routers/services.

The development OTP is fixed to `123456` and MUST NOT be used in production. It exists only for local integration testing until the approved SMS/OTP provider credentials are connected.

## Next development gate
Connect the repository boundaries to Supabase/PostgreSQL, persist sessions, add audit-log writes, then build the Admin Company & Legal Profile UI and Customer Flutter auth/profile/address screens.

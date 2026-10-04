# Phase 7 — Admin, Inventory, RBAC and Audit

## Scope
- Admin inventory control for bags/boxes with lifecycle statuses from FSD: Available, Issued, At Station, In Transit, Returned, Lost, Damaged, Under Repair, Replacement.
- Holder/location and issue/return/exception evidence are persisted as movements.
- Backend permission boundaries for inventory and audit; RBAC remains enforced server-side rather than by UI hiding.
- Audit log read boundary for administrative review.
- Business settings persistence boundary for configurable operational values.

## Rule
Inventory exceptions (Lost/Damaged/Under Repair/Replacement) require remarks. Evidence URL is supported where applicable.

## Integration note
No third-party provider is required for this phase. The module is ready to connect to real Supabase/Postgres when the client environment is supplied.

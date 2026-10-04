# AALA PRESSWAALA — PROJECT RULES

## Rule 1 — One permanent structure
The repository structure is frozen. Do not create duplicate files with alternate names for the same responsibility.

## Rule 2 — Source hierarchy
FSD v2.5 controls scope. Internal Master Development Plan controls execution. API contract controls integration. Database schema controls persistence.

## Rule 3 — Production first
No fake/static workflows. Every approved workflow must connect UI → API → database → permissions → audit/events → tests.

## Rule 4 — Module convention
Every backend business module uses exactly:
- `router.py` — HTTP/API layer
- `schemas.py` — request/response contracts
- `service.py` — business logic
- `repository.py` — database access

Orders may additionally use `state_machine.py`.

## Rule 5 — Historical integrity
Never rewrite historical order, invoice, address, company/legal or operational facts when current configuration changes.

## Rule 6 — RBAC
Permissions are enforced in backend/data access, not only by hiding UI controls.

## Rule 7 — Status integrity
Do not add `Ironing Started`. Station flow is `Received → Ready for Delivery`; exceptions are `On Hold` and `Rejected`.

## Rule 8 — Change control
After a file/module is tested and frozen, changes require a documented reason and regression test.

## Rule 9 — Definition of done
A module is Done only when requirements, DB, API, UI, permissions, audit/events, notifications, evidence storage, error states, tests and UAT criteria are covered.

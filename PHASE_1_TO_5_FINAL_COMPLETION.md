# AALA PRESSWAALA — Phase 1–5 Backend Final Completion

## Release
- Backend release: v1.18.0
- Scope: Phase 1 through Phase 5 backend/data/API/security completion package
- Previous baseline: v1.17 Station Schema Aligned

## Completion gates closed

### Phase 1 — Identity, Customer, Address & White-Label Foundation
- OTP request/verification and session validation
- User/session/revocation checks
- Customer ID + permanent global customer number
- Customer ↔ authenticated user binding support
- Customer object-level access control
- Address create/list with current-address enforcement
- Address history snapshots
- Company/legal runtime configuration and versioned company documents foundation
- Backend RBAC and station-assignment foundation

### Phase 2 — Customer Booking & Order Engine
- Services/catalog/garment categories/pricing
- Pickup slots
- Quote calculation and offer application
- Order creation and state machine
- Order events/audit trail
- Booking/customer/address snapshot support
- Reorder endpoint
- UPI/CARD/COD payment foundation
- Configurable TAT rule support

### Phase 3 — Partner / Picker Pickup Engine
- Partner identity binding to authenticated user
- Station assignment using live `partners.id` / `stations.id` UUID schema
- Pickup assignment
- Partner arrival GPS/time
- Garment quantity verification
- Shortage/customer confirmation rule
- Damage evidence
- Bag linkage
- Pickup completion
- Object-level partner authorization

### Phase 4 — Iron Station Control
- Station-specific access
- Partner station isolation
- Station Manager station isolation
- Station arrival GPS/time
- Separate partner handover vs station received quantities
- Discrepancy reason/remarks requirement
- Received / Ready for Delivery / On Hold / Rejected states
- Evidence/audit records
- Station support request lifecycle
- Configurable TAT rule support

### Phase 5 — Delivery, Delivery Code & Hangers
- Ready-for-delivery assignment
- Single-use 6-digit delivery code
- Persistent SHA-256 hash in DB
- Configurable code expiry
- Standard delivery receiver + GPS
- Manual delivery evidence exception
- Delivery event persistence
- Successful delivery invalidates code
- Hanger issued/returned/pending
- Hanger pending >30 days RED alert
- Post-delivery customer rating (1–5, one rating/order)

## Database migration
Run after the already-applied 009–012 migrations:
- `013_phase1_5_completion.sql`

This migration is additive and aligns with the verified live Supabase schema. It adds customer identity binding support, order snapshots/TAT fields, configurable TAT rules, station support requests, ratings, and delivery-code expiry.

## Verification
- Full automated test suite: **56 passed**
- Python compile: **PASS**
- FastAPI import: **PASS**
- API route registration: **PASS**
- `.env`: excluded from release ZIP

## Important scope note
This package closes the **backend/data/API/security implementation gates for Phases 1–5**. The Master Development Plan defines overall phase completion as UI + API + DB + permissions + audit + error/loading states + tests + UAT evidence. The Flutter Customer/Partner/Station applications and Web Admin integration/UAT are separate deliverables and are not contained in this backend-only ZIP.

Additional Phase 1 controls included in v1.18:
- Customer alternate mobile/photo fields
- Zone master + user-zone assignments
- Seeded permission vocabulary and role-permission mappings

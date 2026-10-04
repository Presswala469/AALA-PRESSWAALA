# Phase 3 — Partner / Picker + Station Handover Foundation

## Scope
Implements the operational pickup boundary from the FSD: partner/station assignment, pickup job assignment, partner arrival evidence, garment quantity verification, customer confirmation, damage evidence, bag assignment, pickup completion and partner-to-station handover. Station receiving preserves both partner handover quantity and station received quantity.

## Operational sequence
1. Booking confirmed
2. Pickup job assigned to partner
3. Partner starts pickup (`PICKUP`)
4. Partner records arrival GPS/time
5. Garment quantity is verified
6. Optional visible-damage evidence is attached
7. Bag/box is assigned
8. Pickup is completed
9. Order moves to `IRON_STATION`
10. Station receives and records both quantities

## Fixed status terminology
The order state machine continues to use `BOOKING_CONFIRMED → PICKUP → IRON_STATION → RECEIVED → READY_FOR_DELIVERY → OUT_FOR_DELIVERY → DELIVERED`. The station module does not introduce an `IRONING_STARTED` status.

## Discrepancy rule
If partner handover quantity differs from station received quantity, a reason is mandatory. Both quantities remain separate records for audit and dispute handling.

## Future production integration
The current development fallback stores operational records in memory when DATABASE_URL is empty. PostgreSQL tables are included in migration `004_phase3_partner_station.sql`. Production wiring must use the same repository/service contracts, S3 for evidence URLs, authenticated partner/station identities, and immutable audit/security records.

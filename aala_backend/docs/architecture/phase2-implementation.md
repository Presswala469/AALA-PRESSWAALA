# AALA PRESSWAALA — Phase 2 Implementation

Phase 2 establishes the real booking engine boundary: service catalogue, garment catalogue, configurable pricing, pickup slots, order creation, permanent Order ID and auditable order state transitions.

## FSD-aligned booking sequence
Service → Address → Pickup Slot → Garment Details → Estimated Amount → Offer → Payment → Confirm Booking → Order Number.

## Implemented
- Standard, Overnight Express and 2-hour Express service types.
- Garment categories including small-garment flag.
- Station-aware pricing lookup boundary.
- Pickup slot configuration.
- Quote engine with line-level quantities and totals.
- Permanent Order ID format `ORD-YYYYMMDD-XXXXXXXX`.
- Order event history in addition to current status.
- State machine aligned to FSD operational statuses: Booking Confirmed → Pickup → Iron Station → Received → Ready for Delivery → Out for Delivery → Delivered.
- On Hold / Rejected / Cancelled paths are represented where applicable.
- Offer calculation is intentionally not guessed; it remains a separate integration boundary.

## Important implementation rule
The current price quote is an estimate based on booking quantities. Pickup/station quantity verification must later create the operational discrepancy/finalization flow; it must not rewrite the historical booking quote silently.

## Next dependency
Phase 3: Partner/Picker pickup operations, garment verification, discrepancy handling, bag assignment and handover evidence.

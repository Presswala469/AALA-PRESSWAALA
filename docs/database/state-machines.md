# State Machines — Frozen Baseline

## Customer order lifecycle
Booking Confirmed → Pickup → Iron Station → Received → Ready for Delivery → Out for Delivery → Delivered

Operational exceptions/cancellation paths are recorded as events and constrained by business rules. Never overwrite history.

## Iron Station
Received → Ready for Delivery
Exceptions: On Hold, Rejected

## Delivery
System-generated single-use delivery code. Successful delivery invalidates the code. Manual delivery is an evidence-based exception with reason/receiver/evidence.

## Complaint CRM
New → Assigned → Under Investigation → Action Required → Resolved → Closed; Rejected where applicable.

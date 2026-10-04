# Phase 6B — Production Notification Engine

## Scope closed in this release

This release implements the Phase 6 notification foundation as a backend workflow, not just a queue table.

### Channels
- `IN_APP`
- `PUSH` via Firebase Cloud Messaging (FCM)
- `SMS` provider-ready
- `WHATSAPP` transactional/UAT-ready
- `EMAIL` provider-ready

FCM remains the primary push channel. The backend stores device registrations and keeps provider credentials outside source control. Firebase recommends server-side token/installation management and proactive stale-registration cleanup.

### Event layer
Supported workflow events:
`REGISTRATION`, `BOOKING`, `ASSIGNMENT`, `ARRIVAL_PICKUP`, `STATION_RECEIPT`,
`STATUS`, `READY`, `OUT_FOR_DELIVERY`, `DELIVERED`, `INVOICE`, `OFFERS`,
`DELAY`, `SERVICE_AVAILABILITY`, `COMPLAINT`, `OTP`.

Order creation/status transitions are wired to the notification event dispatcher. Notification failure does not block the order workflow.

### Delivery hardening
- idempotency key per event/channel
- device token registration and re-registration
- optional Firebase Installation ID, device ID and app version
- customer/device ownership enforcement
- notification recipient isolation
- per-user channel preferences
- auditable delivery attempts
- token hash in attempt history rather than raw token
- permanent FCM token failures deactivate the device
- provider message ID, sent/read timestamps and failure details
- admin-triggered provider send endpoint
- status/read lifecycle
- FCM dependency included in requirements

### Security
- customer/partner/station-manager device registration is bound to the authenticated user
- customer/partner/station-manager can read or modify only their own notification records/preferences
- admin can operate on other recipients
- device and notification changes create audit records when database mode is active

### Provider boundary
The provider adapter deliberately does not put Firebase credentials in Git. Configure the deployment environment with `FIREBASE_SERVICE_ACCOUNT_JSON` pointing to the service-account JSON file. FCM send requests are made from the trusted server environment.

SMS, WhatsApp and email remain provider adapters until the client supplies provider credentials/contracts. They are not falsely reported as live.

### Operational note
FCM acceptance (`SENT`) is not the same as device delivery. Firebase generates a message ID after accepting the send request; delivery/received telemetry is a separate concern.

A scheduler/worker can safely retry failed notifications using the persisted attempt history and idempotent notification record. The current API intentionally keeps provider sending behind the authenticated admin send action rather than silently claiming a background worker exists.

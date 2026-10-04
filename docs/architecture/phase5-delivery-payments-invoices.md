# Phase 5 — Delivery, Payments and Invoices

## Scope
This phase adds the backend contracts and persistence boundaries for:
- delivery assignment and delivery partner execution;
- automatic six-digit delivery code generation and invalidation after successful delivery;
- manual delivery exceptions with reason/evidence;
- payment lifecycle with a provider adapter boundary;
- COD handling;
- invoice issuance with a company/legal snapshot.

## External-account strategy
Client-owned third-party accounts are intentionally deferred. The payment layer uses an explicit development provider adapter (`MockPaymentProvider`) only so business workflows and tests can run without credentials. It is **not** a production payment integration.

When the client supplies Razorpay test credentials, a Razorpay implementation must be added behind the existing `PaymentProvider` interface. No order/payment business logic should be rewritten.

## Delivery flow
`READY_FOR_DELIVERY -> OUT_FOR_DELIVERY -> DELIVERED`

A delivery assignment is required before delivery start. Starting delivery generates a delivery code. Successful delivery verifies the code and immediately invalidates it. A manual delivery exception records reason, receiver information/evidence when available, and remarks.

## Payment flow
For UPI/Card, the provider adapter creates a provider order and later verifies the provider payment. Payment records retain provider identifiers and status. COD is represented separately as a pending collection boundary.

## Invoice integrity
Invoice generation snapshots the current company/legal profile into the invoice row. Future company-profile changes therefore do not rewrite historical invoice details.

## Definition of done for this phase
- DB migration created.
- API routes registered.
- Business rules implemented in service/repository layers.
- Development provider boundary documented.
- Regression tests cover delivery code, invalid code, payment verification, COD and invoice snapshot.
- Real Razorpay/Maps/FCM/S3 credentials remain an explicit later integration gate.

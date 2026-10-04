# Phase 8 — Reports & MIS

## Scope
Implements an admin-only, export-ready reporting data layer covering the FSD report matrix without creating a second source of truth.

## Report types
- revenue
- orders
- customers
- partners
- stations
- garments
- hangers
- bags_boxes
- offers
- complaints
- customer_locations
- customer_history

## Common filters
Date range, station, partner, customer, status, service, city, offer, inventory item type, complaint category, and bounded row limit where applicable.

## Rules
- Reports are read-only projections over operational tables.
- No report-specific duplicate business records are created.
- CSV export uses the same query path as the report endpoint.
- Historical customer address/order data remains reportable; current address is separate from address history.
- Stable IDs are exposed wherever the source table provides them.
- Backend RBAC is required for report access.

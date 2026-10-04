# Module Map — Frozen v1.0

## Applications
- `customer_app`: Customer mobile app, Android + iOS.
- `operations_app`: Single Flutter app with Partner/Picker and Iron Station modes, Android + iOS.
- `admin_panel`: React/Vite web admin.

## Backend modules
`auth`, `users`, `customers`, `addresses`, `company`, `stations`, `partners`, `services_catalog`, `pricing`, `orders`, `garments`, `pickup`, `station_operations`, `delivery`, `payments`, `invoices`, `offers`, `complaints`, `inventory`, `hangers`, `notifications`, `reports`, `audit`.

## Core dependency order
FSD → Architecture → Database Schema → API Contract → Module Design → File Responsibility → Code → Tests → Freeze.

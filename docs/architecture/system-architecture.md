# System Architecture

Flutter Customer + Flutter Operations (Partner/Picker + Station) + React/Vite Admin → FastAPI/Python → Supabase/PostgreSQL.

Integrations: AWS S3 for evidence/documents/invoices, Firebase FCM for push, Razorpay for payments, Google Maps for location/navigation, channel-independent notification layer with WhatsApp readiness.

White-label/runtime company configuration is data-driven. Company/legal/branding changes are audited; issued invoices preserve historical snapshots.

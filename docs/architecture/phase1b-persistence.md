# Phase 1B — Persistent Identity & Configuration

Implemented boundaries:
- PostgreSQL/Supabase customer persistence.
- PostgreSQL/Supabase address persistence.
- Current-address uniqueness at database level.
- Address-history table.
- OTP verification creates/updates a user and customer role mapping.
- Session record creation and logout/revocation boundary.
- Company profile persistence with version increment.
- Public company configuration remains runtime-driven.
- Development fallback remains available when DATABASE_URL is empty so automated tests can run without external credentials.

Production dependency:
- Set DATABASE_URL / Supabase credentials before production deployment.
- Replace development OTP with approved SMS/OTP provider.
- Add S3 document upload and persistent audit repository in the next integration increment.

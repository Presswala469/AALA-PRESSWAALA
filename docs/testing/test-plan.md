# Master Test Plan

Unit: pricing, offers, customer ID, TAT, complaint window, cancellation fee, delivery code, hanger threshold, permissions.

Integration: order lifecycle, payment callbacks, notifications, S3 evidence, maps, OTP, WhatsApp UAT readiness.

E2E: booking → pickup → station arrival/receipt → discrepancy/no discrepancy → ready → delivery code → delivered → invoice → complaint/rating.

Negative: duplicate payment callback; expired/wrong delivery code; shortage without confirmation; station overwrite; cross-station access; unauthorised company/GST edit; manual delivery without evidence; complaint after 24h; hanger count 30 vs 31.

Security: API authorization, object-level access, station isolation, signed file URLs, session revocation, audit integrity.

from __future__ import annotations
from dataclasses import dataclass
import os

@dataclass
class DeliveryResult:
    success: bool
    provider: str
    message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False
    permanent_token_failure: bool = False

def send_push(token: str, title: str, body: str, data: dict) -> DeliveryResult:
    credential_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not credential_path:
        return DeliveryResult(False, "FCM", error_code="PROVIDER_NOT_CONFIGURED",
                              error_message="Firebase service account is not configured")
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(credential_path))
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={str(k): str(v) for k, v in (data or {}).items()},
            token=token,
        )
        mid = messaging.send(message)
        return DeliveryResult(True, "FCM", message_id=mid)
    except Exception as exc:
        name = exc.__class__.__name__
        text = str(exc)[:500]
        permanent = name in {"UnregisteredError", "SenderIdMismatchError"}
        retryable = not permanent and name not in {"InvalidArgumentError"}
        return DeliveryResult(False, "FCM", error_code=name or "PROVIDER_ERROR",
                              error_message=text, retryable=retryable,
                              permanent_token_failure=permanent)

def send(channel: str, token: str | None, title: str, body: str, data: dict) -> DeliveryResult:
    if channel == "PUSH":
        if not token:
            return DeliveryResult(False, "FCM", error_code="NO_DEVICE_TOKEN",
                                  error_message="No active device token available")
        return send_push(token, title, body, data)
    provider = {"SMS":"SMS", "WHATSAPP":"WHATSAPP", "EMAIL":"EMAIL", "IN_APP":"IN_APP"}.get(channel, channel)
    return DeliveryResult(False, provider, error_code="PROVIDER_NOT_CONFIGURED",
                          error_message=f"{channel} provider is not configured")

from abc import ABC, abstractmethod
from uuid import uuid4
import hashlib
import hmac
import httpx
from app.core.config import settings

class PaymentProvider(ABC):
    @abstractmethod
    def create_order(self, *, order_id: str, amount: float, currency: str, receipt: str) -> dict: ...
    @abstractmethod
    def verify(self, *, provider_order_id: str, provider_payment_id: str, signature: str | None = None) -> dict: ...

class MockPaymentProvider(PaymentProvider):
    def create_order(self, *, order_id, amount, currency, receipt):
        return {"provider":"mock","provider_order_id":f"mock_ord_{uuid4().hex[:16]}","order_id":order_id,"amount":float(amount),"currency":currency,"receipt":receipt,"status":"created"}
    def verify(self, *, provider_order_id, provider_payment_id, signature=None):
        return {"provider":"mock","provider_order_id":provider_order_id,"provider_payment_id":provider_payment_id,"verified":True}

class RazorpayProvider(PaymentProvider):
    base_url = "https://api.razorpay.com/v1"
    def _auth(self):
        if not settings.razorpay_key_id or not settings.razorpay_key_secret:
            raise RuntimeError("Razorpay credentials are not configured")
        return (settings.razorpay_key_id, settings.razorpay_key_secret)
    def create_order(self, *, order_id, amount, currency, receipt):
        payload={"amount":int(round(float(amount)*100)),"currency":currency,"receipt":receipt,"notes":{"order_id":order_id}}
        with httpx.Client(timeout=15) as client:
            r=client.post(f"{self.base_url}/orders",auth=self._auth(),json=payload)
            r.raise_for_status()
            data=r.json()
        return {"provider":"razorpay","provider_order_id":data["id"],"order_id":order_id,"amount":amount,"currency":currency,"receipt":receipt,"status":data["status"]}
    def verify(self, *, provider_order_id, provider_payment_id, signature=None):
        if not signature: raise ValueError("Razorpay signature is required")
        message=f"{provider_order_id}|{provider_payment_id}".encode()
        expected=hmac.new(settings.razorpay_key_secret.encode(),message,hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,signature):
            return {"provider":"razorpay","provider_order_id":provider_order_id,"provider_payment_id":provider_payment_id,"verified":False}
        return {"provider":"razorpay","provider_order_id":provider_order_id,"provider_payment_id":provider_payment_id,"verified":True}

def get_payment_provider():
    if settings.razorpay_key_id and settings.razorpay_key_secret:
        return RazorpayProvider()
    return MockPaymentProvider()

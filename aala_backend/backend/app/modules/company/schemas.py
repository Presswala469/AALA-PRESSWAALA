from pydantic import BaseModel, EmailStr, Field

class CompanyPublic(BaseModel):
    legal_name: str
    display_name: str
    logo_url: str | None = None
    registered_address: str | None = None
    service_address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    gstin: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    support_phone: str | None = None
    support_email: EmailStr | None = None
    invoice_prefix: str | None = None
    invoice_terms: str | None = None
    invoice_footer: str | None = None
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    terms_url: str | None = None
    privacy_url: str | None = None
    refund_policy_url: str | None = None
    cancellation_policy_url: str | None = None

class CompanyUpdate(BaseModel):
    legal_name: str = Field(min_length=1, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    logo_url: str | None = None
    registered_address: str | None = None
    service_address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    gstin: str | None = None
    pan: str | None = None
    cin: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    support_phone: str | None = None
    support_email: EmailStr | None = None
    invoice_prefix: str | None = None
    invoice_terms: str | None = None
    invoice_footer: str | None = None
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    terms_url: str | None = None
    privacy_url: str | None = None
    refund_policy_url: str | None = None
    cancellation_policy_url: str | None = None

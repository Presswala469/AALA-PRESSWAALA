from pydantic import BaseModel, Field

class OTPRequest(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=20)

class OTPVerifyRequest(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=20)
    otp: str = Field(min_length=4, max_length=8)
    device_id: str | None = None
    platform: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    session_id: str
    token_type: str = "bearer"

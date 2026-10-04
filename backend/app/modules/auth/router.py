from fastapi import APIRouter, Depends, HTTPException
from app.core.permissions import current_claims
from app.modules.auth.schemas import OTPRequest, OTPVerifyRequest, TokenResponse
from app.modules.auth.service import request_otp, verify_otp, revoke_session

router = APIRouter()

@router.post("/otp/request")
def otp_request(payload: OTPRequest):
    return request_otp(payload.mobile_number)

@router.post("/otp/verify", response_model=TokenResponse)
def otp_verify(payload: OTPVerifyRequest):
    try:
        return verify_otp(payload.mobile_number, payload.otp, payload.device_id, payload.platform)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

@router.post("/logout")
def logout(claims=Depends(current_claims)):
    revoke_session(claims["sid"])
    return {"success": True}


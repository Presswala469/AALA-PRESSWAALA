from pydantic import BaseModel, Field
class NotificationCreate(BaseModel):
    recipient_id: str; channel: str = Field(pattern='^(IN_APP|PUSH|SMS|WHATSAPP)$'); title: str; message: str; data: dict = Field(default_factory=dict)

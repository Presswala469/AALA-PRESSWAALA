from pydantic import BaseModel, Field

CHANNEL_PATTERN = r'^(IN_APP|PUSH|SMS|WHATSAPP|EMAIL)$'
PLATFORM_PATTERN = r'^(ANDROID|IOS|WEB)$'
PRIORITY_PATTERN = r'^(NORMAL|HIGH)$'

class NotificationCreate(BaseModel):
    recipient_id: str
    channel: str = Field(pattern=CHANNEL_PATTERN)
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)
    data: dict = Field(default_factory=dict)
    event_type: str | None = Field(default=None, max_length=80)
    idempotency_key: str | None = Field(default=None, max_length=160)
    priority: str = Field(default='NORMAL', pattern=PRIORITY_PATTERN)

class NotificationEvent(BaseModel):
    recipient_id: str
    event_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)
    data: dict = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, max_length=160)
    priority: str = Field(default='NORMAL', pattern=PRIORITY_PATTERN)
    channels: list[str] | None = None

class DeviceRegister(BaseModel):
    user_id: str | None = None
    platform: str = Field(pattern=PLATFORM_PATTERN)
    token: str = Field(min_length=10, max_length=4096)
    installation_id: str | None = Field(default=None, max_length=200)
    device_id: str | None = Field(default=None, max_length=200)
    app_version: str | None = Field(default=None, max_length=50)

class PreferenceUpdate(BaseModel):
    event_type: str = Field(min_length=1, max_length=80)
    channel: str = Field(pattern=CHANNEL_PATTERN)
    enabled: bool

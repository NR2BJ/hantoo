import uuid

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: str | None = None


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    invite_code: str


class TokenResponse(BaseModel):
    message: str = "Login successful"


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    display_name: str
    role: str
    is_active: bool
    totp_enabled: bool

    model_config = {"from_attributes": True}


class Setup2FAResponse(BaseModel):
    secret: str
    otpauth_url: str


class Verify2FARequest(BaseModel):
    totp_code: str


class InviteCodeCreate(BaseModel):
    max_uses: int = 1


class InviteCodeResponse(BaseModel):
    code: str
    max_uses: int
    use_count: int

    model_config = {"from_attributes": True}

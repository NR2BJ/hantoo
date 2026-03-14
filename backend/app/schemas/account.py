import uuid

from pydantic import BaseModel, Field


class KISAccountCreate(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    account_type: str = Field(pattern="^(personal|shared)$")
    environment: str = Field(default="prod", pattern="^(prod|paper)$")
    app_key: str
    app_secret: str
    account_number: str = Field(min_length=8, max_length=20)
    product_code: str = Field(default="01", max_length=2)
    hts_id: str | None = None


class KISAccountResponse(BaseModel):
    id: uuid.UUID
    label: str
    account_type: str
    environment: str
    account_number: str
    product_code: str
    hts_id: str | None
    is_active: bool
    has_valid_token: bool = False

    model_config = {"from_attributes": True}


class KISAccountAccessGrant(BaseModel):
    user_id: uuid.UUID
    permission: str = Field(default="trade", pattern="^(view|trade)$")

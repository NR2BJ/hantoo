import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.market import StockQuote


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WatchlistRename(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WatchlistItemAdd(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    market: str = Field(pattern=r"^(KOSPI|KOSDAQ)$")


class WatchlistItemResponse(BaseModel):
    id: uuid.UUID
    symbol: str
    market: str
    added_at: datetime
    quote: StockQuote | None = None

    model_config = {"from_attributes": True}


class WatchlistResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    items: list[WatchlistItemResponse] = []

    model_config = {"from_attributes": True}

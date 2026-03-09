from pydantic import BaseModel, HttpUrl
from datetime import datetime


class SuccessResponse(BaseModel):
    success: bool = True
    data: list | dict


class LinkCreationRequest(BaseModel):
    url: str
    custom_alias: str | None = None
    expires_at: datetime | None = None


class LinkCreationResponse(BaseModel):
    short_code: str
    original_url: str
    creation_date: datetime


class ShortCodeStatsResponse(BaseModel):
    original_url: str
    creation_date: datetime
    click_count: int
    last_using: datetime | None
    expires_at: datetime | None


class DeletedShortCodesResponse(BaseModel):
    deleted: list

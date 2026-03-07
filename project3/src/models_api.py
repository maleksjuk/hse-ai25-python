from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class LinkCreationRequest(BaseModel):
    url: str
    custom_alias: str | None = None


class LinkCreationResponse(BaseModel):
    short_code: str
    original_url: str
    creation_date: datetime

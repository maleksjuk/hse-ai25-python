from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import logging
from core import core
from .models import *
from db.database import *


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/links", tags=["links"])

@router.post("/shorten", response_model=LinkCreationResponse)
def create_shorten_link(link_data: LinkCreationRequest):
    short_code = link_data.custom_alias if link_data.custom_alias else core.generate_short_code()
    data = core.add_new_link_to_db(db, link_data.url, short_code, link_data.expires_at)
    if data is None:
        raise HTTPException(403, 'Short code already exists')
    logger.info(f"Created short code '{short_code}' for original URL '{link_data.url}'")
    return LinkCreationResponse(
        short_code=short_code,
        original_url=link_data.url,
        creation_date=data['creation_date']
    )


@router.get("/search")
def search_short_code(original_url: str = Query(...)):
    short_code = core.search_short_code_by_original_url(db, original_url)
    if short_code is None:
        raise HTTPException(404, "Short code not found")
    return short_code


@router.get("/{short_code}")
def get_original_url_content(short_code: str):
    logger.info(f"Try get original URL by '{short_code}'")
    original_url = core.get_original_url_from_db(db, short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    logger.info(f"Redirect to '{original_url}'")
    return RedirectResponse(original_url)


@router.get("/{short_code}/stats")
def get_short_code_stats(short_code: str):
    stats = core.get_stats_from_db(db, short_code)
    if stats is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return ShortCodeStatsResponse(
        original_url=stats['original_url'],
        creation_date=stats['creation_date'],
        click_count=stats['click_count'],
        last_using=stats['last_using'],
        expires_at=stats['expires_at']
    )


@router.delete("/{short_code}")
def delete_short_code(short_code: str):
    core.delete_short_code_from_db(db, short_code)
    return 


@router.put("/{short_code}", response_model=LinkCreationResponse)
def update_url_by_short_code(short_code: str, link_data: LinkCreationRequest):
    data = core.update_url_in_db(db, short_code, link_data.url)
    if data is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return LinkCreationResponse(
        short_code=short_code,
        original_url=link_data.url,
        creation_date=data['creation_date']
    )
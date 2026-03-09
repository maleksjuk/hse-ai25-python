from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
import logging
from core import core
from .models import *
from db.database import *
from db.models import User, Link
from auth.users import current_active_user
from cache import invalidate_cache
from config import CACHE_EXPIRE_SECONDS
from fastapi_cache.decorator import cache


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/links", tags=["links"])


@router.post("/shorten", response_model=LinkCreationResponse)
async def create_shorten_link(
    link_data: LinkCreationRequest,
    db: DB_TYPE = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    short_code = link_data.custom_alias if link_data.custom_alias else core.generate_short_code()
    link = await core.add_new_link_to_db(
        db, link_data.url, short_code,
        link_data.expires_at, user.id if user else None)
    if link is None:
        raise HTTPException(403, 'Short code already exists')
    logger.info(f"Created short code '{short_code}' for original URL '{link_data.url}'")
    return LinkCreationResponse(
        short_code=short_code,
        original_url=link_data.url,
        creation_date=link.creation_date
    )


@router.get("/search")
async def search_short_code(
    original_url: str = Query(...),
    db: DB_TYPE = Depends(get_async_session)
):
    short_code = await core.search_short_code_by_original_url(db, original_url)
    if short_code is None:
        raise HTTPException(404, "Short code not found")
    return short_code


@router.get("/{short_code}")
@cache(expire=CACHE_EXPIRE_SECONDS)
async def get_original_url_content(
    short_code: str,
    db: DB_TYPE = Depends(get_async_session)
):
    logger.info(f"Try get original URL by '{short_code}'")
    original_url = await core.get_original_url_from_db(db, short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    logger.info(f"Redirect to '{original_url}'")
    return RedirectResponse(original_url)


@router.get("/{short_code}/stats")
async def get_short_code_stats(
    short_code: str,
    db: DB_TYPE = Depends(get_async_session)
):
    stats = await core.get_stats_from_db(db, short_code)
    if stats is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return ShortCodeStatsResponse(
        original_url=stats['original_url'],
        creation_date=stats['creation_date'],
        click_count=stats['click_count'],
        last_using=stats['last_using'],
        expires_at=stats['expires_at']
    )


@router.delete("/{short_code}", response_model=SuccessResponse)
async def delete_short_code(
    short_code: str,
    db: DB_TYPE = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    if not await core.check_user_access(db, short_code, 
                                        user.id if user else None):
        raise HTTPException(403, "Forbidden")
    await core.delete_short_code_from_db(db, short_code)
    await invalidate_cache("GET", f"/links/{short_code}")
    return SuccessResponse()


@router.put("/{short_code}", response_model=LinkCreationResponse)
async def update_url_by_short_code(
    short_code: str,
    link_data: LinkCreationRequest,
    db: DB_TYPE = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    if not await core.check_user_access(db, short_code, 
                                        user.id if user else None):
        raise HTTPException(403, "Forbidden")
    link = await core.update_url_in_db(db, short_code, link_data.url)
    if link is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    await invalidate_cache("GET", f"/links/{short_code}")
    return LinkCreationResponse(
        short_code=short_code,
        original_url=link_data.url,
        creation_date=link.creation_date
    )
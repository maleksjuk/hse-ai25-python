import string
import random
import logging
import json
from datetime import datetime, timedelta
from db import links
from db.database import DB_TYPE
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

logger = logging.getLogger(__name__)

ON_TEST_AUTODELETE = False
MAX_DAYS_AFTER_USING = 5
MAX_MINUTES_AFTER_USING = 5


def generate_short_code(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

async def short_code_exists(db: DB_TYPE, short_code: str):
    link = await links.get_active_link_by_code(db, short_code)
    return link is not None

async def check_user_access(db: DB_TYPE, short_code: str, user_id: UUID | None = None):
    link = await links.get_active_link_by_code(db, short_code)
    if link is None:
        return True
    return bool(link.user_id == user_id)



async def get_actual_link(db: DB_TYPE, short_code: str):
    return await links.get_active_link_by_code(db, short_code)

async def add_new_link_to_db(db: DB_TYPE, original_url: str, short_code: str,
                       expires_at: datetime | None = None, user_id: UUID | None = None):
    if await short_code_exists(db, short_code):
        return None
    return await links.create_link(db, short_code, original_url, expires_at, user_id)

async def get_original_url_from_db(db: DB_TYPE, short_code: str):
    link = await links.get_active_link_by_code(db, short_code)
    if link is None:
        return None
    await links.increment_click_count(db, link)
    return link.original_url

async def delete_short_code_from_db(db: DB_TYPE, short_code: str):
    link = await links.get_active_link_by_code(db, short_code)
    if link is not None:
        await links.delete_link(db, link)

async def update_url_in_db(db: DB_TYPE, short_code: str, original_url: str):
    link = await links.get_active_link_by_code(db, short_code)
    if link is None:
        return None
    await links.delete_link(db, link)
    return await add_new_link_to_db(db, original_url, short_code, link.expires_at)

async def get_stats_from_db(db: DB_TYPE, short_code: str):
    link = await links.get_active_link_by_code(db, short_code)
    if link is None:
        return None
    return {
        'short_code': link.short_code,
        'original_url': link.original_url,
        'creation_date': link.creation_date,
        'click_count': link.click_count,
        'last_using': link.last_using,
        'expires_at': link.expires_at
    }

async def search_short_code_by_original_url(db: DB_TYPE, original_url: str):
    return await links.search_by_original_url(db, original_url)

async def cleanup_unused_links(db: DB_TYPE):
    if ON_TEST_AUTODELETE:
        border_date = datetime.now() - timedelta(minutes=MAX_MINUTES_AFTER_USING)
    else:
        border_date = datetime.now() - timedelta(days=MAX_DAYS_AFTER_USING)
    
    unused_links = await links.get_unused_links(db, border_date)
    for link in unused_links:
        await links.delete_link(db, link)
    
async def get_deleted_short_codes(db: DB_TYPE):
    return await links.get_deleted_links(db)

import string
import random
import logging
import json
from datetime import datetime, timedelta
from db import links
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

DB_TYPE = Session

ON_TEST_AUTODELETE = True
MAX_DAYS_AFTER_USING = 5
MAX_MINUTES_AFTER_USING = 5


def generate_short_code(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def short_code_exists(db: DB_TYPE, short_code: str):
    link = links.get_active_link_by_code(db, short_code)
    return link is not None


def add_new_link_to_db(db: DB_TYPE, original_url: str, short_code: str,
                       expires_at: datetime | None = None):
    if short_code_exists(db, short_code):
        return None
    return links.create_link(db, short_code, original_url, expires_at)

def get_original_url_from_db(db: DB_TYPE, short_code: str):
    link = links.get_active_link_by_code(db, short_code)
    if link is None:
        return None
    links.increment_click_count(db, link)
    return link.original_url

def delete_short_code_from_db(db: DB_TYPE, short_code: str):
    link = links.get_active_link_by_code(db, short_code)
    if link is not None:
        links.delete_link(db, link)

def update_url_in_db(db: DB_TYPE, short_code: str, original_url: str):
    link = links.get_active_link_by_code(db, short_code)
    if link is None:
        return
    links.delete_link(db, link)
    return add_new_link_to_db(db, original_url, short_code, link.expires_at)

def get_stats_from_db(db: DB_TYPE, short_code: str):
    link = links.get_active_link_by_code(db, short_code)
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

def search_short_code_by_original_url(db: DB_TYPE, original_url: str):
    return links.search_by_original_url(db, original_url)

def cleanup_unused_links(db: DB_TYPE):
    if ON_TEST_AUTODELETE:
        border_date = datetime.now() - timedelta(minutes=MAX_MINUTES_AFTER_USING)
    else:
        border_date = datetime.now() - timedelta(days=MAX_DAYS_AFTER_USING)
    
    unused_links = links.get_unused_links(db, border_date)
    for link in unused_links:
        links.delete_link(db, link)
    
def get_deleted_short_codes(db: DB_TYPE):
    return links.get_deleted_links(db)

import string
import random
from datetime import datetime
import logging
import json
from datetime import datetime, timedelta
from db.database import DB_TYPE

logger = logging.getLogger(__name__)

ON_TEST_AUTODELETE = True
MAX_DAYS_AFTER_USING = 5
MAX_MINUTES_AFTER_USING = 5


def generate_short_code(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def short_code_enabled(db: DB_TYPE, short_code: str):
    if short_code not in db:
        return False
    return not db[short_code].get('is_deleted', False)


def add_new_link_to_db(db: DB_TYPE, original_url: str, short_code: str, expires_at: datetime | None = None):
    if short_code_enabled(db, short_code):
        return None
    db[short_code] = {
        'original_url': original_url,
        'creation_date': datetime.now(),
        'click_count': 0,
        'last_using': None,
        'expires_at': expires_at,
        'is_deleted': False
    }
    return db[short_code]

def get_original_url_from_db(db: DB_TYPE, short_code: str):
    if not short_code_enabled(db, short_code):
        return None
    data = db[short_code]
    data['click_count'] += 1
    data['last_using'] = datetime.now()
    return data['original_url']

def delete_short_code_from_db(db: DB_TYPE, short_code: str):
    # db.pop(short_code, None)
    if short_code_enabled(db, short_code):
        db[short_code]['is_deleted'] = True

def update_url_in_db(db: DB_TYPE, short_code: str, original_url: str):
    if short_code not in db:
        return
    delete_short_code_from_db(db, short_code)
    return add_new_link_to_db(db, original_url, short_code)

def get_stats_from_db(db: DB_TYPE, short_code: str):
    return db.get(short_code, None)

def search_short_code_by_original_url(db: DB_TYPE, original_url: str):
    short_code = None
    for code, stats in db.items():
        if stats['original_url'] == original_url:
            short_code = code
            break
    return short_code

def cleanup_unused_links(db: DB_TYPE):
    if ON_TEST_AUTODELETE:
        border_date = datetime.now() - timedelta(minutes=MAX_MINUTES_AFTER_USING)
    else:
        border_date = datetime.now() - timedelta(days=MAX_DAYS_AFTER_USING)
    for code, stats in db.items():
        if stats.get('is_deleted', False):
            continue
        last_using = stats['last_using']
        if last_using is None:
            last_using = stats['creation_date']
        if last_using < border_date:
            delete_short_code_from_db(db, code)
            logger.info(f"Remove unused link: {code}")
        
def get_deleted_short_codes(db: DB_TYPE):
    deleted = {}
    for code, stats in db.items():
        if stats.get('is_deleted', False):
            deleted[code] = stats
    return deleted

import string
import random
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

def generate_short_code(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def add_new_link_to_db(db: dict, original_url: str, short_code: str):
    db[short_code] = {
        'original_url': original_url,
        'creation_date': datetime.now(),
        'click_count': 0,
        'last_using': None
    }
    return db[short_code]

def get_original_url_from_db(db: dict, short_code: str):
    if short_code not in db:
        return None
    data = db[short_code]
    data['click_count'] += 1
    data['last_using'] = datetime.now()
    return data['original_url']

def delete_short_code_from_db(db: dict, short_code: str):
    db.pop(short_code, None)

def update_url_in_db(db: dict, short_code: str, original_url: str):
    if short_code not in db:
        return
    delete_short_code_from_db(db, short_code)
    return add_new_link_to_db(db, original_url, short_code)


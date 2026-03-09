import asyncio
from core import core
from db.database import *
import logging
from fastapi import APIRouter, Depends
from .models import *


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/links", tags=["links"])


async def cleanup_unused_links():
    while True:
        try:
            if core.ON_TEST_AUTODELETE:
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(1 * 60 * 60)
            core.cleanup_unused_links(Depends(get_session))
        except asyncio.CancelledError:
            break


@router.get("/deleted", response_model=DeletedShortCodesResponse)
def get_deleted_short_codes(
    db: Session = Depends(get_session)
):
    deleted = core.get_deleted_short_codes(db)
    deleted_list = []
    for link in deleted:
        deleted_list.append({
        'short_code': link.short_code,
        'original_url': link.original_url,
        'creation_date': link.creation_date,
        'click_count': link.click_count,
        'last_using': link.last_using,
        'expires_at': link.expires_at
    })
    return DeletedShortCodesResponse(deleted=deleted_list)


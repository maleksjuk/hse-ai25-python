import asyncio
from core import core
from db.database import *
import logging
from fastapi import APIRouter
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
            core.cleanup_unused_links(db)
        except asyncio.CancelledError:
            break


@router.get("/deleted", response_model=DeletedShortCodesResponse)
def get_deleted_short_codes():
    deleted = core.get_deleted_short_codes(db)
    return DeletedShortCodesResponse(deleted=deleted)


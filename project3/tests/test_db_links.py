import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select
from src.db.models import Link
from src.db import links as db_links


VALID_URL = "http://valid.url"
NOT_EXIST_URL = "http://not.exist.url"
BASE_SHORT_CODE = "SHoRtCoDe"


@pytest.mark.asyncio
async def test_create_link(async_session):
    user_id = uuid4()
    
    link = await db_links.create_link(async_session, BASE_SHORT_CODE, VALID_URL, user_id=user_id)
    
    assert link.short_code == BASE_SHORT_CODE
    assert link.original_url == VALID_URL
    assert link.user_id == user_id
    assert link.click_count == 0
    assert link.is_deleted is False
    
    result = await async_session.execute(select(Link).where(Link.short_code == BASE_SHORT_CODE))
    db_link = result.scalar_one()
    assert db_link.id == link.id


@pytest.mark.asyncio
async def test_get_active_link_by_code(async_session):
    link = await db_links.create_link(async_session, BASE_SHORT_CODE, VALID_URL)
    
    found_link = await db_links.get_active_link_by_code(async_session, BASE_SHORT_CODE)
    assert found_link is not None
    assert found_link.id == link.id
    
    link.is_deleted = True
    await async_session.commit()
    not_found = await db_links.get_active_link_by_code(async_session, BASE_SHORT_CODE)
    assert not_found is None


@pytest.mark.asyncio
async def test_increment_click_count(async_session):
    link = await db_links.create_link(async_session, BASE_SHORT_CODE, VALID_URL)
    assert link.click_count == 0
    assert link.last_using is None
    
    await db_links.increment_click_count(async_session, link)
    
    assert link.click_count == 1
    assert link.last_using is not None


@pytest.mark.asyncio
async def test_delete_link(async_session):
    link = await db_links.create_link(async_session, BASE_SHORT_CODE, VALID_URL)
    assert link.is_deleted == False
    
    await db_links.delete_link(async_session, link)
    assert link.is_deleted == True


@pytest.mark.asyncio
async def test_search_by_original_url(async_session):
    link1 = await db_links.create_link(async_session, "search1", VALID_URL)
    link2 = await db_links.create_link(async_session, "search2", VALID_URL)
    link3 = await db_links.create_link(async_session, "search3", VALID_URL)
    link3.is_deleted = True
    await async_session.commit()
    
    results = await db_links.search_by_original_url(async_session, VALID_URL)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_get_unused_links(async_session):
    now = datetime.now()
    
    created = await db_links.create_link(async_session, "created", "http://url1")
    
    unused = await db_links.create_link(async_session, "unused", "http://url2")
    unused.last_using = now - timedelta(days=10)
    
    used = await db_links.create_link(async_session, "used", "http://url3")
    used.last_using = now - timedelta(days=1)
    
    await async_session.commit()
    
    border_date = now - timedelta(days=5)
    unused_links = await db_links.get_unused_links(async_session, border_date)
    
    short_codes = [link.short_code for link in unused_links]
    assert "created" not in short_codes
    assert "unused" in short_codes
    assert "used1" not in short_codes


@pytest.mark.asyncio
async def test_get_deleted_links(async_session):
    await db_links.create_link(async_session, "active1", "http://active1.com")
    await db_links.create_link(async_session, "active2", "http://active2.com")
    deleted1 = await db_links.create_link(async_session, "del1", "http://deleted1.com")
    deleted2 = await db_links.create_link(async_session, "del2", "http://deleted2.com")
    
    await db_links.delete_link(async_session, deleted1)
    await db_links.delete_link(async_session, deleted2)
    await async_session.commit()
    
    deleted_links = await db_links.get_deleted_links(async_session)
    assert len(deleted_links) == 2
    short_codes = [link.short_code for link in deleted_links]
    assert "del1" in short_codes
    assert "del2" in short_codes

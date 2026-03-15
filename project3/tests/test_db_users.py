import pytest
from uuid import uuid4
from sqlalchemy import select
from datetime import datetime
from src.db.models import User, Link
from src.db import users as db_users
from src.db import links as db_links


EMAIL = "test@e.mail"
PASSWORD = "password"


@pytest.mark.asyncio
async def test_create_user(async_session):
    user = await db_users.create_user(async_session, EMAIL, PASSWORD)
    assert user.email == EMAIL
    assert user.hashed_password == PASSWORD
    assert user.is_active is True
    assert isinstance(user.registered_at, datetime)
    
    result = await async_session.execute(select(User).where(User.email == EMAIL))
    db_user = result.scalar_one()
    assert db_user.email == EMAIL


@pytest.mark.asyncio
async def test_get_user_by_email(async_session):
    await db_users.create_user(async_session, EMAIL, PASSWORD)
    
    user = await db_users.get_user_by_email(async_session, EMAIL)
    assert user is not None
    assert user.email == EMAIL
    
    user = await db_users.get_user_by_email(async_session, "not@exist.user")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_id(async_session):
    
    user = await db_users.create_user(async_session, EMAIL, PASSWORD)
    user_id = user.id
    
    user = await db_users.get_user_by_id(async_session, user_id)
    assert user is not None
    assert user.email == EMAIL

    user = await db_users.get_user_by_id(async_session, str(user_id))
    assert user is not None
    assert user.email == EMAIL
    
    user = await db_users.get_user_by_id(async_session, uuid4())
    assert user is None


@pytest.mark.asyncio
async def test_update_user(async_session):
    original_email = "original@example.com"
    new_email = "updated@example.com"
    
    user = await db_users.create_user(async_session, original_email, PASSWORD)
    updated_user = await db_users.update_user_email(async_session, user.id, new_email)
    
    assert updated_user is not None
    assert user.id == updated_user.id
    assert updated_user.email == new_email


@pytest.mark.asyncio
async def test_delete_user(async_session):
    user = await db_users.create_user(async_session, EMAIL, PASSWORD)
    result = await db_users.deactivate_user(async_session, user.id)
    assert result is True


@pytest.mark.asyncio
async def test_get_user_links(async_session):
    user = await db_users.create_user(async_session, EMAIL, PASSWORD)
    user_links = ['link1', 'link2']

    links_list = await db_users.get_user_links(async_session, user.id)
    assert len(links_list) == 0

    await db_links.create_link(async_session, user_links[0],
                               original_url=user_links[0], user_id=user.id)
    links_list = await db_users.get_user_links(async_session, user.id)
    assert len(links_list) == 1

    await db_links.create_link(async_session, user_links[1],
                               original_url=user_links[1], user_id=user.id)
    links_list = await db_users.get_user_links(async_session, user.id)
    assert len(links_list) == 2


@pytest.mark.asyncio
async def test_check_email_exists(async_session):

    result = await db_users.check_email_exists(async_session, EMAIL)
    assert result == False
    
    await db_users.create_user(async_session, EMAIL, PASSWORD)
    result = await db_users.check_email_exists(async_session, EMAIL)
    assert result == True

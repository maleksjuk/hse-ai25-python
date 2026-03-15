from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from datetime import datetime
from uuid import UUID, uuid4
from .models import User
from .database import DB_TYPE

async def create_user(db: DB_TYPE, email: str, hashed_password: str):
    user = User(
        id=uuid4(),
        email=email,
        hashed_password=hashed_password,
        registered_at=datetime.utcnow(),
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: DB_TYPE, email: str):
    result = await db.execute(select(User).filter(
        and_(
            User.email == email,
            User.is_active == True
        )
    ))
    return result.scalar_one_or_none()

async def get_user_by_id(db: DB_TYPE, user_id: str | UUID):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        result = await db.execute(select(User).filter(
            and_(
                User.id == user_id,
                User.is_active == True
            )
        ))
        return result.scalar_one_or_none()
    except ValueError:
        return None

async def get_user_links(db: DB_TYPE, user_id: str | UUID):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        return user.links if user else []
    except ValueError:
        return []

async def deactivate_user(db: DB_TYPE, user_id: str | UUID):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        if user is not None:
            user.is_active = False
            await db.commit()
            await db.refresh(user)
            return True
        return False
    except ValueError:
        return False

async def update_user_email(db: DB_TYPE, user_id: str | UUID, new_email: str):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        user = await db.execute(select(User).filter(
            and_(
                User.id == user_id,
                User.is_active == True
            )
        ))
        user = user.scalar_one_or_none()
        if user:
            user.email = new_email
            await db.commit()
            await db.refresh(user)
        return user
    except ValueError:
        return None

async def check_email_exists(db: DB_TYPE, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none() is not None

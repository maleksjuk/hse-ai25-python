from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from datetime import datetime
from .models import Link
from .database import DB_TYPE
from uuid import UUID


async def create_link(db: DB_TYPE, short_code: str, original_url: str,
                expires_at: datetime | None = None, user_id: UUID | None = None):
    new_link = Link(
        short_code=short_code,
        original_url=original_url,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link

async def get_active_link_by_code(db: DB_TYPE, short_code: str):
    result = await db.execute(select(Link).filter(
        and_(
            Link.short_code == short_code,
            Link.is_deleted == False
        )
    ))
    return result.scalar_one_or_none()

async def get_all_links_by_code(db: DB_TYPE, short_code: str):
    result = await db.execute(select(Link).filter(Link.short_code == short_code))
    return result.scalars().all()

async def search_by_original_url(db: DB_TYPE, original_url: str):
    result = await db.execute(select(Link).filter(
        Link.original_url.contains(original_url)
    ))
    return result.scalars().all()

# async def update_link_url(db: DB_TYPE, link_id: int, new_url: str):
#     link = db.query(Link).filter(Link.id == link_id).first()
#     if link:
#         link.original_url = new_url
#         db.commit()
#         db.refresh(link)
#     return link

async def delete_link(db: DB_TYPE, link: Link):
    if link:
        link.is_deleted = True
        await db.commit()
        return True
    return False

async def delete_expired_links(db: DB_TYPE):
    now = datetime.utcnow()
    deleted = await db.execute(
        update(Link)
        .where(
            and_(
                Link.expires_at < now,
                Link.expires_at.isnot(None),
                Link.is_deleted == False
            )
        )
        .values(is_deleted=True)
        .returning(Link.id)
    )
    await db.commit()
    return len(deleted.all())

async def increment_click_count(db: DB_TYPE, link: Link) -> None:
    link.click_count += 1
    link.last_using = datetime.utcnow()
    await db.commit()

async def get_unused_links(db: DB_TYPE, border_date: datetime):
    result = await db.execute(select(Link).filter(
        or_(
            and_(
                Link.last_using < border_date,
                Link.last_using.isnot(None)
                ),
            and_(
                Link.creation_date < border_date,
                Link.last_using.is_(None)
            )
        )
    ))
    return result.scalars().all()

async def get_deleted_links(db: DB_TYPE):
    result = await db.execute(select(Link).filter(Link.is_deleted == True))
    return result.scalars().all()

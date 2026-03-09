from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from .models import Link

def create_link(db: Session, short_code: str, original_url: str,
                expires_at: datetime | None = None, user_id: str | None = None):
    new_link = Link(
        short_code=short_code,
        original_url=original_url,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

def get_active_link_by_code(db: Session, short_code: str):
    return db.query(Link).filter(
        and_(
            Link.short_code == short_code,
            Link.is_deleted == False
        )
    ).first()

def get_all_links_by_code(db: Session, short_code: str):
    return db.query(Link).filter(Link.short_code == short_code).all()

def search_by_original_url(db: Session, original_url: str):
    return db.query(Link).filter(
        Link.original_url.contains(original_url)
    ).all()

# def update_link_url(db: Session, link_id: int, new_url: str):
#     link = db.query(Link).filter(Link.id == link_id).first()
#     if link:
#         link.original_url = new_url
#         db.commit()
#         db.refresh(link)
#     return link

def delete_link(db: Session, link: Link):
    if link:
        link.is_deleted = True
        db.commit()
        return True
    return False

def delete_expired_links(db: Session):
    now = datetime.utcnow()
    deleted_count = db.query(Link).filter(
        and_(
            Link.expires_at < now,
            Link.expires_at.isnot(None),
            Link.is_deleted == False
        )
    ).update({"is_deleted": True}, synchronize_session=True)
    db.commit()
    return deleted_count

def increment_click_count(db: Session, link: Link) -> None:
    link.click_count += 1
    link.last_using = datetime.utcnow()
    db.commit()

def get_unused_links(db: Session, border_date: datetime):
    return db.query(Link).filter(
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
    ).all()

def get_deleted_links(db: Session):
    return db.query(Link).filter(Link.is_deleted == True).all()

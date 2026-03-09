from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID, uuid4
from .models import User

def create_user(db: Session, email: str, hashed_password: str):
    user = User(
        id=uuid4(),
        email=email,
        hashed_password=hashed_password,
        registered_at=datetime.utcnow(),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(
        and_(
            User.email == email,
            User.is_active == True
        )
    ).first()

def get_user_by_id(db: Session, user_id: str | UUID):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        return db.query(User).filter(
            and_(
                User.id == user_id,
                User.is_active == True
            )
        ).first()
    except ValueError:
        return None

def get_user_links(db: Session, user_id: str | UUID):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        user = db.query(User).filter(User.id == user_id).first()
        return user.links if user else []
    except ValueError:
        return []

def deactivate_user(db: Session, user_id: str | UUID):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    except ValueError:
        return False

def update_user_email(db: Session, user_id: str | UUID, new_email: str):
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        user = db.query(User).filter(
            and_(
                User.id == user_id,
                User.is_active == True
            )
        ).first()
        if user:
            user.email = new_email
            db.commit()
            db.refresh(user)
        return user
    except ValueError:
        return None

def check_email_exists(db: Session, email: str):
    return db.query(User).filter(User.email == email).first() is not None

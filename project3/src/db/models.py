from datetime import datetime, timezone

from sqlalchemy import Column, String, TIMESTAMP, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    # registered_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True, nullable=False)

    links = relationship("Link", back_populates="owner")


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, nullable=False, index=True)
    original_url = Column(String, nullable=False, index=True)
    creation_date = Column(TIMESTAMP, default=datetime.utcnow)
    # creation_date = Column(TIMESTAMP, default=datetime.now(timezone.utc))
    click_count = Column(Integer, default=0)
    last_using = Column(TIMESTAMP)
    expires_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)

    user_id = Column(UUID, ForeignKey("users.id"))
    owner = relationship("User", back_populates="links")


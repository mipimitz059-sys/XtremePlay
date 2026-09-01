from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True,
    )

    description = Column(
        String(500),
        default="",
        nullable=False,
    )

    owner_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_private = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    max_members = Column(
        Integer,
        default=50,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # -------------------------
    # Relationships
    # -------------------------

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
    )

    members = relationship(
        "RoomMember",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    messages = relationship(
        "Message",
        back_populates="room",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"<Room("
            f"id={self.id}, "
            f"name='{self.name}')>"
        )
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    room_id = Column(
        Integer,
        ForeignKey(
            "rooms.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    message = Column(
        Text,
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

    user = relationship(
        "User",
        back_populates="messages",
    )

    room = relationship(
        "Room",
        back_populates="messages",
    )

    def __repr__(self):
        return (
            f"<Message("
            f"id={self.id}, "
            f"user={self.user_id}, "
            f"room={self.room_id})>"
        )
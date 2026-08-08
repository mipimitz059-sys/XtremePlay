from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    password = Column(
        String(255),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    sent_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )

    received_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    friends = relationship(
        "Friend",
        foreign_keys="Friend.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    messages = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    room_memberships = relationship(
        "RoomMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<User("
            f"id={self.id}, "
            f"username='{self.username}')>"
        )
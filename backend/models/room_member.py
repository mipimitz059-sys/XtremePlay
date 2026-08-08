from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class RoomMember(Base):
    __tablename__ = "room_members"

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "user_id",
            name="uq_room_member",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    room_id = Column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        String(20),
        nullable=False,
        default="member",
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    room = relationship(
        "Room",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="room_memberships",
    )

    def __repr__(self):
        return (
            f"<RoomMember("
            f"room={self.room_id}, "
            f"user={self.user_id}, "
            f"role='{self.role}')>"
        )
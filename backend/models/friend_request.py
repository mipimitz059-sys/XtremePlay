from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_requests",
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_requests",
    )

    def __repr__(self):
        return (
            f"<FriendRequest("
            f"{self.sender_id}->{self.receiver_id}, "
            f"status={self.status})>"
        )
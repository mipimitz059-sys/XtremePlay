from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    display_name = Column(
        String(100),
        nullable=True,
    )

    bio = Column(
        String(500),
        nullable=True,
    )

    avatar_url = Column(
        String(255),
        nullable=True,
    )

    level = Column(
        Integer,
        nullable=False,
        default=1,
    )

    xp = Column(
        Integer,
        nullable=False,
        default=0,
    )

    coins = Column(
        Integer,
        nullable=False,
        default=0,
    )

    diamonds = Column(
        Integer,
        nullable=False,
        default=0,
    )

    user = relationship(
        "User",
        back_populates="profile",
    )

    def __repr__(self):
        return (
            f"<Profile(user_id={self.user_id}, "
            f"display_name={self.display_name})>"
        )
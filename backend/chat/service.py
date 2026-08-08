from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.database.session import SessionLocal
from backend.models.message import Message
from backend.models.room import Room
from backend.models.room_member import RoomMember
from backend.models.user import User


MAX_MESSAGE_LENGTH = 5000
DEFAULT_MESSAGE_LIMIT = 50
MAX_MESSAGE_LIMIT = 100


def serialize_message(message: Message) -> dict[str, Any]:
    return {
        "id": message.id,
        "room_id": message.room_id,
        "user_id": message.user_id,
        "username": (
            message.user.username
            if message.user is not None
            else None
        ),
        "message": message.message,
        "created_at": (
            message.created_at.isoformat()
            if message.created_at
            else None
        ),
    }


def is_room_member(
    session,
    room_id: int,
    user_id: int,
) -> bool:

    room = session.get(Room, room_id)

    if room is None:
        return False

    # Owner automatically has access.
    if room.owner_id == user_id:
        return True

    membership = session.scalar(
        select(RoomMember.id).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id,
        )
    )

    return membership is not None


def send_message(
    room_id: int,
    user_id: int,
    message_text: str,
) -> dict[str, Any]:

    if not isinstance(message_text, str):
        return {
            "success": False,
            "message": "Message must be a string",
        }

    message_text = message_text.strip()

    if not message_text:
        return {
            "success": False,
            "message": "Message cannot be empty",
        }

    if len(message_text) > MAX_MESSAGE_LENGTH:
        return {
            "success": False,
            "message": (
                f"Message cannot exceed "
                f"{MAX_MESSAGE_LENGTH} characters"
            ),
        }

    session = SessionLocal()

    try:
        room = session.get(Room, room_id)

        if room is None:
            return {
                "success": False,
                "message": "Room not found",
            }

        user = session.get(User, user_id)

        if user is None:
            return {
                "success": False,
                "message": "User not found",
            }

        if not is_room_member(
            session,
            room_id,
            user_id,
        ):
            return {
                "success": False,
                "message": (
                    "You are not a member of this room"
                ),
            }

        new_message = Message(
            user_id=user_id,
            room_id=room_id,
            message=message_text,
        )

        session.add(new_message)
        session.commit()
        session.refresh(new_message)

        return {
            "success": True,
            "message": serialize_message(new_message),
        }

    except SQLAlchemyError as exc:
        session.rollback()

        # Development diagnostic.
        print("=" * 70)
        print("CHAT DATABASE ERROR")
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 70)

        return {
            "success": False,
            "message": "Failed to send message",
            "error": str(exc),
        }

    finally:
        session.close()


def get_messages(
    room_id: int,
    user_id: int,
    limit: int = DEFAULT_MESSAGE_LIMIT,
    before_id: int | None = None,
) -> dict[str, Any]:

    limit = max(
        1,
        min(limit, MAX_MESSAGE_LIMIT),
    )

    session = SessionLocal()

    try:
        room = session.get(Room, room_id)

        if room is None:
            return {
                "success": False,
                "message": "Room not found",
            }

        if not is_room_member(
            session,
            room_id,
            user_id,
        ):
            return {
                "success": False,
                "message": (
                    "You are not a member of this room"
                ),
            }

        query = select(Message).where(
            Message.room_id == room_id
        )

        if before_id is not None:
            query = query.where(
                Message.id < before_id
            )

        query = (
            query
            .order_by(Message.id.desc())
            .limit(limit)
        )

        messages = list(
            session.scalars(query).all()
        )

        messages.reverse()

        return {
            "success": True,
            "room_id": room_id,
            "messages": [
                serialize_message(message)
                for message in messages
            ],
            "count": len(messages),
            "has_more": len(messages) == limit,
        }

    except SQLAlchemyError as exc:
        print("=" * 70)
        print("CHAT READ DATABASE ERROR")
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 70)

        return {
            "success": False,
            "message": "Failed to retrieve messages",
            "error": str(exc),
        }

    finally:
        session.close()
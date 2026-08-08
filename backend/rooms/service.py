from sqlalchemy.exc import IntegrityError

from backend.database.session import SessionLocal

from backend.models.room import Room
from backend.models.room_member import RoomMember


def create_room(
    owner_id: int,
    name: str,
    description: str = "",
    is_private: bool = False,
    max_members: int = 50,
):
    session = SessionLocal()

    try:

        if not name:
            return {
                "success": False,
                "message": "Room name is required",
            }

        existing = (
            session.query(Room)
            .filter(Room.name == name)
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": "Room already exists",
            }

        room = Room(
            name=name,
            description=description,
            owner_id=owner_id,
            is_private=is_private,
            max_members=max_members,
        )

        session.add(room)
        session.flush()

        owner = RoomMember(
            room_id=room.id,
            user_id=owner_id,
            role="owner",
        )

        session.add(owner)

        session.commit()

        return {
            "success": True,
            "room": {
                "id": room.id,
                "name": room.name,
                "description": room.description,
                "owner_id": room.owner_id,
                "is_private": room.is_private,
                "max_members": room.max_members,
            },
        }

    except IntegrityError:

        session.rollback()

        return {
            "success": False,
            "message": "Room already exists",
        }

    except Exception as e:

        session.rollback()

        return {
            "success": False,
            "message": str(e),
        }

    finally:

        session.close()


def get_rooms():

    session = SessionLocal()

    try:

        rooms = (
            session.query(Room)
            .order_by(Room.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "rooms": [
                {
                    "id": room.id,
                    "name": room.name,
                    "description": room.description,
                    "owner_id": room.owner_id,
                    "is_private": room.is_private,
                    "max_members": room.max_members,
                }
                for room in rooms
            ],
        }

    finally:

        session.close()


def get_room(room_id: int):

    session = SessionLocal()

    try:

        room = session.get(Room, room_id)

        if room is None:
            return {
                "success": False,
                "message": "Room not found",
            }

        members = (
            session.query(RoomMember)
            .filter(RoomMember.room_id == room.id)
            .count()
        )

        return {
            "success": True,
            "room": {
                "id": room.id,
                "name": room.name,
                "description": room.description,
                "owner_id": room.owner_id,
                "is_private": room.is_private,
                "max_members": room.max_members,
                "members": members,
            },
        }

    finally:

        session.close()


def join_room(room_id: int, user_id: int):

    session = SessionLocal()

    try:

        room = session.get(Room, room_id)

        if room is None:
            return {
                "success": False,
                "message": "Room not found",
            }

        existing = (
            session.query(RoomMember)
            .filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id,
            )
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": "Already joined",
            }

        total = (
            session.query(RoomMember)
            .filter(RoomMember.room_id == room_id)
            .count()
        )

        if total >= room.max_members:
            return {
                "success": False,
                "message": "Room is full",
            }

        member = RoomMember(
            room_id=room_id,
            user_id=user_id,
            role="member",
        )

        session.add(member)

        session.commit()

        return {
            "success": True,
            "message": "Joined room",
        }

    finally:

        session.close()


def leave_room(room_id: int, user_id: int):

    session = SessionLocal()

    try:

        member = (
            session.query(RoomMember)
            .filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id,
            )
            .first()
        )

        if member is None:
            return {
                "success": False,
                "message": "Not a member",
            }

        session.delete(member)

        session.commit()

        return {
            "success": True,
            "message": "Left room",
        }

    finally:

        session.close()
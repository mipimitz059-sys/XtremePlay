"""Authenticated WebSocket endpoints for real-time room events."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

from quart import Blueprint, websocket

from backend.auth.utils import decode_access_token
from backend.chat.engine import engine
from backend.database.session import SessionLocal
from backend.models.room import Room
from backend.models.room_member import RoomMember
from backend.models.user import User
from backend.websocket.dispatcher import dispatcher
from backend.websocket.manager import manager

logger = logging.getLogger(__name__)

websocket_bp = Blueprint("websocket", __name__)

MAX_PACKET_BYTES = 16384
MAX_MESSAGE_LENGTH = 4000
POLICY_VIOLATION = 1008


@dataclass(frozen=True, slots=True)
class RoomPrincipal:
    user_id: int
    username: str
    room_id: int


async def _close_policy_violation():
    await websocket.close(POLICY_VIOLATION)


def _access_token_subject():

    authorization = websocket.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer":
        return None

    try:
        payload = decode_access_token(token)

        return int(payload["sub"])

    except Exception:
        logger.exception("Invalid websocket token")
        return None


def _authorize_room_connection(room_id: int, user_id: int):

    session = SessionLocal()

    try:

        user = session.get(User, user_id)
        room = session.get(Room, room_id)

        if user is None or room is None:
            return None

        member = (
            session.query(RoomMember)
            .filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id,
            )
            .first()
        )

        if member is None and room.owner_id != user_id:
            return None

        return RoomPrincipal(
            user_id=user.id,
            username=user.username,
            room_id=room.id,
        )

    finally:
        session.close()


async def _send_error(code: str, message: str):
    await websocket.send_json(
        {
            "type": "error",
            "code": code,
            "message": message,
        }
    )


async def _receive_packet():

    raw = await websocket.receive()

    if isinstance(raw, bytes):
        raw = raw.decode()

    packet = json.loads(raw)

    return packet


async def _process_message(
    principal: RoomPrincipal,
    packet: dict[str, Any],
):

    result = await asyncio.to_thread(
        engine.process_message,
        room_id=principal.room_id,
        user_id=principal.user_id,
        message=packet["message"],
    )

    if not result["success"]:

        await _send_error(
            "message_failed",
            result["message"],
        )

        return

    await manager.broadcast(
        principal.room_id,
        {
            "type": "message",
            "room_id": principal.room_id,
            "message": result["message"],
        },
    )


@websocket_bp.websocket("/api/v1/ws/rooms/<int:room_id>")
async def room_socket(room_id: int):

    print("=" * 80)
    print("WEBSOCKET CONNECT")
    print("ROOM:", room_id)
    print("HEADERS:", dict(websocket.headers))
    print("=" * 80)

    user_id = _access_token_subject()

    print("USER:", user_id)

    if user_id is None:
        print("AUTH FAILED")
        await _close_policy_violation()
        return

    principal = await asyncio.to_thread(
        _authorize_room_connection,
        room_id,
        user_id,
    )

    print("PRINCIPAL:", principal)

    if principal is None:
        print("ROOM AUTH FAILED")
        await _close_policy_violation()
        return

    connected = False

    try:

        # FIXED
        await manager.connect(
            room_id,
            websocket,
        )

        connected = True

        await websocket.send_json(
            {
                "type": "connected",
                "room_id": room_id,
                "user_id": principal.user_id,
            }
        )

        await manager.broadcast(
            room_id,
            {
                "type": "presence",
                "event": "joined",
                "room_id": room_id,
                "user_id": principal.user_id,
                "username": principal.username,
            },
        )

        while True:

            packet = await _receive_packet()

            if packet["type"] == "ping":

                if not await dispatcher.dispatch(packet):
                    await websocket.send_json(
                        {
                            "type": "pong",
                        }
                    )

                continue

            if packet["type"] == "message":

                await _process_message(
                    principal,
                    packet,
                )

                continue

            await _send_error(
                "unsupported",
                "Unsupported packet",
            )

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.exception("WebSocket crashed")

    finally:

        if connected:

            # FIXED
            await manager.disconnect(
                room_id,
                websocket,
            )

            try:

                await manager.broadcast(
                    room_id,
                    {
                        "type": "presence",
                        "event": "left",
                        "room_id": room_id,
                        "user_id": principal.user_id,
                        "username": principal.username,
                    },
                )

            except Exception:
                logger.exception("Presence broadcast failed")
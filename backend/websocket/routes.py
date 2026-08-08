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

MAX_PACKET_BYTES = 16_384
MAX_MESSAGE_LENGTH = 4_000
POLICY_VIOLATION = 1008


@dataclass(frozen=True, slots=True)
class RoomPrincipal:
    user_id: int
    username: str
    room_id: int


def _get_access_token() -> str | None:
    authorization = websocket.headers.get("Authorization", "")

    if authorization:
        scheme, _, token = authorization.partition(" ")

        if scheme.lower() == "bearer":
            token = token.strip()
            if token:
                return token

    # Browser WebSocket clients cannot set arbitrary Authorization headers.
    # Accept the short-lived access token as a query parameter for browser
    # compatibility. Never log the query string.
    token = websocket.args.get("access_token", "").strip()

    return token or None


def _authenticate() -> int | None:
    token = _get_access_token()

    if token is None:
        logger.warning("WebSocket rejected: missing bearer token")
        return None

    try:
        payload = decode_access_token(token)

        if not isinstance(payload, dict):
            return None

        token_type = payload.get("type") or payload.get("token_type")

        if token_type != "access":
            logger.warning("WebSocket rejected: invalid token type")
            return None

        subject = payload.get("sub")

        if subject is None:
            logger.warning("WebSocket rejected: missing token subject")
            return None

        return int(subject)

    except Exception:
        logger.warning(
            "WebSocket rejected: invalid access token",
            exc_info=True,
        )
        return None


def _authorize_room(
    room_id: int,
    user_id: int,
) -> RoomPrincipal | None:

    session = SessionLocal()

    try:
        user = session.get(User, user_id)
        room = session.get(Room, room_id)

        if user is None:
            logger.warning(
                "WebSocket authorization failed: user %s not found",
                user_id,
            )
            return None

        if room is None:
            logger.warning(
                "WebSocket authorization failed: room %s not found",
                room_id,
            )
            return None

        membership = (
            session.query(RoomMember)
            .filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id,
            )
            .first()
        )

        if membership is None and room.owner_id != user_id:
            logger.warning(
                "WebSocket authorization failed: "
                "user=%s room=%s not a member",
                user_id,
                room_id,
            )
            return None

        logger.info(
            "WebSocket authorization: AUTHORIZED user=%s room=%s",
            user_id,
            room_id,
        )

        return RoomPrincipal(
            user_id=user.id,
            username=user.username,
            room_id=room.id,
        )

    except Exception:
        logger.exception(
            "WebSocket authorization database failure"
        )
        return None

    finally:
        session.close()


async def _send_error(
    code: str,
    message: str,
) -> None:

    try:
        await websocket.send_json(
            {
                "type": "error",
                "code": code,
                "message": message,
            }
        )
    except Exception:
        logger.debug(
            "Unable to send WebSocket error",
            exc_info=True,
        )


async def _receive_packet() -> dict[str, Any] | None:

    try:
        raw_packet = await websocket.receive()

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.debug(
            "WebSocket receive failed",
            exc_info=True,
        )
        return None

    if isinstance(raw_packet, bytes):

        if len(raw_packet) > MAX_PACKET_BYTES:
            await _send_error(
                "packet_too_large",
                "Packet exceeds the allowed size",
            )
            return None

        try:
            raw_packet = raw_packet.decode("utf-8")

        except UnicodeDecodeError:
            await _send_error(
                "invalid_json",
                "Packet must be valid UTF-8 JSON",
            )
            return None

    if not isinstance(raw_packet, str):
        await _send_error(
            "invalid_packet",
            "Packet must be a JSON object",
        )
        return None

    if len(raw_packet.encode("utf-8")) > MAX_PACKET_BYTES:
        await _send_error(
            "packet_too_large",
            "Packet exceeds the allowed size",
        )
        return None

    try:
        packet = json.loads(raw_packet)

    except json.JSONDecodeError:
        await _send_error(
            "invalid_json",
            "Packet must contain valid JSON",
        )
        return None

    if not isinstance(packet, dict):
        await _send_error(
            "invalid_packet",
            "Packet must be a JSON object",
        )
        return None

    packet_type = packet.get("type")

    if not isinstance(packet_type, str):
        await _send_error(
            "invalid_packet",
            "Packet field 'type' must be a string",
        )
        return None

    return packet


async def _process_message(
    principal: RoomPrincipal,
    packet: dict[str, Any],
) -> None:

    message_text = packet.get("message")

    if not isinstance(message_text, str):
        await _send_error(
            "invalid_message",
            "Message must be a string",
        )
        return

    message_text = message_text.strip()

    if not message_text:
        await _send_error(
            "invalid_message",
            "Message cannot be empty",
        )
        return

    if len(message_text) > MAX_MESSAGE_LENGTH:
        await _send_error(
            "message_too_long",
            f"Message cannot exceed {MAX_MESSAGE_LENGTH} characters",
        )
        return

    try:
        result = await asyncio.to_thread(
            engine.process_message,
            room_id=principal.room_id,
            user_id=principal.user_id,
            message=message_text,
        )

    except Exception:
        logger.exception(
            "Message processing failed"
        )

        await _send_error(
            "message_processing_failed",
            "Message could not be processed",
        )
        return

    if not isinstance(result, dict):
        await _send_error(
            "message_rejected",
            "Message could not be sent",
        )
        return

    if not result.get("success"):
        await _send_error(
            "message_rejected",
            result.get("message")
            or "Message could not be sent",
        )
        return

    persisted_message = result.get("message")

    if not isinstance(persisted_message, dict):
        logger.error(
            "MessageEngine returned invalid message: %r",
            result,
        )

        await _send_error(
            "message_persistence_failed",
            "Message could not be sent",
        )
        return

    await manager.broadcast(
        principal.room_id,
        {
            "type": "message",
            "room_id": principal.room_id,
            "message": persisted_message,
        },
    )


@websocket_bp.websocket(
    "/api/v1/ws/rooms/<int:room_id>"
)
async def room_socket(room_id: int) -> None:

    logger.info(
        "WebSocket connection attempt room=%s",
        room_id,
    )

    user_id = await asyncio.to_thread(
        _authenticate
    )

    if user_id is None:
        logger.warning(
            "WebSocket authentication failed room=%s",
            room_id,
        )

        return (
            {
                "success": False,
                "message": "Unauthorized",
            },
            401,
        )

    principal = await asyncio.to_thread(
        _authorize_room,
        room_id,
        user_id,
    )

    if principal is None:
        logger.warning(
            "WebSocket room authorization failed "
            "user=%s room=%s",
            user_id,
            room_id,
        )

        return (
            {
                "success": False,
                "message": "Forbidden",
            },
            403,
        )

    # IMPORTANT:
    # Explicitly accept the WebSocket after authentication
    # and authorization have succeeded.
    await websocket.accept()

    connected = False

    try:

        await manager.connect(
            room_id,
            websocket._get_current_object(),
        )

        connected = True

        await websocket.send_json(
            {
                "type": "connected",
                "room_id": principal.room_id,
                "user_id": principal.user_id,
                "username": principal.username,
            }
        )

        await manager.broadcast(
            principal.room_id,
            {
                "type": "presence",
                "event": "joined",
                "room_id": principal.room_id,
                "user_id": principal.user_id,
                "username": principal.username,
            },
        )

        logger.info(
            "WebSocket CONNECTED user=%s room=%s",
            principal.user_id,
            principal.room_id,
        )

        while True:

            packet = await _receive_packet()

            if packet is None:
                break

            packet_type = packet["type"]

            if packet_type == "message":

                await _process_message(
                    principal,
                    packet,
                )

                continue

            if not await dispatcher.dispatch(packet):

                await _send_error(
                    "unsupported_type",
                    "Unsupported event type",
                )

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.debug(
            "Room WebSocket closed user=%s room=%s",
            principal.user_id,
            principal.room_id,
            exc_info=True,
        )

    finally:

        if connected:

            await manager.disconnect(
                room_id,
                websocket._get_current_object(),
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
                logger.debug(
                    "Presence broadcast failed",
                    exc_info=True,
                )

            logger.info(
                "WebSocket DISCONNECTED user=%s room=%s",
                principal.user_id,
                principal.room_id,
            )
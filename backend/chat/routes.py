from __future__ import annotations

from quart import Blueprint, jsonify, request

from backend.auth.utils import decode_access_token
from backend.chat.service import (
    get_messages,
    send_message,
)


chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/v1/rooms",
)


async def get_current_user() -> int | None:
    """
    Extract and validate the authenticated user from:

        Authorization: Bearer <access_token>
    """

    authorization = request.headers.get(
        "Authorization",
        "",
    ).strip()

    if not authorization.startswith("Bearer "):
        return None

    token = authorization[7:].strip()

    if not token:
        return None

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return int(user_id)

    except (ValueError, TypeError):
        return None

    except Exception:
        return None


@chat_bp.post("/<int:room_id>/messages")
async def create_message(room_id: int):
    """
    Send a message to a room.
    """

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized",
        }), 401

    data = await request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must be JSON",
        }), 400

    message_text = data.get("message")

    if not isinstance(message_text, str):
        return jsonify({
            "success": False,
            "message": "Missing message",
        }), 400

    result = send_message(
        room_id=room_id,
        user_id=user_id,
        message_text=message_text,
    )

    if not result["success"]:
        message = result.get(
            "message",
            "Request failed",
        )

        if message == "Room not found":
            return jsonify(result), 404

        if message == "User not found":
            return jsonify(result), 404

        if message == "You are not a member of this room":
            return jsonify(result), 403

        if message in {
            "Message cannot be empty",
            "Message is too long",
            "Message must be a string",
        }:
            return jsonify(result), 400

        return jsonify(result), 500

    return jsonify(result), 201


@chat_bp.get("/<int:room_id>/messages")
async def list_messages(room_id: int):
    """
    Retrieve messages from a room.

    Query parameters:

        limit
        before_id
    """

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized",
        }), 401

    # -----------------------------
    # limit
    # -----------------------------

    limit_raw = request.args.get(
        "limit",
        "50",
    )

    try:
        limit = int(limit_raw)

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid limit",
        }), 400

    if limit < 1 or limit > 100:
        return jsonify({
            "success": False,
            "message": "Limit must be between 1 and 100",
        }), 400

    # -----------------------------
    # before_id
    # -----------------------------

    before_id_raw = request.args.get(
        "before_id"
    )

    before_id = None

    if before_id_raw is not None:
        try:
            before_id = int(before_id_raw)

        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid before_id",
            }), 400

        if before_id <= 0:
            return jsonify({
                "success": False,
                "message": "before_id must be positive",
            }), 400

    result = get_messages(
        room_id=room_id,
        user_id=user_id,
        limit=limit,
        before_id=before_id,
    )

    if not result["success"]:
        message = result.get(
            "message",
            "Request failed",
        )

        if message == "Room not found":
            return jsonify(result), 404

        if message == "You are not a member of this room":
            return jsonify(result), 403

        return jsonify(result), 500

    return jsonify(result), 200
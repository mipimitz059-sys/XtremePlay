from quart import Blueprint, jsonify, request

from backend.auth.utils import decode_token
from backend.rooms.service import (
    create_room,
    get_rooms,
    get_room,
    join_room,
    leave_room,
)

rooms_bp = Blueprint(
    "rooms",
    __name__,
    url_prefix="/api/v1/rooms",
)


async def get_current_user():
    auth = request.headers.get("Authorization", "")

    print("\n" + "=" * 70)
    print("ROOM AUTH DEBUG")
    print("=" * 70)
    print("Authorization Header:")
    print(auth)

    if not auth:
        print("ERROR: No Authorization header")
        return None

    if not auth.startswith("Bearer "):
        print("ERROR: Authorization header must start with Bearer")
        return None

    token = auth.split(" ", 1)[1].strip()

    print("\nTOKEN:")
    print(token)

    try:
        payload = decode_token(token)

        print("\nJWT PAYLOAD:")
        print(payload)

        if "sub" not in payload:
            print("ERROR: Missing 'sub' claim")
            return None

        user_id = int(payload["sub"])

        print(f"Authenticated User ID: {user_id}")

        return user_id

    except Exception as e:
        print("\nJWT ERROR")
        print(type(e).__name__)
        print(str(e))
        return None


@rooms_bp.route("", methods=["POST"])
async def create():

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized",
        }), 401

    data = await request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Missing JSON",
        }), 400

    result = create_room(
        owner_id=user_id,
        name=data.get("name"),
        description=data.get("description", ""),
        is_private=data.get("is_private", False),
        max_members=data.get("max_members", 50),
    )

    return jsonify(result)


@rooms_bp.route("", methods=["GET"])
async def rooms():
    return jsonify(get_rooms())


@rooms_bp.route("/<int:room_id>", methods=["GET"])
async def room(room_id):
    return jsonify(get_room(room_id))


@rooms_bp.route("/<int:room_id>/join", methods=["POST"])
async def join(room_id):

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized",
        }), 401

    return jsonify(join_room(room_id, user_id))


@rooms_bp.route("/<int:room_id>/leave", methods=["POST"])
async def leave(room_id):

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized",
        }), 401

    return jsonify(leave_room(room_id, user_id))
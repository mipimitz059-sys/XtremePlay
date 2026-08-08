from quart import Blueprint, request, jsonify

from backend.auth.utils import decode_token
from backend.friends.service import (
    send_friend_request,
    get_pending_requests,
    accept_friend_request,
    get_friends,
)

friends_bp = Blueprint(
    "friends",
    __name__,
    url_prefix="/api/v1/friends",
)


async def get_current_user():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return None

    token = auth.split(" ", 1)[1]

    try:
        payload = decode_token(token)

        if "sub" not in payload:
            return None

        return int(payload["sub"])

    except Exception:
        return None


@friends_bp.route("/request", methods=["POST"])
async def friend_request():

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = await request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Missing JSON body"
        }), 400

    username = data.get("username")

    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400

    result = send_friend_request(
        user_id,
        username,
    )

    return jsonify(result)


@friends_bp.route("/pending", methods=["GET"])
async def pending():

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    requests = get_pending_requests(user_id)

    return jsonify({
        "success": True,
        "requests": requests,
    })


@friends_bp.route("/accept", methods=["POST"])
async def accept():

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = await request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Missing JSON body"
        }), 400

    request_id = data.get("request_id")

    if request_id is None:
        return jsonify({
            "success": False,
            "message": "request_id is required"
        }), 400

    result = accept_friend_request(
        request_id,
        user_id,
    )

    return jsonify(result)


@friends_bp.route("", methods=["GET"])
async def friends():

    user_id = await get_current_user()

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    friends = get_friends(user_id)

    return jsonify({
        "success": True,
        "friends": friends,
    })
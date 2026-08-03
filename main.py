import hashlib
import json
import os
import secrets
from datetime import datetime, timezone

import quart
import quart_cors
from quart import request

app = quart_cors.cors(
    quart.Quart(__name__),
    allow_origin=os.getenv("XTREMEPLAY_ALLOWED_ORIGIN", "https://chat.openai.com"),
)

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

# Phase 2 in-memory domain model for XtremePlay.
_USERS = {}
_SESSIONS = {}
_ROOMS = {}
_LEADERBOARD = {}
_PRESENCE = {}
_FRIEND_REQUESTS = {}
_FRIENDS = {}
_NOTIFICATIONS = {}


def _utcnow():
    return datetime.now(timezone.utc).isoformat()


def _json_response(payload, status=200):
    return quart.Response(response=json.dumps(payload), mimetype="application/json", status=status)


def _error(message, status=400):
    return _json_response({"error": message}, status=status)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _normalize_username(username: str) -> str:
    return (username or "").strip().lower()


async def _get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[len("Bearer "):].strip()
    user_id = _SESSIONS.get(token)
    if not user_id:
        return None

    return _USERS.get(user_id)


@app.get("/api/v1/health")
async def health():
    return _json_response({"service": "XtremePlay", "status": "ok", "timestamp": _utcnow()})


@app.post("/api/v1/auth/register")
async def register_user():
    payload = await request.get_json(force=True)
    username = _normalize_username(payload.get("username"))
    display_name = (payload.get("display_name") or username).strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not username or not email or len(password) < 8:
        return _error("username, email, and a password of at least 8 characters are required", 400)

    if any(user["username"] == username for user in _USERS.values()):
        return _error("username already exists", 409)

    user_id = f"user-{len(_USERS) + 1}"
    token = secrets.token_urlsafe(24)
    user = {
        "id": user_id,
        "username": username,
        "display_name": display_name or username,
        "email": email,
        "password_hash": _hash_password(password),
        "coins": 1000,
        "wallet": {"balance": 0, "currency": "XPL"},
        "created_at": _utcnow(),
        "roles": ["member"],
        "status": "offline",
        "avatar": "https://api.dicebear.com/7.x/thumbs/svg?seed=" + username,
    }
    _USERS[user_id] = user
    _SESSIONS[token] = user_id
    _FRIENDS.setdefault(user_id, [])
    _FRIEND_REQUESTS.setdefault(user_id, [])
    _NOTIFICATIONS.setdefault(user_id, [])

    return _json_response({"token": token, "user": user}, 201)


@app.post("/api/v1/auth/login")
async def login_user():
    payload = await request.get_json(force=True)
    username = _normalize_username(payload.get("username"))
    password = payload.get("password") or ""

    if not username or not password:
        return _error("username and password are required", 400)

    user = next((candidate for candidate in _USERS.values() if candidate["username"] == username), None)
    if not user or user["password_hash"] != _hash_password(password):
        return _error("invalid credentials", 401)

    token = secrets.token_urlsafe(24)
    _SESSIONS[token] = user["id"]
    user["last_token"] = token
    return _json_response({"token": token, "user": user})


@app.get("/api/v1/me")
async def get_current_user_profile():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)
    return _json_response({"user": user})


@app.post("/api/v1/rooms")
async def create_room():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    payload = await request.get_json(force=True)
    name = (payload.get("name") or "").strip()
    theme = (payload.get("theme") or "casual").strip()

    if not name:
        return _error("room name is required", 400)

    room_id = f"room-{len(_ROOMS) + 1}"
    room = {
        "id": room_id,
        "name": name,
        "theme": theme or "casual",
        "host_id": user["id"],
        "participants": [user["id"]],
        "created_at": _utcnow(),
    }
    _ROOMS[room_id] = room
    return _json_response({"room": room}, 201)


@app.get("/api/v1/rooms")
async def list_rooms():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)
    return _json_response({"rooms": list(_ROOMS.values())})


@app.get("/api/v1/users/search")
async def search_users():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    query = _normalize_username(request.args.get("query", ""))
    if not query:
        return _json_response({"users": []})

    matches = [
        {
            "id": candidate["id"],
            "username": candidate["username"],
            "display_name": candidate["display_name"],
            "avatar": candidate["avatar"],
            "status": candidate.get("status", "offline"),
        }
        for candidate in _USERS.values()
        if query in candidate["username"] or query in candidate["display_name"].lower()
    ]
    return _json_response({"users": matches})


@app.post("/api/v1/friends/requests")
async def send_friend_request():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    payload = await request.get_json(force=True)
    target_username = _normalize_username(payload.get("target_username"))
    target_user = next((candidate for candidate in _USERS.values() if candidate["username"] == target_username), None)

    if not target_user or target_user["id"] == user["id"]:
        return _error("invalid target user", 400)

    _FRIEND_REQUESTS.setdefault(target_user["id"], []).append({"from_user_id": user["id"], "username": user["username"]})
    _NOTIFICATIONS.setdefault(target_user["id"], []).append({"type": "friend_request", "from": user["username"], "message": f"{user['display_name']} wants to be friends"})
    return _json_response({"message": "friend request sent"}, 201)


@app.post("/api/v1/friends/requests/<string:username>/accept")
async def accept_friend_request(username):
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    source_user = next((candidate for candidate in _USERS.values() if candidate["username"] == username), None)
    if not source_user:
        return _error("user not found", 404)

    pending_requests = [request for request in _FRIEND_REQUESTS.get(user["id"], []) if request.get("from_user_id") == source_user["id"]]
    if not pending_requests:
        return _error("friend request not found", 404)

    _FRIENDS.setdefault(user["id"], []).append(source_user["id"])
    _FRIENDS.setdefault(source_user["id"], []).append(user["id"])
    _FRIEND_REQUESTS[user["id"]] = [request for request in _FRIEND_REQUESTS.get(user["id"], []) if request.get("from_user_id") != source_user["id"]]
    _NOTIFICATIONS.setdefault(user["id"], []).append({"type": "friend_accept", "from": source_user["username"], "message": f"{source_user['display_name']} accepted your request"})
    return _json_response({"status": "accepted", "friend": {"id": source_user["id"], "username": source_user["username"]}})


@app.get("/api/v1/friends")
async def list_friends():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    friend_ids = _FRIENDS.get(user["id"], [])
    friends = [
        {
            "id": friend_id,
            "username": _USERS[friend_id]["username"],
            "display_name": _USERS[friend_id]["display_name"],
            "status": _USERS[friend_id].get("status", "offline"),
        }
        for friend_id in friend_ids
        if friend_id in _USERS
    ]
    return _json_response({"friends": friends})


@app.post("/api/v1/presence")
async def update_presence():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    payload = await request.get_json(force=True)
    status = (payload.get("status") or "online").strip()
    channel = (payload.get("channel") or "lobby").strip()
    user["status"] = status
    _PRESENCE[user["id"]] = {"status": status, "channel": channel}
    return _json_response({"status": status, "channel": channel})


@app.get("/api/v1/notifications")
async def list_notifications():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    notifications = _NOTIFICATIONS.get(user["id"], [])
    return _json_response({"notifications": notifications})


@app.post("/api/v1/leaderboard/score")
async def update_leaderboard_score():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    payload = await request.get_json(force=True)
    score = int(payload.get("score", 0))
    entry = {
        "user_id": user["id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "score": score,
        "updated_at": _utcnow(),
    }
    _LEADERBOARD[user["id"]] = entry
    return _json_response({"score": score, "entry": entry})


@app.get("/api/v1/leaderboard")
async def list_leaderboard():
    user = await _get_current_user()
    if not user:
        return _error("authentication required", 401)

    entries = sorted(_LEADERBOARD.values(), key=lambda item: item["score"], reverse=True)
    return _json_response({"entries": entries})


@app.post("/todos/<string:username>")
async def add_todo(username):
    payload = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(payload["todo"])
    return quart.Response(response="OK", status=200)


@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)


@app.delete("/todos/<string:username>")
async def delete_todo(username):
    payload = await quart.request.get_json(force=True)
    todo_idx = payload["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS.get(username, [])):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response="OK", status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await quart.send_file(filename, mimetype="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as handle:
        text = handle.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as handle:
        text = handle.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()

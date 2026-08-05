from quart import Blueprint, request

auth_bp = Blueprint("auth", __name__)

_USERS = {}

@auth_bp.post("/register")
async def register():
    data = await request.get_json()

    username = data.get("username")

    if username in _USERS:
        return {"error": "Username already exists"}, 409

    _USERS[username] = data

    return {
        "success": True,
        "user": _USERS[username]
    }, 201


@auth_bp.get("/health")
async def auth_health():
    return {
        "module": "auth",
        "status": "ok"
    }
from quart import Blueprint, request

from backend.auth.service import register, login

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
async def register_route():
    data = await request.get_json()

    username = data.get("username")
    password = data.get("password")

    result = register(username, password)

    if not result["success"]:
        return result, 409

    return result, 201


@auth_bp.post("/login")
async def login_route():
    data = await request.get_json()

    username = data.get("username")
    password = data.get("password")

    result = login(username, password)

    if not result["success"]:
        return result, 401

    return result


@auth_bp.get("/health")
async def auth_health():
    return {
        "module": "auth",
        "status": "ok",
    }
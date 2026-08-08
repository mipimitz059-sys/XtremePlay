from quart import Blueprint, request

from backend.auth.utils import decode_token
from backend.profile.service import get_user_profile

profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/health")
async def health():
    return {
        "module": "profile",
        "status": "ok",
    }


@profile_bp.get("/me")
async def my_profile():
    auth = request.headers.get("Authorization")

    if not auth:
        return {
            "success": False,
            "message": "Authorization header missing",
        }, 401

    if not auth.startswith("Bearer "):
        return {
            "success": False,
            "message": "Invalid Authorization header",
        }, 401

    token = auth.split(" ", 1)[1]

    try:
        payload = decode_token(token)
    except Exception:
        return {
            "success": False,
            "message": "Invalid or expired token",
        }, 401

    username = payload.get("sub")

    return get_user_profile(username)
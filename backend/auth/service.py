from backend.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

_USERS = {}


def register(username: str, password: str):
    if username in _USERS:
        return {"success": False, "message": "User already exists"}

    _USERS[username] = {
        "username": username,
        "password": hash_password(password),
    }

    return {
        "success": True,
        "user": {
            "username": username,
        },
    }


def login(username: str, password: str):
    user = _USERS.get(username)

    if not user:
        return {"success": False, "message": "Invalid credentials"}

    if not verify_password(password, user["password"]):
        return {"success": False, "message": "Invalid credentials"}

    return {
        "success": True,
        "access_token": create_access_token(username),
        "refresh_token": create_refresh_token(username),
        "user": {
            "username": username,
        },
    }
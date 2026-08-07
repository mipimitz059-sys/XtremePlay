from backend.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from backend.database.db import (
    create_user,
    get_user,
)


def register(username: str, password: str):

    print("=" * 60)
    print("REGISTER")
    print("USERNAME:", username)
    print("=" * 60)

    user = get_user(username)

    if user:
        return {
            "success": False,
            "message": "User already exists",
        }

    user_id = create_user(
        username,
        hash_password(password),
    )

    return {
        "success": True,
        "user": {
            "id": user_id,
            "username": username,
        },
    }


def login(username: str, password: str):

    user = get_user(username)

    if not user:
        return {
            "success": False,
            "message": "Invalid credentials",
        }

    if not verify_password(password, user["password"]):
        return {
            "success": False,
            "message": "Invalid credentials",
        }

    access_token = create_access_token(user["id"])
    refresh_token = create_refresh_token(user["id"])

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user["id"],
            "username": user["username"],
        },
    }
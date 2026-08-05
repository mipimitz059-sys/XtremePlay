from backend.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from backend.database.db import create_user, get_user


def register(username: str, password: str):
    print("USERNAME =", username)
    print("PASSWORD =", password)
    print("PASSWORD TYPE =", type(password))
    print("PASSWORD LENGTH =", len(password))

    user = get_user(username)

    if user:
        return {
            "success": False,
            "message": "User already exists",
        }

    create_user(username, hash_password(password))

    return {
        "success": True,
        "user": {
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

    return {
        "success": True,
        "access_token": create_access_token(username),
        "refresh_token": create_refresh_token(username),
        "user": {
            "username": user["username"],
        },
    }
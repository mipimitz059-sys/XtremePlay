from backend.database.db import get_user, get_profile


def get_user_profile(username: str):
    user = get_user(username)

    if not user:
        return {
            "success": False,
            "message": "User not found",
        }

    profile = get_profile(user["id"])

    if not profile:
        return {
            "success": False,
            "message": "Profile not found",
        }

    return {
        "success": True,
        "profile": {
            "username": user["username"],
            "display_name": profile["display_name"],
            "bio": profile["bio"],
            "avatar_url": profile["avatar_url"],
            "cover_url": profile["cover_url"],
            "country": profile["country"],
            "level": profile["level"],
            "xp": profile["xp"],
            "coins": profile["coins"],
            "diamonds": profile["diamonds"],
            "followers": profile["followers"],
            "following": profile["following"],
        },
    }
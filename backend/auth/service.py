from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from backend.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from backend.database.session import SessionLocal
from backend.models.user import User
from backend.models.profile import Profile


def register(username: str, password: str):
    """Register a new XtremePlay user and create their profile."""

    session = SessionLocal()

    try:
        username = (username or "").strip()
        password = password or ""

        if not username or not password:
            return {
                "success": False,
                "message": "Username and password are required",
            }

        existing = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": "User already exists",
            }

        user = User(
            username=username,
            password=hash_password(password),
        )

        session.add(user)
        session.flush()

        profile = Profile(
            user_id=user.id,
            display_name=username,
            bio="",
            avatar_url="",
            level=1,
            xp=0,
            coins=0,
            diamonds=0,
        )

        session.add(profile)
        session.commit()
        session.refresh(user)

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
            },
        }

    except IntegrityError:
        session.rollback()

        return {
            "success": False,
            "message": "User already exists",
        }

    except Exception as exc:
        session.rollback()

        print("\nREGISTER ERROR")
        print(type(exc).__name__)
        print(str(exc))

        return {
            "success": False,
            "message": "Registration failed",
        }

    finally:
        session.close()


def login(username: str, password: str):
    """Authenticate a user and issue access and refresh JWTs."""

    session = SessionLocal()

    try:
        username = (username or "").strip()
        password = password or ""

        if not username or not password:
            return {
                "success": False,
                "message": "Username and password are required",
            }

        user = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )

        if user is None:
            return {
                "success": False,
                "message": "Invalid credentials",
            }

        if not verify_password(password, user.password):
            return {
                "success": False,
                "message": "Invalid credentials",
            }

        return {
            "success": True,
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "user": {
                "id": user.id,
                "username": user.username,
            },
        }

    except Exception as exc:
        print("\nLOGIN ERROR")
        print(type(exc).__name__)
        print(str(exc))

        return {
            "success": False,
            "message": "Login failed",
        }

    finally:
        session.close()

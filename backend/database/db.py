from pathlib import Path
import sqlite3

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base


# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "xtremeplay.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ==========================================================
# LEGACY SQLITE CONNECTION
#
# Existing modules such as friends/service.py use this API.
# Keep it available while the application migrates to
# SQLAlchemy.
# ==========================================================

def get_connection():
    """
    Return a SQLite connection compatible with the existing
    friends/profile/database services.

    Row objects can be accessed by column name.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign-key enforcement for this connection.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==========================================================
# SQLALCHEMY ENGINE
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
    future=True,
)


# ==========================================================
# SQLALCHEMY SESSION
# ==========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ==========================================================
# MODEL REGISTRATION
# ==========================================================

def load_models():
    """
    Import all models so SQLAlchemy registers their metadata.
    """

    from backend.models.user import User
    from backend.models.profile import Profile
    from backend.models.friend import Friend
    from backend.models.friend_request import FriendRequest
    from backend.models.message import Message
    from backend.models.room import Room
    from backend.models.room_member import RoomMember

    return {
        "User": User,
        "Profile": Profile,
        "Friend": Friend,
        "FriendRequest": FriendRequest,
        "Message": Message,
        "Room": Room,
        "RoomMember": RoomMember,
    }


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

def init_db():
    """
    Initialize the database without destroying existing data.
    """

    load_models()

    Base.metadata.create_all(bind=engine)

    print("=" * 60)
    print("XtremePlay database initialized successfully")
    print("=" * 60)


# ==========================================================
# USER FUNCTIONS
# ==========================================================

def create_user(
    username: str,
    password: str,
):
    """
    Create a new user.

    Password must already be hashed.
    """

    models = load_models()
    User = models["User"]

    db = SessionLocal()

    try:
        user = User(
            username=username,
            password=password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_user(username: str):
    """
    Retrieve a user by username.
    """

    models = load_models()
    User = models["User"]

    db = SessionLocal()

    try:
        user = db.execute(
            select(User).where(
                User.username == username
            )
        ).scalar_one_or_none()

        if user is None:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "password": user.password,
        }

    finally:
        db.close()


def get_user_by_id(user_id: int):
    """
    Retrieve a user by ID.
    """

    models = load_models()
    User = models["User"]

    db = SessionLocal()

    try:
        user = db.get(User, user_id)

        if user is None:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "password": user.password,
        }

    finally:
        db.close()


# ==========================================================
# PROFILE FUNCTIONS
# ==========================================================

def get_profile(user_id: int):
    """
    Retrieve a profile by user ID.
    """

    models = load_models()
    Profile = models["Profile"]

    db = SessionLocal()

    try:
        profile = db.execute(
            select(Profile).where(
                Profile.user_id == user_id
            )
        ).scalar_one_or_none()

        if profile is None:
            return None

        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "level": profile.level,
            "xp": profile.xp,
            "coins": profile.coins,
            "diamonds": profile.diamonds,
        }

    finally:
        db.close()


def create_profile(
    user_id: int,
    display_name: str = "",
    bio: str = "",
    avatar_url: str = "",
):
    """
    Create a profile if one does not already exist.
    """

    models = load_models()
    Profile = models["Profile"]

    db = SessionLocal()

    try:
        existing = db.execute(
            select(Profile).where(
                Profile.user_id == user_id
            )
        ).scalar_one_or_none()

        if existing is not None:
            return existing.id

        profile = Profile(
            user_id=user_id,
            display_name=display_name,
            bio=bio,
            avatar_url=avatar_url,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def update_profile(
    user_id: int,
    display_name=None,
    bio=None,
    avatar_url=None,
):
    """
    Update only fields supplied by the caller.
    """

    models = load_models()
    Profile = models["Profile"]

    db = SessionLocal()

    try:
        profile = db.execute(
            select(Profile).where(
                Profile.user_id == user_id
            )
        ).scalar_one_or_none()

        if profile is None:
            return None

        if display_name is not None:
            profile.display_name = display_name

        if bio is not None:
            profile.bio = bio

        if avatar_url is not None:
            profile.avatar_url = avatar_url

        db.commit()
        db.refresh(profile)

        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "level": profile.level,
            "xp": profile.xp,
            "coins": profile.coins,
            "diamonds": profile.diamonds,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================================
# SQLALCHEMY SESSION HELPER
# ==========================================================

def get_db():
    """
    Yield a SQLAlchemy session.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
import os
from datetime import datetime, timedelta, UTC

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from jwt import ExpiredSignatureError, InvalidTokenError

load_dotenv()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

SECRET_KEY = os.getenv("SECRET_KEY", "xtremeplay-dev-secret")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(UTC)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(UTC)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str):
    """
    Decode any valid JWT.
    Raises an exception if invalid.
    """

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    return payload


def decode_access_token(token: str):
    """
    Decode only access tokens.
    """

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")

    return payload


def decode_refresh_token(token: str):
    """
    Decode only refresh tokens.
    """

    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")

    return payload
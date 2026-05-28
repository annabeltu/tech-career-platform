from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from core.config import get_settings
from core.errors import AuthorizationError
from api.database import get_session
from api.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/waypoint/auth/login")


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthorizationError("Invalid token.")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise AuthorizationError("Token has expired.")
    except jwt.InvalidTokenError:
        raise AuthorizationError("Invalid token.")


# ── Dependency ────────────────────────────────────────────────────────────────

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    user_id = decode_token(token)
    user = session.get(User, user_id)
    if not user:
        raise AuthorizationError("User not found.")
    return user


def require_same_user(user_id: int, current_user: User) -> None:
    """Raise AuthorizationError if the token user doesn't match the path user_id."""
    if current_user.id != user_id:
        raise AuthorizationError("You do not have access to this resource.")
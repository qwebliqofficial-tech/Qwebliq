import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, Request, status

from database import db

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=ALGORITHM)


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization[7:]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("Unexpected token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])}, {"_id": 0})
        if not user:
            raise ValueError("User does not exist")
        user.pop("password_hash", None)
        return user
    except (InvalidId, jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")


async def require_admin(request: Request) -> dict:
    user = await get_current_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
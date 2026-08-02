from datetime import datetime, timedelta, timezone

import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from database import db
from schemas import ClientCreateRequest, LoginRequest
from security import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def safe_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]) if "_id" in user else user.get("id", ""),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


def set_session(response: Response, user: dict) -> None:
    access_token = create_access_token(str(user["_id"]), user["email"], user["role"])
    refresh_token = create_refresh_token(str(user["_id"]))
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=900,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=604800,
        path="/",
    )


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response) -> dict:
    email = str(payload.email).lower()
    identifier = f"{request.client.host}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": identifier}, {"_id": 0})
    if attempt and attempt.get("locked_until", "") > datetime.now(timezone.utc).isoformat():
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Try again later")

    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        attempts = int(attempt.get("attempts", 0)) + 1 if attempt else 1
        update = {"attempts": attempts, "updated_at": datetime.now(timezone.utc).isoformat()}
        if attempts >= 5:
            update["locked_until"] = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        await db.login_attempts.update_one({"identifier": identifier}, {"$set": update}, upsert=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    await db.login_attempts.delete_one({"identifier": identifier})
    set_session(response, user)
    return safe_user(user)


@router.post("/logout")
async def logout(response: Response, _: dict = Depends(get_current_user)) -> dict:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Signed out"}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)) -> dict:
    return user


@router.post("/refresh")
async def refresh(request: Request, response: Response) -> dict:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    try:
        payload = jwt.decode(token, __import__("os").environ["JWT_SECRET"], algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise ValueError("Unexpected token")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise ValueError("User does not exist")
        set_session(response, user)
        return safe_user(user)
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")


@router.post("/clients", status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreateRequest, _: dict = Depends(require_admin)) -> dict:
    email = str(payload.email).lower()
    if await db.users.find_one({"email": email}, {"_id": 0}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already uses this email")
    document = {
        "name": payload.name,
        "email": email,
        "password_hash": hash_password(payload.password),
        "role": "client",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(document)
    document.pop("_id", None)
    document.pop("password_hash", None)
    document["id"] = str(result.inserted_id)
    return document
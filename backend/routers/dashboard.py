from datetime import datetime, timezone
from copy import deepcopy

import requests
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from database import db
from schemas import ContentCreateRequest, ProjectCreateRequest, SiteSettingsUpdateRequest
from security import get_current_user, require_admin
from services.storage import download_media, upload_media

router = APIRouter(tags=["Dashboards"])

ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4"}
MAX_MEDIA_BYTES = 25 * 1024 * 1024
EXTENSIONS_BY_TYPE = {
    "image/jpeg": {"jpg", "jpeg"},
    "image/png": {"png"},
    "image/webp": {"webp"},
    "image/gif": {"gif"},
    "video/mp4": {"mp4"},
}


def merge_settings(current: dict, incoming: dict) -> dict:
    result = deepcopy(current)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value
    return result


def validate_settings(settings: dict) -> None:
    calculator = settings.get("calculator", {})
    valid_services = isinstance(settings.get("services"), list) and settings["services"]
    valid_prices = isinstance(calculator.get("base_prices"), dict) and calculator["base_prices"]
    valid_math = isinstance(calculator.get("per_page"), (int, float))
    valid_math = valid_math and calculator["per_page"] >= 0
    valid_math = valid_math and isinstance(calculator.get("rush_multiplier"), (int, float))
    valid_math = valid_math and calculator["rush_multiplier"] >= 1
    if not valid_services or not valid_prices or not valid_math:
        raise HTTPException(status_code=422, detail="Settings need services and valid calculator rules")


@router.get("/admin/overview")
async def admin_overview(_: dict = Depends(require_admin)) -> dict:
    inquiries = await db.inquiries.count_documents({})
    subscribers = await db.newsletter_subscribers.count_documents({})
    projects = await db.projects.count_documents({})
    recent_inquiries = await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(8)
    return {
        "metrics": [
            {"label": "Open leads", "value": inquiries, "trend": "Live"},
            {"label": "Projects", "value": projects, "trend": "Portfolio"},
            {"label": "Subscribers", "value": subscribers, "trend": "Audience"},
            {"label": "Studio health", "value": "Ready", "trend": "Operational"},
        ],
        "recent_inquiries": recent_inquiries,
    }


@router.get("/admin/inquiries")
async def list_inquiries(_: dict = Depends(require_admin)) -> list[dict]:
    return await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)


@router.get("/admin/site-settings")
async def get_site_settings(_: dict = Depends(require_admin)) -> dict:
    settings = await db.site_settings.find_one({"key": "public"}, {"_id": 0})
    return {"settings": settings}


@router.put("/admin/site-settings")
async def update_site_settings(
    payload: SiteSettingsUpdateRequest,
    _: dict = Depends(require_admin),
) -> dict:
    current = await db.site_settings.find_one({"key": "public"}, {"_id": 0})
    if current is None:
        raise HTTPException(status_code=503, detail="Website settings are unavailable")
    settings = merge_settings(current, payload.settings)
    settings["key"] = "public"
    validate_settings(settings)
    await db.site_settings.update_one({"key": "public"}, {"$set": settings}, upsert=True)
    saved = await db.site_settings.find_one({"key": "public"}, {"_id": 0})
    return {"settings": saved}


@router.post("/admin/media", status_code=status.HTTP_201_CREATED)
async def upload_project_media(
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
) -> dict:
    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(status_code=415, detail="Use a JPG, PNG, WEBP, GIF, or MP4 file")
    data = await file.read()
    if len(data) > MAX_MEDIA_BYTES:
        raise HTTPException(status_code=413, detail="Files must be 25 MB or smaller")
    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "bin"
    if extension not in EXTENSIONS_BY_TYPE[file.content_type]:
        raise HTTPException(status_code=415, detail="File extension does not match its media type")
    try:
        result = await run_in_threadpool(upload_media, data, file.content_type, extension)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Media storage is temporarily unavailable")
    document = {
        "storage_path": result["path"],
        "original_filename": file.filename,
        "content_type": file.content_type,
        "size": result["size"],
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_result = await db.media_files.insert_one(document)
    return {"id": str(insert_result.inserted_id), "url": f"/api/media/{insert_result.inserted_id}"}


@router.get("/media/{media_id}")
async def get_project_media(media_id: str) -> Response:
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        record = await db.media_files.find_one(
            {"_id": ObjectId(media_id), "is_deleted": False},
            {"_id": 0},
        )
    except InvalidId:
        record = None
    if record is None:
        raise HTTPException(status_code=404, detail="Media file not found")
    try:
        data, content_type = await run_in_threadpool(download_media, record["storage_path"])
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Media storage is temporarily unavailable")
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/admin/projects", status_code=status.HTTP_201_CREATED)
async def add_project(payload: ProjectCreateRequest, _: dict = Depends(require_admin)) -> dict:
    document = payload.model_dump()
    document.update(
        {
            "featured": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "technologies": ["Strategy", "Design", "Development"],
        }
    )
    if not document["cover_image"]:
        document.pop("cover_image")
    result = await db.projects.insert_one(document)
    document.pop("_id", None)
    document["id"] = str(result.inserted_id)
    return document


@router.post("/admin/feed", status_code=status.HTTP_201_CREATED)
async def add_feed_post(payload: ContentCreateRequest, _: dict = Depends(require_admin)) -> dict:
    document = payload.model_dump()
    document.update({"tag": document.pop("category"), "date": "Just now"})
    result = await db.feed_posts.insert_one(document)
    document.pop("_id", None)
    document["id"] = str(result.inserted_id)
    return document


@router.post("/admin/blog", status_code=status.HTTP_201_CREATED)
async def add_blog_post(payload: ContentCreateRequest, _: dict = Depends(require_admin)) -> dict:
    document = payload.model_dump()
    document.update({"status": "published", "published_at": datetime.now(timezone.utc).date().isoformat()})
    result = await db.blog_posts.insert_one(document)
    document.pop("_id", None)
    document["id"] = str(result.inserted_id)
    return document


@router.get("/client/projects")
async def client_projects(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] == "admin":
        return {"projects": [], "message": "Create a client account to preview client project data."}
    return {
        "projects": [
            {
                "name": "Your digital growth project",
                "status": "Discovery",
                "progress": 18,
                "next_step": "Project kick-off and requirements review",
            }
        ],
        "message": "Your workspace will show approved milestones, files, and decisions here.",
    }
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from database import db
from schemas import ContentCreateRequest, ProjectCreateRequest
from security import get_current_user, require_admin

router = APIRouter(tags=["Dashboards"])


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
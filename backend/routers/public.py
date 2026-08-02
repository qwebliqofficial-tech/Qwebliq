from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from database import db
from schemas import CalculatorRequest, InquiryRequest, NewsletterRequest

router = APIRouter(tags=["Public"])

FAQS = [
    {"q": "What kind of teams do you work with?", "a": "Ambitious businesses, institutions, and founders ready to improve their digital presence."},
    {"q": "Can you support us after launch?", "a": "Yes. Ongoing optimisation, content, support, and growth work can be shaped around your team."},
    {"q": "Do you work beyond websites?", "a": "Yes. Brand direction, acquisition, systems, and digital operations sit alongside the website work."},
    {"q": "How do projects begin?", "a": "We start with context: your goals, audience, priorities, and the opportunity in front of you."},
]


@router.get("/")
async def root() -> dict:
    return {"message": "Qwebliq Platform API"}


@router.get("/site")
async def get_site_content() -> dict:
    settings = await db.site_settings.find_one({"key": "public"}, {"_id": 0})
    projects = await db.projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    posts = await db.feed_posts.find({}, {"_id": 0}).to_list(50)
    blogs = await db.blog_posts.find({"status": "published"}, {"_id": 0}).to_list(50)
    return {
        "services": settings["services"],
        "projects": projects,
        "feed": posts,
        "blogs": blogs,
        "faqs": FAQS,
        "settings": settings,
    }


@router.post("/inquiries", status_code=status.HTTP_201_CREATED)
async def create_inquiry(payload: InquiryRequest) -> dict:
    document = payload.model_dump()
    document["email"] = str(payload.email).lower()
    document["status"] = "new"
    document["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.inquiries.insert_one(document)
    return {"message": "Thanks — your project note is safely with our team."}


@router.post("/newsletter", status_code=status.HTTP_201_CREATED)
async def subscribe(payload: NewsletterRequest) -> dict:
    email = str(payload.email).lower()
    try:
        await db.newsletter_subscribers.insert_one(
            {"email": email, "created_at": datetime.now(timezone.utc).isoformat()}
        )
    except DuplicateKeyError:
        pass
    return {"message": "You’re on the list."}


@router.post("/calculator")
async def calculate_project(payload: CalculatorRequest) -> dict:
    settings = await db.site_settings.find_one({"key": "public"}, {"_id": 0})
    calculator = settings["calculator"]
    base_price = calculator["base_prices"].get(payload.project_type)
    if base_price is None:
        raise HTTPException(status_code=422, detail="Unknown project type")
    timeline_factor = calculator["rush_multiplier"] if payload.timeline == "accelerated" else 1
    estimate = int((base_price + (payload.pages - 1) * calculator["per_page"]) * timeline_factor)
    return {"estimate": estimate, "currency": "INR", "label": f"₹{estimate:,} onwards"}
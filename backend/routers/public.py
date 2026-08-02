from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from database import db
from schemas import CalculatorRequest, InquiryRequest, NewsletterRequest

router = APIRouter(tags=["Public"])

SERVICES = [
    {"name": "Digital foundations", "detail": "Websites, product experiences, and distinctive digital homes."},
    {"name": "Brand systems", "detail": "Identity, direction, and design systems made to stay coherent."},
    {"name": "Commerce & platforms", "detail": "E-commerce, portals, operations, and conversion-focused flows."},
    {"name": "Growth & visibility", "detail": "SEO, performance, social, and practical digital momentum."},
]

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
    projects = await db.projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    posts = await db.feed_posts.find({}, {"_id": 0}).to_list(50)
    blogs = await db.blog_posts.find({"status": "published"}, {"_id": 0}).to_list(50)
    return {
        "services": SERVICES,
        "projects": projects,
        "feed": posts,
        "blogs": blogs,
        "faqs": FAQS,
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
    except Exception as exc:
        if "duplicate" not in str(exc).lower():
            raise HTTPException(status_code=500, detail="Unable to save your subscription")
    return {"message": "You’re on the list."}


@router.post("/calculator")
async def calculate_project(payload: CalculatorRequest) -> dict:
    base_prices = {"website": 65000, "ecommerce": 120000, "brand": 45000, "growth": 35000}
    timeline_factor = 1.25 if payload.timeline == "accelerated" else 1
    estimate = int((base_prices[payload.project_type] + (payload.pages - 1) * 4500) * timeline_factor)
    return {"estimate": estimate, "currency": "INR", "label": f"₹{estimate:,} onwards"}
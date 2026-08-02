import os
from datetime import datetime, timezone

import bcrypt
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]


def close_mongo_connection() -> None:
    client.close()


async def seed_application_data() -> None:
    await db.users.create_index("email", unique=True)
    await db.newsletter_subscribers.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier", unique=True)
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.media_files.create_index("storage_path", unique=True)
    await db.inquiries.create_index([("record_type", 1), ("is_test", 1), ("name", 1)])
    await db.projects.create_index([("is_test", 1), ("industry", 1), ("title", 1)])

    await db.inquiries.update_many(
        {
            "name": {"$regex": "^TEST "},
            "company": {"$in": ["QA", "QA Co", "QA Corp"]},
        },
        {"$set": {"record_type": "inquiry", "is_test": True, "is_legitimate": False}},
    )
    await db.projects.update_many(
        {"title": {"$regex": "^TEST "}, "industry": "QA"},
        {"$set": {"is_test": True}},
    )
    test_projects = await db.projects.find({"is_test": True}, {"_id": 0, "cover_image": 1}).to_list(100)
    for project in test_projects:
        media_id = project.get("cover_image", "").rsplit("/", 1)[-1]
        try:
            await db.media_files.update_one(
                {"_id": ObjectId(media_id)},
                {"$set": {"is_test": True}},
            )
        except InvalidId:
            continue

    admin_email = os.environ["ADMIN_EMAIL"].lower()
    admin_password = os.environ["ADMIN_PASSWORD"]
    existing_admin = await db.users.find_one({"email": admin_email})
    password_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
    admin_document = {
        "name": os.environ["ADMIN_NAME"],
        "email": admin_email,
        "password_hash": password_hash,
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if existing_admin is None:
        await db.users.insert_one(admin_document)
    elif not bcrypt.checkpw(admin_password.encode(), existing_admin["password_hash"].encode()):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": password_hash}},
        )

    if await db.projects.count_documents({}) == 0:
        await db.projects.insert_one(
            {
                "title": "Tripura Darpan",
                "slug": "tripura-darpan",
                "industry": "Regional media",
                "year": "2025",
                "featured": True,
                "live_url": "https://tripuradarpan.com/",
                "summary": (
                    "A digital presence project for a regional media platform, "
                    "designed to make local stories clear, fast, and accessible."
                ),
                "challenge": "Present timely local reporting in a focused digital experience.",
                "solution": "A structured editorial experience with responsive reading flows.",
                "results": "A scalable foundation ready for evolving regional coverage.",
                "technologies": ["Responsive UI", "Performance", "SEO-ready structure"],
                "cover_image": (
                    "https://images.unsplash.com/photo-1597672996375-4d21cad0cbb9?"
                    "auto=format&fit=crop&w=1600&q=85"
                ),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    if await db.feed_posts.count_documents({}) == 0:
        await db.feed_posts.insert_many(
            [
                {
                    "title": "A clearer path from first click to real conversation.",
                    "tag": "Perspective",
                    "date": "Today",
                    "excerpt": "The best digital experiences earn attention by respecting it.",
                },
                {
                    "title": "Design systems are a growth decision.",
                    "tag": "Studio note",
                    "date": "This week",
                    "excerpt": "Consistency makes every future launch faster and more recognisable.",
                },
            ]
        )

    if await db.blog_posts.count_documents({}) == 0:
        await db.blog_posts.insert_many(
            [
                {
                    "title": "What a growth-ready website actually needs",
                    "category": "Business Growth",
                    "excerpt": "A practical view of the systems behind a website that keeps working.",
                    "status": "published",
                    "published_at": "2026-03-01",
                },
                {
                    "title": "Building trust before the first sales call",
                    "category": "Branding",
                    "excerpt": "The high-signal decisions that make an emerging brand feel established.",
                    "status": "published",
                    "published_at": "2026-02-20",
                },
            ]
        )

    public_settings = {
        "key": "public",
        "hero": {
            "eyebrow": "Qwebliq LLP · Crafted for Growth",
            "headline": "Building digital experiences that move businesses.",
            "description": (
                "Qwebliq creates premium websites, powerful brands, and digital strategies "
                "that help businesses stand out, generate leads, and increase sales."
            ),
        },
        "services": [
            {
                "name": "Digital foundations",
                "detail": "Websites, product experiences, and distinctive digital homes.",
            },
            {
                "name": "Brand systems",
                "detail": "Identity, direction, and design systems made to stay coherent.",
            },
            {
                "name": "Commerce & platforms",
                "detail": "E-commerce, portals, operations, and conversion-focused flows.",
            },
            {
                "name": "Social media marketing",
                "detail": (
                    "Content direction, platform strategy, community management, and "
                    "performance-led campaigns."
                ),
            },
            {
                "name": "Growth & visibility",
                "detail": "SEO, performance, social, and practical digital momentum.",
            },
        ],
        "calculator": {
            "base_prices": {
                "website": 65000,
                "ecommerce": 120000,
                "brand": 45000,
                "growth": 35000,
                "social": 30000,
            },
            "per_page": 4500,
            "rush_multiplier": 1.25,
        },
        "pricing": [
            {"name": "Growth website", "starting_at": 65000, "note": "Strategy, UX, design"},
            {"name": "Social media marketing", "starting_at": 30000, "note": "Monthly channel plan"},
        ],
        "contact": {
            "phones": ["+91 97740 90507", "+91 93628 23252"],
            "email": "qwebliqofficial@gmail.com",
            "instagram": "https://www.instagram.com/qwebliq",
        },
        "founders": [
            {
                "name": "Smaranjit Saha",
                "role": "Co-Founder & Creative Director",
                "focus": ["Creative direction", "UI/UX", "Brand strategy"],
            },
            {
                "name": "Diganta Bhowmik",
                "role": "Co-Founder & Technical Director",
                "focus": ["Development", "Architecture", "Scalable systems"],
            },
        ],
    }
    await db.site_settings.update_one(
        {"key": "public"},
        {"$setOnInsert": public_settings},
        upsert=True,
    )
    current_settings = await db.site_settings.find_one({"key": "public"}, {"_id": 0})
    if "founders" not in current_settings:
        await db.site_settings.update_one(
            {"key": "public"},
            {"$set": {"founders": public_settings["founders"]}},
        )
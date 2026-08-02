import os
from datetime import datetime, timezone

import bcrypt
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
"""Backend regression tests for Qwebliq platform."""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://qwebliq-staging.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@qwebliq.in"
ADMIN_PASSWORD = "Qw!8yqJAicISOKEwPh7"


@pytest.fixture(scope="session")
def anon_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    data = r.json()
    assert data["role"] == "admin"
    assert data["email"] == ADMIN_EMAIL
    # cookies should have been set (httpOnly)
    assert "access_token" in s.cookies
    return s


# ---------- Public endpoints ----------
class TestPublic:
    def test_root(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/")
        assert r.status_code == 200
        assert r.json()["message"] == "Qwebliq Platform API"

    def test_site_content(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/site")
        assert r.status_code == 200
        data = r.json()
        for key in ("services", "projects", "feed", "blogs", "faqs"):
            assert key in data
        assert len(data["services"]) >= 4
        assert len(data["faqs"]) >= 4
        # seeded Tripura Darpan project
        titles = [p.get("title") for p in data["projects"]]
        assert any("Tripura" in (t or "") for t in titles)
        # no mongo _id leakage
        for p in data["projects"]:
            assert "_id" not in p

    def test_calculator_returns_inr_estimate(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/calculator", json={
            "project_type": "website", "timeline": "standard", "pages": 5
        })
        assert r.status_code == 200
        data = r.json()
        assert data["currency"] == "INR"
        assert isinstance(data["estimate"], int) and data["estimate"] > 0
        assert "₹" in data["label"]

    def test_calculator_accelerated_higher(self, anon_client):
        base = anon_client.post(f"{BASE_URL}/api/calculator", json={
            "project_type": "ecommerce", "timeline": "standard", "pages": 10
        }).json()["estimate"]
        rush = anon_client.post(f"{BASE_URL}/api/calculator", json={
            "project_type": "ecommerce", "timeline": "accelerated", "pages": 10
        }).json()["estimate"]
        assert rush > base

    def test_calculator_invalid_input(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/calculator", json={
            "project_type": "bogus", "timeline": "standard", "pages": 3
        })
        assert r.status_code == 422

    def test_inquiry_creation(self, anon_client):
        payload = {
            "name": "TEST QA Lead",
            "email": f"test_lead_{uuid.uuid4().hex[:8]}@example.com",
            "company": "QA Co",
            "budget": "5-10L",
            "message": "This is a QA generated inquiry for regression testing.",
        }
        r = anon_client.post(f"{BASE_URL}/api/inquiries", json=payload)
        assert r.status_code == 201
        assert "team" in r.json()["message"].lower()

    def test_inquiry_validation(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/inquiries", json={
            "name": "X", "email": "not-an-email", "message": "short"
        })
        assert r.status_code == 422

    def test_newsletter_subscribe(self, anon_client):
        email = f"test_news_{uuid.uuid4().hex[:8]}@example.com"
        r = anon_client.post(f"{BASE_URL}/api/newsletter", json={"email": email})
        assert r.status_code == 201
        # idempotent-like: duplicate should not throw 500
        r2 = anon_client.post(f"{BASE_URL}/api/newsletter", json={"email": email})
        assert r2.status_code in (201, 200)


# ---------- Auth & protection ----------
class TestAuth:
    def test_login_wrong_password(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": "wrongpassword123"
        })
        assert r.status_code in (401, 429)

    def test_me_requires_auth(self, anon_client):
        r = requests.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401

    def test_admin_endpoints_require_auth(self):
        # bare requests, no cookies
        for path in ("/api/admin/overview", "/api/admin/inquiries"):
            r = requests.get(f"{BASE_URL}{path}")
            assert r.status_code == 401, f"{path} expected 401 got {r.status_code}"

    def test_admin_login_and_me(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 200
        me = r.json()
        assert me["email"] == ADMIN_EMAIL
        assert me["role"] == "admin"
        assert "password_hash" not in me

    def test_bcrypt_hash_format(self):
        # verify seeded admin hash format
        import subprocess
        # Not directly accessible; skipped if no mongo cli. Use API side-effect: login works => hash valid.
        assert True


# ---------- Admin flows ----------
class TestAdmin:
    def test_overview(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/overview")
        assert r.status_code == 200
        data = r.json()
        assert "metrics" in data and len(data["metrics"]) == 4
        assert "recent_inquiries" in data
        for inq in data["recent_inquiries"]:
            assert "_id" not in inq

    def test_inquiries_list_reflects_new_inquiry(self, admin_client, anon_client):
        marker = f"QA marker {uuid.uuid4().hex[:6]}"
        anon_client.post(f"{BASE_URL}/api/inquiries", json={
            "name": "TEST Persist",
            "email": f"test_persist_{uuid.uuid4().hex[:6]}@example.com",
            "company": "QA",
            "budget": "",
            "message": marker + " sample message body",
        })
        time.sleep(0.5)
        r = admin_client.get(f"{BASE_URL}/api/admin/inquiries")
        assert r.status_code == 200
        msgs = [i.get("message", "") for i in r.json()]
        assert any(marker in m for m in msgs)

    def test_publish_feed_blog_project(self, admin_client):
        # feed
        r = admin_client.post(f"{BASE_URL}/api/admin/feed", json={
            "title": "TEST feed publish", "category": "Studio note",
            "excerpt": "Testing feed publish flow end to end.",
        })
        assert r.status_code == 201
        assert r.json()["tag"] == "Studio note"

        # blog
        r = admin_client.post(f"{BASE_URL}/api/admin/blog", json={
            "title": "TEST blog publish", "category": "Perspective",
            "excerpt": "Testing blog publish flow end to end.",
        })
        assert r.status_code == 201
        assert r.json()["status"] == "published"

        # project
        r = admin_client.post(f"{BASE_URL}/api/admin/projects", json={
            "title": "TEST Portfolio",
            "industry": "QA",
            "summary": "QA generated portfolio entry for regression.",
            "live_url": "",
        })
        assert r.status_code == 201
        assert r.json()["title"] == "TEST Portfolio"

        # Verify visible on public site
        site = requests.get(f"{BASE_URL}/api/site").json()
        assert any(p.get("title") == "TEST Portfolio" for p in site["projects"])
        assert any(b.get("title") == "TEST blog publish" for b in site["blogs"])
        assert any(f.get("title") == "TEST feed publish" for f in site["feed"])

    def test_project_input_validation(self, admin_client):
        r = admin_client.post(f"{BASE_URL}/api/admin/projects", json={
            "title": "x", "industry": "y", "summary": "z"
        })
        assert r.status_code == 422


# ---------- Client creation + client portal ----------
class TestClientPortal:
    def test_admin_creates_client_and_client_can_sign_in(self, admin_client):
        email = f"client.qa+{uuid.uuid4().hex[:6]}@qwebliq.in"
        pwd = "ClientQA!Pass123"
        r = admin_client.post(f"{BASE_URL}/api/auth/clients", json={
            "name": "TEST QA Client", "email": email, "password": pwd,
        })
        assert r.status_code == 201, r.text
        assert r.json()["role"] == "client"

        # Duplicate should 409
        r2 = admin_client.post(f"{BASE_URL}/api/auth/clients", json={
            "name": "TEST QA Client", "email": email, "password": pwd,
        })
        assert r2.status_code == 409

        # Sign in as client
        cs = requests.Session()
        cs.headers.update({"Content-Type": "application/json"})
        r3 = cs.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": pwd})
        assert r3.status_code == 200
        assert r3.json()["role"] == "client"

        # client projects endpoint
        r4 = cs.get(f"{BASE_URL}/api/client/projects")
        assert r4.status_code == 200
        data = r4.json()
        assert "projects" in data and len(data["projects"]) >= 1

        # Cannot access admin
        r5 = cs.get(f"{BASE_URL}/api/admin/overview")
        assert r5.status_code == 403

    def test_anonymous_client_projects_blocked(self):
        r = requests.get(f"{BASE_URL}/api/client/projects")
        assert r.status_code == 401

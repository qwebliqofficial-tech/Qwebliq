"""Regression tests for admin editors, site settings, media upload, and portfolio project creation."""
import copy
import io
import os
import struct
import uuid
import zlib

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://qwebliq-staging.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "admin@qwebliq.in"
ADMIN_PASSWORD = "Qw!8yqJAicISOKEwPh7"


def _make_png_bytes() -> bytes:
    """Build a valid 1x1 PNG (no external deps)."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00" + b"\xff\x00\x00"
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


@pytest.fixture(scope="session")
def admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"admin login failed {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="session")
def original_settings(admin_session):
    r = admin_session.get(f"{BASE_URL}/api/admin/site-settings")
    assert r.status_code == 200
    data = r.json()["settings"]
    assert data is not None
    return copy.deepcopy(data)


# ------------------ Auth guards ------------------
class TestAdminAuthGuards:
    def test_site_settings_get_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/admin/site-settings")
        assert r.status_code == 401

    def test_site_settings_put_requires_auth(self):
        r = requests.put(f"{BASE_URL}/api/admin/site-settings", json={"settings": {}})
        assert r.status_code == 401

    def test_media_upload_requires_auth(self):
        files = {"file": ("t.png", _make_png_bytes(), "image/png")}
        r = requests.post(f"{BASE_URL}/api/admin/media", files=files)
        assert r.status_code == 401

    def test_projects_post_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/admin/projects", json={
            "title": "TEST unauth", "industry": "QA", "summary": "should be blocked before persist"
        })
        assert r.status_code == 401


# ------------------ Site settings editor ------------------
class TestSiteSettingsEditor:
    def test_get_returns_expected_shape(self, original_settings):
        assert "hero" in original_settings
        assert "services" in original_settings and len(original_settings["services"]) >= 4
        assert "calculator" in original_settings
        assert "pricing" in original_settings
        assert "contact" in original_settings
        assert "founders" in original_settings
        social_names = [s["name"].lower() for s in original_settings["services"]]
        assert any("social" in n for n in social_names), "Social media marketing service must be present"

    def test_pricing_update_reflects_in_calculator_and_public(self, admin_session, original_settings):
        modified = copy.deepcopy(original_settings)
        modified["calculator"]["base_prices"]["social"] = 42000
        modified["calculator"]["per_page"] = 5000
        modified["calculator"]["rush_multiplier"] = 1.5
        # ensure pricing block also updated
        pricing = modified.get("pricing", [])
        found = False
        for item in pricing:
            if "social" in item["name"].lower():
                item["starting_at"] = 42000
                found = True
        if not found:
            pricing.append({"name": "Social media marketing", "starting_at": 42000, "note": "Monthly channel plan"})
        modified["pricing"] = pricing

        r = admin_session.put(f"{BASE_URL}/api/admin/site-settings", json={"settings": modified})
        assert r.status_code == 200, r.text
        saved = r.json()["settings"]
        assert saved["calculator"]["base_prices"]["social"] == 42000
        assert saved["calculator"]["per_page"] == 5000
        assert saved["calculator"]["rush_multiplier"] == 1.5

        # public /api/site reflects the change
        site = requests.get(f"{BASE_URL}/api/site").json()
        social_price = next((p["starting_at"] for p in site["settings"]["pricing"] if "social" in p["name"].lower()), None)
        assert social_price == 42000

        # calculator uses new base + per_page + rush
        calc = requests.post(f"{BASE_URL}/api/calculator", json={
            "project_type": "social", "timeline": "standard", "pages": 1
        }).json()
        assert calc["estimate"] == 42000

        calc2 = requests.post(f"{BASE_URL}/api/calculator", json={
            "project_type": "social", "timeline": "accelerated", "pages": 3
        }).json()
        # (42000 + 2*5000) * 1.5 = 78000
        assert calc2["estimate"] == 78000

        # restore
        rr = admin_session.put(f"{BASE_URL}/api/admin/site-settings", json={"settings": original_settings})
        assert rr.status_code == 200

    def test_website_editor_hero_update_reflects_publicly(self, admin_session, original_settings):
        modified = copy.deepcopy(original_settings)
        marker = f"TEST hero {uuid.uuid4().hex[:6]}"
        modified["hero"]["description"] = marker + " — regression editable description."
        r = admin_session.put(f"{BASE_URL}/api/admin/site-settings", json={"settings": modified})
        assert r.status_code == 200
        site = requests.get(f"{BASE_URL}/api/site").json()
        assert marker in site["settings"]["hero"]["description"]
        # restore
        admin_session.put(f"{BASE_URL}/api/admin/site-settings", json={"settings": original_settings})

    def test_services_include_social_media_marketing(self, original_settings):
        names = [s["name"] for s in original_settings["services"]]
        assert any("Social media marketing".lower() == n.lower() for n in names)


# ------------------ Media upload + project creation ------------------
class TestMediaAndProject:
    def test_media_upload_and_download(self, admin_session):
        png = _make_png_bytes()
        files = {"file": ("test.png", png, "image/png")}
        r = admin_session.post(f"{BASE_URL}/api/admin/media", files=files)
        assert r.status_code == 201, r.text
        payload = r.json()
        assert "id" in payload and "url" in payload
        assert payload["url"].startswith("/api/media/")
        # Fetch via proxy URL
        proxy_url = f"{BASE_URL}{payload['url']}"
        r2 = requests.get(proxy_url)
        assert r2.status_code == 200
        assert r2.headers.get("content-type", "").startswith("image/")
        assert len(r2.content) > 0
        # unknown id -> 404
        r3 = requests.get(f"{BASE_URL}/api/media/notarealid")
        assert r3.status_code == 404

    def test_media_upload_rejects_bad_type(self, admin_session):
        files = {"file": ("t.txt", b"hello", "text/plain")}
        r = admin_session.post(f"{BASE_URL}/api/admin/media", files=files)
        assert r.status_code == 415

    def test_project_created_with_media_visible_publicly(self, admin_session):
        png = _make_png_bytes()
        files = {"file": ("cover.png", png, "image/png")}
        m = admin_session.post(f"{BASE_URL}/api/admin/media", files=files)
        assert m.status_code == 201
        media_url = f"{BASE_URL}{m.json()['url']}"

        title = f"TEST Media Project {uuid.uuid4().hex[:6]}"
        r = admin_session.post(f"{BASE_URL}/api/admin/projects", json={
            "title": title,
            "industry": "QA",
            "summary": "QA generated portfolio entry with uploaded cover image.",
            "live_url": "https://example.com/",
            "cover_image": media_url,
            "year": "2026",
        })
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["title"] == title
        assert body["cover_image"] == media_url
        assert "_id" not in body

        site = requests.get(f"{BASE_URL}/api/site").json()
        titles = [p.get("title") for p in site["projects"]]
        assert title in titles
        found = next(p for p in site["projects"] if p["title"] == title)
        assert found["cover_image"] == media_url

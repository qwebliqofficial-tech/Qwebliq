import os
import uuid
from threading import Lock

import requests

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
APP_PREFIX = "qwebliq"
storage_key: str | None = None
storage_lock = Lock()


def init_storage() -> str:
    global storage_key
    if storage_key:
        return storage_key
    with storage_lock:
        if storage_key:
            return storage_key
        response = requests.post(
            f"{STORAGE_URL}/init",
            json={"emergent_key": os.environ["EMERGENT_LLM_KEY"]},
            timeout=30,
        )
        response.raise_for_status()
        storage_key = response.json()["storage_key"]
        return storage_key


def upload_media(data: bytes, content_type: str, extension: str) -> dict:
    path = f"{APP_PREFIX}/portfolio/{uuid.uuid4()}.{extension}"
    response = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": init_storage(), "Content-Type": content_type},
        data=data,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def download_media(path: str) -> tuple[bytes, str]:
    response = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": init_storage()},
        timeout=60,
    )
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "application/octet-stream")
    return response.content, content_type


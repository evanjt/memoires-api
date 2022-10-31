import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Tuple, Dict
from app.config import settings


def test_add_get_photo(
    client: TestClient,
    testimage: Dict[str, Tuple[bytes, str, str]]
) -> None:
    ''' Upload a test file, then retrieve its metadata '''

    res = client.post(
        f"{settings.API_V1_STR}/photos",
        files=testimage
    )

    uploaded = res.json()
    assert uploaded.get('duplicate') == False, "Image marked as duplicate"

    res = client.get(
        f"{settings.API_V1_STR}/photos/{uploaded['uuid']}/metadata"
    )

    retrieved = res.json()
    assert retrieved['original'] == uploaded['original']
    assert retrieved['thumbnail'] == uploaded['thumbnail']

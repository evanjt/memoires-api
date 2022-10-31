import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Tuple
from app.config import settings


def test_add_photo(
    client: TestClient,
    testimage: Tuple[bytes, str, str]
) -> None:
    res = client.post(
        f"{settings.API_V1_STR}/photos",
        files=testimage)

    assert res.json().get('duplicate') == False, "Image marked as duplicate"

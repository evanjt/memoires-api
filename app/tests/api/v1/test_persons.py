from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.api.v1.schemas.person import PersonCreate


def test_create_person(
    client: TestClient,
    #superuser_token_headers: dict,
    db: Session
) -> None:

    data = {"email": 'user@domain.com', 
            "first_names": "Steve",
            "last_names": "Johnston"}

    r = client.post(
        f"{settings.API_V1_STR}/persons",
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_person = r.json()

    assert created_person["first_names"] == data["first_names"]
    assert created_person["last_names"] == data["last_names"]
    assert created_person["email"] == data["email"]


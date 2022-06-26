from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.api.deps import get_db


@pytest.fixture(scope="session")
def db() -> Generator:
    engine = create_engine(
        "sqlite:///",
        echo=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False})

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def client(db: Session) -> Generator:
    def override_get_db() -> Generator:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

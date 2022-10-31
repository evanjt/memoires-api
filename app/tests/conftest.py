from typing import Dict, Generator
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.api.dependencies import get_db, get_minio
from moto import mock_s3
from minio import Minio
import boto3

from app.config import settings


ASSETS_PATH = os.path.join(
    os.getcwd(), 
    'app', 
    'tests', 
    'assets', 
), 


@pytest.fixture(scope="session")
def db() -> Generator:
    engine = create_engine(
        "sqlite:///",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False})

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def client(db: Session) -> Generator:
    def override_get_db() -> Generator:
        yield db

    def override_minio() -> Generator:
        with mock_s3():
            conn = boto3.resource('s3', region_name='us-east-1')
            
            return conn
            minio = Minio(
                f"{settings.MINIO_ADDR}:{settings.MINIO_PORT}",
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_ACCESS_PASSWORD,
                secure=False
            )
            return minio
        
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_minio] = override_minio

    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def testimage() -> bytes:
    with open(os.path.join(
        os.getcwd(), 
        'app', 
        'tests', 
        'assets', 
        '2022-07-27 10.52.21.jpg'
    ), 'rb') as imgfile:
        img = imgfile.read()
    
    return img

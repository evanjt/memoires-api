from typing import Generator
from pydantic import ValidationError
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from minio import Minio

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# # Minio dependency
# minio = Minio(
#     f"{settings.MINIO_ADDR}:{settings.MINIO_PORT}",
#     access_key=settings.MINIO_ACCESS_KEY,
#     secret_key=settings.MINIO_ACCESS_PASSWORD,
#     secure=False
# )

# async def get_minio() -> Minio:
#     return minio

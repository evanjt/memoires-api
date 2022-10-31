from typing import Generator
from pydantic import ValidationError
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from minio import Minio
import boto3
from aiobotocore.session import AioSession

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# minio = Minio(
#     f"{settings.MINIO_ADDR}:{settings.MINIO_PORT}",
#     access_key=settings.MINIO_ACCESS_KEY,
#     secret_key=settings.MINIO_ACCESS_PASSWORD,
#     secure=False
# )

minio = boto3.resource(
    's3', 
    endpoint_url="{ssl}://{address}:{port}".format(
        ssl='https' if settings.MINIO_SSL == True else 'http',
        address=settings.MINIO_ADDR,
        port=settings.MINIO_PORT
    ),
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_ACCESS_PASSWORD,
    aws_session_token=None,
    config=boto3.session.Config(signature_version='s3v4'),
    verify=False
    )


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_minio() -> Minio:
    session = AioSession()

    async with AsyncExitStack() as exit_stack:
        s3_client = await create_s3_client(session, exit_stack)
        return s3_client

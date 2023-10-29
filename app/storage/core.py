from app.config import settings
from minio import Minio

# Minio dependency
minio = Minio(
    f"{settings.MINIO_ADDR}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_ACCESS_PASSWORD,
    secure=False
)

async def get_minio() -> Minio:
    return minio

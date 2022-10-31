from typing import Dict, Generator, Tuple
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.api.dependencies import minio
from app.config import settings
from app.api.dependencies import engine


@pytest.fixture(scope="module")
def client() -> Generator:
    # Drop then create tables on PostgreSQL (Drop first in case tests fail
    # previously and aren't collected in the start up metadata)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Create the bucket if it's not there
    if not minio.bucket_exists(settings.MINIO_BUCKET):
        minio.make_bucket(settings.MINIO_BUCKET)

    with TestClient(app) as c:
        yield c

    # Cleanup MinIO
    memoire_objs = minio.list_objects(settings.MINIO_BUCKET, recursive=True)
    for obj in memoire_objs:
        minio.remove_object(settings.MINIO_BUCKET, obj.object_name)
    minio.remove_bucket(settings.MINIO_BUCKET)


@pytest.fixture(scope="module")
def testimage() -> Dict[str, Tuple[str, bytes, str]]:
    filename = "2022-07-27 10.52.21.jpg"
    mimetype = 'image/png'
    with open(os.path.join(
        os.getcwd(),
        'app',
        'tests',
        'assets',
        filename
    ), 'rb') as imgfile:
        img = imgfile.read()

    return {"file": (filename, img, mimetype)}

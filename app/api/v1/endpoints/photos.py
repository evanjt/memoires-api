from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, models
from app.api.dependencies import get_db, get_minio
from app.api.v1 import schemas
from minio import Minio
from uuid import uuid4
from PIL import Image
from app.config import settings
import io

router = APIRouter()


@router.post("")
def upload_photo(
    file: UploadFile = File(...),
    *,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio),
) -> List[schemas.EventRead]:

    contents = io.BytesIO(file.file.read())
    
    # Store original
    res = minio.put_object(
        bucket_name='memoires', 
        object_name=uuid4().hex,
        data=contents,
        length=contents.getbuffer().nbytes)

    contents.seek(0)
    output = io.BytesIO()    
    with Image.open(contents) as img:
        img.thumbnail(settings.MAX_THUMBNAIL_SIZE)
        img.save(output, format="JPEG")
        
        output.seek(0)
        thumbres = minio.put_object(
            bucket_name='memoires', 
            object_name=uuid4().hex,
            data=output,
            length=output.getbuffer().nbytes)

    return {'original': res.object_name,
            'thumbnail': thumbres.object_name}

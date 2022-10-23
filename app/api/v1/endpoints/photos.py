from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Request, status)
from sqlalchemy.orm import Session
from typing import Any, Generator, Dict
from app.api.dependencies import get_db, get_minio
from minio import Minio
from minio.error import S3Error
from uuid import uuid4
from PIL import Image, ExifTags, TiffImagePlugin
from app.config import settings
import io
import json
from pydantic import BaseModel, UUID4, Extra
from app.models.photo import Photo
from enum import Enum

router = APIRouter()


ExifEnum = Enum(
    "ExifEnum",
    list(set([(x, x) for x in ExifTags.TAGS.values()]))
)


class PhotoAdd(BaseModel, extra=Extra.allow):
    image: UUID4
    thumbnail: UUID4
    exif: Dict[ExifEnum, Any]


def add_new(
    db: Session,
    image: UUID4,
    thumbnail: UUID4,
) -> Photo:
    photo = Photo(
        image=image,
        thumbnail=thumbnail
    )

    db.add(photo)
    db.commit()
    db.refresh(photo)

    return photo


def get_image_data(
    minio: Minio,
    image_uuid: UUID4
) -> Generator:
    try:
        res = minio.get_object(
            bucket_name='memoires',
            object_name=image_uuid.replace('-', '')
        )
        with Image.open(res) as img:
            return img
    except S3Error as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    finally:
        res.close()
        res.release_conn()


def get_exif(
    *,
    request: Request,
    minio: Minio = Depends(get_minio),
    # image_uuid: UUID4
) -> Dict[ExifEnum, Any]:

    def ifd_rational_serializer(value):
        if isinstance(value, TiffImagePlugin.IFDRational):
            return float(value)

    exif_data = {}
    exif_data["GPSInfo"] = {}
    img = get_image_data(minio, request.path_params["image_uuid"])

    exif = img._getexif()
    for k, v in exif.items():
        # Convert a byte string from hex to string
        try:
            str_value = v.hex()
        except Exception:
            str_value = v

        if k in ExifTags.TAGS:
            if ExifTags.TAGS[k] == "GPSInfo":
                for gpsk, gpsv in str_value.items():
                    if gpsk in ExifTags.GPSTAGS:
                        exif_data["GPSInfo"][ExifTags.GPSTAGS[gpsk]] = gpsv
                    else:
                        exif_data["GPSInfo"][gpsk] = gpsv
            else:
                exif_data[ExifTags.TAGS[k]] = str_value
        else:
            exif_data[k] = str_value

    # Serialise the dictionary before returning it as Dict again
    serialised_obj = json.dumps(
        exif_data,
        default=ifd_rational_serializer)

    return json.loads(serialised_obj)


def get_metadata(
    *,
    request: Request,
    db: Session = Depends(get_db),
) -> Photo:
    try:
        return db.query(Photo).filter(
            Photo.image == request.path_params["image_uuid"]).one_or_none()
    except S3Error as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get("/{image_uuid}", response_model=PhotoAdd)
def get_image_metadata(
    *,
    image_uuid: UUID4,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio),
    photo_metadata: Photo = Depends(get_metadata),
    exif: PhotoAdd = Depends(get_exif),
):

    return PhotoAdd(
        image=photo_metadata.image,
        thumbnail=photo_metadata.thumbnail,
        exif=exif
    )


@router.post("")
def upload_photo(
    file: UploadFile = File(...),
    *,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio),
):

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

    photo = add_new(
        db=db,
        image=res.object_name,
        thumbnail=thumbres.object_name
    )

    return PhotoAdd(
        image=photo.image,
        thumbnail=photo.thumbnail
    )

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Request, status,
    Query, Path)
from fastapi.responses import Response, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Any, Generator, Dict, Tuple
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
from fastapi.exceptions import RequestValidationError
from enum import Enum
import datetime
import hashlib

router = APIRouter()


ExifEnum = Enum(
    "ExifEnum",
    list(set([(x, x) for x in ExifTags.TAGS.values()]))
)


class PhotoTime(BaseModel):
    camera: datetime.datetime | None = None
    gps: datetime.datetime | None = None
    validated: datetime.datetime | None = None

class PhotoBase(BaseModel):
    original: UUID4
    thumbnail: UUID4
    time: PhotoTime
    content_type: str

class PhotoAdd(PhotoBase, extra=Extra.allow):
    exif: Dict[ExifEnum, Any] | None

class PhotoRead(PhotoBase, extra=Extra.allow):
    uuid: UUID4
    exif: Dict[ExifEnum, Any] | None
    duplicate: bool


def add_new(
    db: Session,
    original: UUID4,
    thumbnail: UUID4,
    content_type: str,
    checksum: str,
    camera_time: datetime.datetime | None = None,
    gps_time: datetime.datetime | None = None,
    validated_time: datetime.datetime | None = None,
) -> Photo:

    photo = Photo(
        uuid=uuid4(),   # Generate a new UUID
        original=original,    # The UUID of the original
        thumbnail=thumbnail,
        content_type=content_type,
        camera_time=camera_time,
        gps_time=gps_time,
        validated_time=validated_time,
        checksum_blake2=checksum,
    )

    db.add(photo)
    db.commit()
    db.refresh(photo)

    return photo


def get_image(
    minio: Minio,
    image_uuid: UUID4
) -> Image:
    ''' Works with either an original or the thumbnail uuid '''
    res = minio.get_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=image_uuid
    )

    return Image.open(res)


def get_exif(
    img: Image,
) -> Dict[ExifEnum, Any]:

    def ifd_rational_serializer(value):
        if isinstance(value, TiffImagePlugin.IFDRational):
            return float(value)

    exif_data = {}
    exif_data["GPSInfo"] = {}

    exif = img._getexif()
    if exif:
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


def get(
    *,
    request: Request,
    db: Session = Depends(get_db),
) -> Photo:

    return db.query(Photo).filter(
        Photo.uuid == request.path_params["photo_uuid"]).one()


def get_from_checksum(
    db: Session,
    checksum: str,
) -> Photo:

    return db.query(Photo).filter(
        Photo.checksum_blake2 == checksum).one_or_none()


def get_time_taken(
    exif: Dict[ExifEnum, Any],
) -> Tuple[datetime.datetime, datetime.datetime] | Tuple[None, None]:
    ''' Attempts to get the correct date that the image was taken '''

    time = None
    gpstime = None

    gps_data = exif.get('GPSInfo')
    if gps_data:
        if gps_data.get('GPSTimeStamp') and gps_data.get('GPSDateStamp'):
            hour, minute, second = list(map(int, gps_data['GPSTimeStamp']))
            year, month, day = list(map(int, gps_data['GPSDateStamp'].split(":")))

            gpstime = datetime.datetime(year, month, day, hour, minute, second,
                                        tzinfo=datetime.timezone.utc)

    if exif.get('DateTimeOriginal'):
        time = datetime.datetime.strptime(
            exif.get('DateTimeOriginal'),
            '%Y:%m:%d %H:%M:%S'
        )


    return time, gpstime


@router.get("/{photo_uuid}/metadata", response_model=PhotoAdd)
def get_metadata(
    *,
    photo_uuid: UUID4,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio),
    photo: Photo = Depends(get),
):
    exif = get_exif(get_image(minio, photo.original.hex))

    return PhotoAdd(
        original=photo.original,
        thumbnail=photo.thumbnail,
        content_type=photo.content_type,
        time=PhotoTime(
            camera=photo.camera_time,
            gps=photo.gps_time,
            validated=photo.validated_time,
            ),
        exif=exif
    )

@router.get("/{photo_uuid}")
def get_photo_image(
    *,
    photo_uuid: UUID4,
    thumbnail: bool = Query(False, title="Get thumbnail"),
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio),
    photo: Photo = Depends(get),
):
    if thumbnail:
        res = minio.get_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=photo.thumbnail.hex
        )
        return StreamingResponse(res.stream(), media_type='image/jpeg')
    else:
        res = minio.get_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=photo.original.hex
        )
        return StreamingResponse(res.stream(), media_type=photo.content_type)



@router.post("", response_model=PhotoRead)
def upload_photo(
    file: UploadFile = File(...),
    *,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio),
) -> PhotoAdd:

    contents = io.BytesIO(file.file.read())
    print(file.content_type)
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "This endpoint only receives images"
    )

    # Generate checksum
    contents.seek(0)
    checksum = hashlib.blake2b(contents.getbuffer()).hexdigest()

    # Get the uploaded image by checksum. Prevents duplicates
    photo = get_from_checksum(db, checksum)
    duplicate = True if photo else False

    if photo is None:
        # Store original
        contents.seek(0)
        res = minio.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=uuid4().hex,
            data=contents,
            length=contents.getbuffer().nbytes)

        # Create and store a thumbnail
        contents.seek(0)
        output = io.BytesIO()
        with Image.open(contents) as img:
            img.thumbnail(settings.MAX_THUMBNAIL_SIZE)
            img.save(output, format="JPEG")

            output.seek(0)
            thumbres = minio.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=uuid4().hex,
                data=output,
                length=output.getbuffer().nbytes)

        exif = get_exif(get_image(minio, res.object_name))

        camera_time, gps_time = get_time_taken(exif)

        photo = add_new(
            db=db,
            original=res.object_name,
            thumbnail=thumbres.object_name,
            content_type=file.content_type,
            camera_time=camera_time,
            gps_time=gps_time,
            checksum=checksum,
        )

    else:
        # Get exif again (incase of duplicate) -- temporarily
        exif = get_exif(get_image(minio, photo.original.hex))

    return PhotoRead(
        uuid=photo.uuid,
        duplicate=duplicate,
        original=photo.original,
        thumbnail=photo.thumbnail,
        content_type=photo.content_type,
        time=PhotoTime(
            camera=photo.camera_time,
            gps=photo.gps_time,
            validated=photo.validated_time,
            ),
        exif=exif,
    )

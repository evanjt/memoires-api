from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.api.v1.routes import router
from app.config import settings
from app.api.dependencies import engine, get_db
from fastapi.exceptions import RequestValidationError
from minio.error import S3Error
from app.api.dependencies import minio
from sqlalchemy.exc import NoResultFound

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,
    redoc_url='/docs/'
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():

    Base.metadata.create_all(engine)

    # Create the bucket if it's not there
    if not minio.bucket_exists(settings.MINIO_BUCKET):
        minio.make_bucket(settings.MINIO_BUCKET)

app.include_router(router, prefix=settings.API_V1_STR)

@app.exception_handler(S3Error)
async def validation_exception_handler(request: Request,
                                       exc: S3Error):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.exception_handler(NoResultFound)
async def validation_exception_handler(request: Request,
                                       exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )

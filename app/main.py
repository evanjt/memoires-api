from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.api.v1.routes import router
from app.core.config import settings
from app.api.deps import engine

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

#@app.on_event("startup")
#async def startup_event():

    #Base.metadata.create_all(engine)

app.include_router(router, prefix=settings.API_V1_STR)

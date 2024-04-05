from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.events.views import router as events_router
from app.root.views import router as root_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    root_router,
    prefix=f"{config.API_V1_PREFIX}",
    tags=["root"],
)
app.include_router(
    events_router,
    prefix=f"{config.API_V1_PREFIX}/events",
    tags=["events"],
)

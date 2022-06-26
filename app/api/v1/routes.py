from fastapi import APIRouter

from app.api.v1.endpoints import events, persons

router = APIRouter()
router.include_router(persons.router, prefix="/persons", tags=["persons"])
router.include_router(events.router, prefix="/events", tags=["events"])

from fastapi import APIRouter

from app.api.v1.endpoints import events, persons, photos

router = APIRouter()
router.include_router(
    persons.router, 
    prefix="/persons", 
    tags=["Persons"]
)
router.include_router(
    events.router, 
    prefix="/events", 
    tags=["Events"]
)
router.include_router(
    photos.router, 
    prefix="/photos", 
    tags=["Photos"]
)

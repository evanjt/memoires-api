from fastapi import APIRouter

from app.api.v1.endpoints import items, persons

router = APIRouter()
router.include_router(persons.router, prefix="/persons", tags=["persons"])
router.include_router(items.router, prefix="/items", tags=["items"])

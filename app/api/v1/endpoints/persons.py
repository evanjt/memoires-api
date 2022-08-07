from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Query
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from typing import Optional
from sqlalchemy.orm import Session

from app import crud, models
from app.api.dependencies import get_db
from app.api.v1 import schemas
from app.config import settings

router = APIRouter()


@router.get("", response_model=List[schemas.PersonRead])
def read_persons(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    response: Response,
    filter: Optional[str] = Query(None),
    range: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
) -> List[schemas.PersonRead]:
    """ Retrieve persons """

    objs = crud.person.get_multi(db, skip=skip, limit=limit)

    response.headers["Content-Range"] = f"persons {skip}-{skip+limit}/{str(len(objs))}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    return objs


@router.post("", response_model=schemas.PersonRead)
def create_person(
    *,
    db: Session = Depends(get_db),
    person_in: schemas.PersonCreate,
) -> schemas.PersonRead:
    """ Create new person """

    person = crud.person.get_by_email(db, email=person_in.email)
    if person:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    person = crud.person.create(db, obj_in=person_in)

    return schemas.PersonRead(uuid=person.uuid,
                              first_names=person.first_names,
                              last_names=person.last_names,
                              email=person.email)

from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, models
from app.api.dependencies import get_db
from app.api.v1 import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.EventRead])
def read_events(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    response: Response,
    filter: Optional[str] = Query(None),
    range: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
) -> List[schemas.EventRead]:
    """ Retrieve persons """

    objs = crud.event.get_multi(db, skip=skip, limit=limit)

    response.headers["Content-Range"] = f"events {skip}-{skip+limit}/{str(len(objs))}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    return objs


@router.post("", response_model=schemas.EventRead)
def create_event(
    *,
    db: Session = Depends(get_db),
    item_in: schemas.EventCreate,
) -> schemas.EventRead:
    """ Create new event. """
    owner_id = crud.person.get_db_id(db, uuid=item_in.owner)

    event = crud.event.create_with_owner(db=db, obj_in=item_in,
                                         owner_id=owner_id)


    return schemas.EventRead(title=event.title,
                             description=event.description,
                             start_time=event.start_time,
                             end_time=event.end_time,
                             owner=schemas.PersonRead(
                                 uuid=event.owner.uuid,
                                 first_names=event.owner.first_names,
                                 last_names=event.owner.last_names,
                                 email=event.owner.email
                                 )
                             )


@router.get("/{id}", response_model=schemas.EventRead)
def read_event(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """ Get event by ID. """

    event = crud.event.get(db=db, id=id)
    if not event:
        raise HTTPException(status_code=404, detail="Item not found")

    return event


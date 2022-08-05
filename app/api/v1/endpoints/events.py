from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, models
from app.api.dependencies import get_db
from app.api.v1 import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.Event])
def read_events(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    response: Response,
    filter: Optional[str] = Query(None),
    range: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
) -> List[schemas.Event]:
    """ Retrieve persons """

    objs = crud.event.get_multi(db, skip=skip, limit=limit)

    response.headers["Content-Range"] = f"events {skip}-{skip+limit}/{str(len(objs))}"
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    return objs


@router.post("", response_model=schemas.Event)
def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: schemas.EventCreate,
    #current_user: models.User = Depends(deps.get_current_active_user),
) -> schemas.Event:
    """
    Create new event.
    """

    event = crud.event.create(db=db, obj_in=item_in,)
                                         #owner_id=current_user.id)
    return event


@router.get("/{id}", response_model=schemas.Event)
def read_item(
    *,
    db: Session = Depends(get_db),
    id: int,
    #current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """ Get event by ID. """

    event = crud.event.get(db=db, id=id)
    if not event:
        raise HTTPException(status_code=404, detail="Item not found")
    #if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        #raise HTTPException(status_code=400, detail="Not enough permissions")

    return event


#@router.post("", response_model=schemas.Event)
#def create_event(
    #event: EventCreate,
    #db: Session = Depends(deps.get_db),
#) -> schemas.Event:

    #obj = Event.from_orm(event)

    #person_list = []
    #if event.persons:
        #for person in event.persons:
            #person_list.append(session.get(Person, person))

    #obj.persons = person_list

    #session.add(obj)
    #session.commit()
    #session.refresh(obj)
    #return obj


#@router.get("/", response_model=List[schemas.Item])
#def read_items(
    #db: Session = Depends(deps.get_db),
    #skip: int = 0,
    #limit: int = 100,
    #current_user: models.User = Depends(deps.get_current_active_user),
#) -> Any:
    #"""
    #Retrieve items.
    #"""
    #if crud.user.is_superuser(current_user):
        #items = crud.item.get_multi(db, skip=skip, limit=limit)
    #else:
        #items = crud.item.get_multi_by_owner(
            #db=db, owner_id=current_user.id, skip=skip, limit=limit
        #)
    #return items




#@router.put("/{id}", response_model=schemas.Item)
#def update_item(
    #*,
    #db: Session = Depends(deps.get_db),
    #id: int,
    #item_in: schemas.ItemUpdate,
    #current_user: models.User = Depends(deps.get_current_active_user),
#) -> Any:
    #"""
    #Update an item.
    #"""
    #item = crud.item.get(db=db, id=id)
    #if not item:
        #raise HTTPException(status_code=404, detail="Item not found")
    #if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        #raise HTTPException(status_code=400, detail="Not enough permissions")
    #item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    #return item




#@router.delete("/{id}", response_model=schemas.Item)
#def delete_item(
    #*,
    #db: Session = Depends(deps.get_db),
    #id: int,
    #current_user: models.User = Depends(deps.get_current_active_user),
#) -> Any:
    #"""
    #Delete an item.
    #"""
    #item = crud.item.get(db=db, id=id)
    #if not item:
        #raise HTTPException(status_code=404, detail="Item not found")
    #if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        #raise HTTPException(status_code=400, detail="Not enough permissions")
    #item = crud.item.remove(db=db, id=id)
    #return item

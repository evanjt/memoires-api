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
    #current_user: models.User = Depends(deps.get_current_active_superuser),
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
    #current_user: models.User = Depends(deps.get_current_active_superuser),
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


#@router.put("/me", response_model=schemas.User)
#def update_user_me(
    #*,
    #db: Session = Depends(deps.get_db),
    #password: str = Body(None),
    #full_name: str = Body(None),
    #email: EmailStr = Body(None),
    #current_user: models.User = Depends(deps.get_current_active_user),
#) -> Any:
    #"""
    #Update own user.
    #"""
    #current_user_data = jsonable_encoder(current_user)
    #user_in = schemas.UserUpdate(**current_user_data)
    #if password is not None:
        #user_in.password = password
    #if full_name is not None:
        #user_in.full_name = full_name
    #if email is not None:
        #user_in.email = email
    #user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    #return user


#@router.get("/me", response_model=schemas.User)
#def read_user_me(
    #db: Session = Depends(deps.get_db),
    #current_user: models.User = Depends(deps.get_current_active_user),
#) -> Any:
    #"""
    #Get current user.
    #"""
    #return current_user


#@router.post("/open", response_model=schemas.User)
#def create_user_open(
    #*,
    #db: Session = Depends(deps.get_db),
    #password: str = Body(...),
    #email: EmailStr = Body(...),
    #full_name: str = Body(None),
#) -> Any:
    #"""
    #Create new user without the need to be logged in.
    #"""
    #if not settings.USERS_OPEN_REGISTRATION:
        #raise HTTPException(
            #status_code=403,
            #detail="Open user registration is forbidden on this server",
        #)
    #user = crud.user.get_by_email(db, email=email)
    #if user:
        #raise HTTPException(
            #status_code=400,
            #detail="The user with this username already exists in the system",
        #)
    #user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    #user = crud.user.create(db, obj_in=user_in)
    #return user


#@router.get("/{user_id}", response_model=schemas.User)
#def read_user_by_id(
    #user_id: int,
    #current_user: models.User = Depends(deps.get_current_active_user),
    #db: Session = Depends(deps.get_db),
#) -> Any:
    #"""
    #Get a specific user by id.
    #"""
    #user = crud.user.get(db, id=user_id)
    #if user == current_user:
        #return user
    #if not crud.user.is_superuser(current_user):
        #raise HTTPException(
            #status_code=400, detail="The user doesn't have enough privileges"
        #)
    #return user


#@router.put("/{user_id}", response_model=schemas.User)
#def update_user(
    #*,
    #db: Session = Depends(deps.get_db),
    #user_id: int,
    #user_in: schemas.UserUpdate,
    #current_user: models.User = Depends(deps.get_current_active_superuser),
#) -> Any:
    #"""
    #Update a user.
    #"""
    #user = crud.user.get(db, id=user_id)
    #if not user:
        #raise HTTPException(
            #status_code=404,
            #detail="The user with this username does not exist in the system",
        #)
    #user = crud.user.update(db, db_obj=user, obj_in=user_in)
    #return user

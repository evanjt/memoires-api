from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

#from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.person import Person
from app.api.v1.schemas.person import PersonCreate, PersonUpdate


class CRUDPerson(CRUDBase[Person, PersonCreate, PersonUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Person]:
        return db.query(Person).filter(Person.email == email).first()

    def create(self, db: Session, *, obj_in: PersonCreate) -> Person:
        db_obj = Person(
            email=obj_in.email,
            #hashed_password=get_password_hash(obj_in.password),
            first_names=obj_in.first_names,
            #is_superuser=obj_in.is_superuser,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update(
        self, db: Session, *, db_obj: Person, obj_in: Union[PersonUpdate, Dict[str, Any]]
    ) -> Person:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

person = CRUDPerson(Person)

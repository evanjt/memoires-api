from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app import crud
from app.models.event import Event
from app.api.v1.schemas.event import EventCreate, EventUpdate


class CRUDEvent(CRUDBase[Event, EventCreate, EventUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: EventCreate, owner_id: int
    ) -> Event:

        db_obj = self.model(owner_id=owner_id,
                            title=obj_in.title,
                            description=obj_in.description,
                            start_time=obj_in.start_time,
                            end_time=obj_in.end_time)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        return (
            db.query(self.model)
            .filter(Event.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


event = CRUDEvent(Event)

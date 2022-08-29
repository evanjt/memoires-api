from typing import Optional, List, TYPE_CHECKING
from fastapi import UploadFile
from pydantic import BaseModel, UUID4
import datetime
from app.api.v1.schemas.person import PersonRead


# Shared properties
class EventBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime.datetime
    end_time: datetime.datetime


# Properties to receive on item creation
class EventCreate(EventBase):
    owner: UUID4


# Properties to receive on item update
class EventUpdate(EventBase):
    pass


# Properties to return to client
class EventRead(EventBase):
    owner: "PersonRead"

    class Config:
        orm_mode = True


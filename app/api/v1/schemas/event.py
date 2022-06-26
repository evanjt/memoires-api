from typing import Optional, List
from fastapi import UploadFile
from pydantic import BaseModel


# Shared properties
class EventBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on item creation
class EventCreate(EventBase):
    title: str
    #pictures: Optional[UploadFile]


# Properties to receive on item update
class EventUpdate(EventBase):
    pass


# Properties shared by models stored in DB
class EventInDBBase(EventBase):
    id: int
    title: str
    #owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Event(EventInDBBase):
    pass


# Properties properties stored in DB
class EventInDB(EventInDBBase):
    pass

from sqlmodel import SQLModel, Field, UniqueConstraint
import datetime
from uuid import uuid4, UUID


class EventBase(SQLModel):
    title: str = Field(
        default=None,
        index=True,
    )
    description: str = Field(
        default=None,
        index=True,
    )
    start_time: datetime.datetime = Field(
        default=None,
        index=True,
    )
    end_time: datetime.datetime = Field(
        default=None,
        index=True,
    )


class Event(EventBase, table=True):
    __table_args__ = (UniqueConstraint("id"),)
    iterator: int = Field(
        default=None,
        nullable=False,
        primary_key=True,
        index=True,
    )
    id: UUID = Field(
        default_factory=uuid4,
        index=True,
        nullable=False,
    )


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    uuid: UUID


class EventUpdate(SQLModel):
    pass

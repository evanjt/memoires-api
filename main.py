from typing import List, Optional
from fastapi import FastAPI, HTTPException
from sqlmodel import (Field, Session, SQLModel, create_engine, select,
                      Relationship)
import datetime


class EventPersonLink(SQLModel, table=True):
    ''' Bridge table between Persons and Events '''

    event_id: Optional[int] = Field(
        default=None,
        foreign_key="event.id",
        primary_key=True,
        title="Event ID",
        description="The event's ID"
    )
    person_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        foreign_key="person.id",
        title="Person ID",
        description="The ID of a person associated with the event")


class PersonBase(SQLModel):
    first_names: str = Field(index=True)
    last_names: str = Field(index=True)
    birth_date: datetime.date

class Person(PersonBase, table=True):
    ''' A person belonging to a memoir '''
    id: Optional[int] = Field(default=None, primary_key=True)

    events: List["Event"] = Relationship(back_populates="persons",
                                         link_model=EventPersonLink)

class PersonRead(PersonBase):
    id: int

class PersonCreate(PersonBase):
    pass

class EventBase(SQLModel):
    description: str = Field(
        ..., title="Description of event",
        description="The description of the event, this is the information "
                    "of what happened.")
    time_start: Optional[datetime.datetime]
    time_end: Optional[datetime.datetime]
    time_continuous: bool


class Event(EventBase, table=True):
    ''' Pieces of information that together build a memoir of life '''

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(
        default=None, foreign_key="person.id",
        title="Owner ID",
        description="The person who owns the event")

    persons: List["Person"] = Relationship(back_populates="events",
                                           link_model=EventPersonLink)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/persons/", response_model=PersonCreate)
def create_person(person: PersonCreate):
    with Session(engine) as session:
        obj = Person.from_orm(person)

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj


@app.get("/persons/", response_model=List[PersonRead])
def read_persons():
    with Session(engine) as session:
        objs = session.exec(select(Person)).all()
        return objs

@app.delete("/persons/{id}", status_code=202)
def delete_person(id: int):
    with Session(engine) as session:
        obj = session.get(Person, id)
        if not obj:
            raise HTTPException(404, detail="User not found")

        session.delete(obj)
        session.commit()

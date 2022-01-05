from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Response, Path
from fastapi.middleware.cors import CORSMiddleware
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
    birth_date: Optional[datetime.date] = Field(index=True)


class Person(PersonBase, table=True):
    ''' A person belonging to a memoir '''
    id: Optional[int] = Field(default=None, primary_key=True)

    events: "Event" = Relationship(back_populates="owner")
    associations: List["Event"] = Relationship(back_populates="persons",
                                               link_model=EventPersonLink)

class PersonRead(PersonBase):
    id: int

class PersonCreate(PersonBase):
    pass

class PersonReplace(PersonBase):
    id: int

class EventBase(SQLModel):
    description: str = Field(
        ..., title="Description of event",
        description="The description of the event, this is the information "
                    "of what happened.")
    title: str
    time_start: Optional[datetime.datetime]
    time_end: Optional[datetime.datetime]
    time_continuous: bool
    time_confirmed: bool


class Event(EventBase, table=True):
    ''' Pieces of information that together build a memoir of life '''

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(
        default=None, foreign_key="person.id",
        title="Owner ID",
        description="The person who owns the event")

    owner: "Person" = Relationship(back_populates="events")
    persons: List["Person"] = Relationship(back_populates="associations",
                                           link_model=EventPersonLink)

class EventCreate(EventBase):
    owner_id: Optional[int] = Field(
        default=None, foreign_key="person.id",
        title="Owner ID",
        description="The person who owns the event")
    persons: Optional[List[int]]

class EventRead(EventBase):
    id: int
    owner_id: int
    #owner: PersonRead
    #persons: List[PersonRead]

class EventReplace(EventBase):
    id: int

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/persons", response_model=PersonRead)
def create_person(person: PersonCreate,
                  session: Session = Depends(get_session)):

    obj = Person.from_orm(person)

    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj


@app.put("/persons/{id}", response_model=PersonRead)
def replace_person(person: PersonCreate,
                   id: int = Path(...),
                   session: Session = Depends(get_session)):

    obj = session.get(Person, id)
    data = person.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(obj, key, value)

    session.commit()
    session.refresh(obj)

    return obj


@app.get("/persons", response_model=List[PersonRead])
def read_persons(
    response: Response,
    session: Session = Depends(get_session),
):
    objs = session.exec(select(Person)).all()
    response.headers["Content-Range"] = str(len(objs))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    return objs

@app.get("/persons/{id}", response_model=PersonRead)
def read_person(
    id: int = Path(...),
    session: Session = Depends(get_session),
):
    obj = session.get(Person, id)

    return obj

@app.delete("/persons/{id}", status_code=202)
def delete_person(id: int,
                  session: Session = Depends(get_session)):
    obj = session.get(Person, id)
    if not obj:
        raise HTTPException(404, detail="User not found")

    session.delete(obj)
    session.commit()


@app.post("/events", response_model=EventRead)
def create_event(
    event: EventCreate,
    session: Session = Depends(get_session)
) -> EventRead:

    obj = Event.from_orm(event)

    person_list = []
    if event.persons:
        for person in event.persons:
            person_list.append(session.get(Person, person))

    obj.persons = person_list

    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

@app.put("/events/{id}", response_model=EventRead)
def replace_event(event: EventCreate,
                  id: int = Path(...),
                  session: Session = Depends(get_session)):

    obj = session.get(Event, id)
    data = event.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(obj, key, value)

    session.commit()
    session.refresh(obj)

    return obj


@app.get("/events", response_model=List[EventRead])
def read_events(
    response: Response,
    session: Session = Depends(get_session),
) -> List[EventRead]:

    objs = session.exec(select(Event)).all()
    response.headers["Content-Range"] = str(len(objs))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"

    return objs

@app.get("/events/{id}", response_model=EventRead)
def read_event(
    id: int = Path(...),
    session: Session = Depends(get_session),
):
    obj = session.get(Event, id)

    return obj

@app.delete("/events/{id}", status_code=202)
def delete_event(
    id: int,
    session: Session = Depends(get_session)
) -> None:

    obj = session.get(Event, id)
    if not obj:
        raise HTTPException(404, detail="Event not found")

    session.delete(obj)
    session.commit()

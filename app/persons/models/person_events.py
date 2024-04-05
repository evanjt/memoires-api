from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .event import Event    # noqa: F401
    from .person import Person  # noqa: F401


class PersonEvents(Base):
    __tablename__ = 'person_events'

    id_person = Column(ForeignKey('person.id'), primary_key=True)
    id_event = Column(ForeignKey('event.id'), primary_key=True)

    person = relationship("Person", back_populates="events_associated")
    event = relationship("Event", back_populates="persons")

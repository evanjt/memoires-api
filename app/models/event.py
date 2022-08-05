from typing import TYPE_CHECKING
#from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User                      # noqa: F401
    from .person_events import PersonEvents     # noqa: F401


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUIDType, default=uuid.uuid4, unique=True, index=True, 
                  nullable=False)

    owner_id = Column(ForeignKey("person.id"), index=True, nullable=False)

    title = Column(String, index=True)
    description = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)

    persons = relationship("PersonEvents", back_populates="event")
    owner = relationship("Person", back_populates="events_owned")

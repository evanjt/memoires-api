from typing import TYPE_CHECKING
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .event import Event                    # noqa: F401
    from .person import Person                  # noqa: F401
    from .person_events import PersonEvents     # noqa: F401

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUIDType, default=uuid.uuid4, 
                  unique=True, index=True, nullable=False)
    first_names = Column(String, index=True)
    last_names = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)

    events_associated = relationship("PersonEvents", back_populates="person")
    events_owned = relationship("Event", back_populates="owner")

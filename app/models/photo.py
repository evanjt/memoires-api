from typing import TYPE_CHECKING
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    image = Column(
        UUIDType,
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False
    )
    thumbnail = Column(
        UUIDType,
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False
    )

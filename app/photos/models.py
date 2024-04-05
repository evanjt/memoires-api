from typing import TYPE_CHECKING
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy import Boolean, Column, Integer, String, DateTime
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
    uuid = Column(
        UUIDType,
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False
    )
    original = Column(
        UUIDType,
        unique=True,
        index=True,
        nullable=False
    )
    content_type = Column(
        String,
        nullable=False
    )
    thumbnail = Column(
        UUIDType,
        unique=True,
        index=True,
        nullable=True
    )
    camera_time = Column(
        DateTime,
        default=None,
        index=True,
        nullable=True
    )
    gps_time = Column(
        DateTime,
        default=None,
        index=True,
        nullable=True
    )
    validated_time = Column(
        DateTime,
        default=None,
        index=True,
        nullable=True
    )
    checksum_blake2 = Column(
        String,
        index=True,
        nullable=False
        )

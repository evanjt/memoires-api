from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4
import datetime

# Shared properties
class PersonBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    first_names: Optional[str] = None
    last_names: Optional[str] = None
    alternative_names: Optional[str] = None
    birth_date: Optional[datetime.date] = None


# Properties to receive via API on creation
class PersonCreate(PersonBase):
    pass


# Properties to receive via API on update
class PersonUpdate(PersonBase):
    pass


# Additional properties to return via API
class PersonRead(PersonBase):
    uuid: UUID4

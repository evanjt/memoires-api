from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class PersonBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class PersonCreate(PersonBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class PersonUpdate(PersonBase):
    password: Optional[str] = None


class PersonInDBBase(PersonBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Person(PersonInDBBase):
    pass


# Additional properties stored in DB
class PersonInDB(PersonInDBBase):
    hashed_password: str

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    role: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    unique_id: int

    class Config:
        from_attributes = True

class TodoBase(BaseModel):
    title: str
    description: str
    priority: int
    complete: bool

class TodoCreate(TodoBase):
    pass

class TodoOut(TodoBase):
    unique_id: int
    owner_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    # This schema is the response model for the login endpoint (/token)
    access_token: str
    token_type: str = "bearer"
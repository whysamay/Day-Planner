from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserOut(UserBase):
    id: int
    is_active: bool = True 

    class Config:
        from_attributes = True

class TodoBase(BaseModel):
    title: str
    description: str
    priority: int

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    # CRITICAL FIX: Schema for updating a task. All fields are Optional.
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None 

class TodoOut(TodoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    # This schema is the response model for the login endpoint (/token)
    access_token: str
    token_type: str = "bearer"
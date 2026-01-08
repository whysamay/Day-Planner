from pydantic import BaseModel, EmailStr
from typing import Optional

# --- 1. User Schemas ---

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

# --- 2. Todo Schemas ---

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None # Fixed: Made optional to prevent 422 errors
    priority: int

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None 

class TodoOut(TodoBase):
    id: int
    owner_id: int
    complete: bool # Fixed: Added this field so Pydantic can return the completion status

    class Config:
        from_attributes = True

# --- 3. Authentication Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
import email
from database import Base

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(Base):
    __tablename__ = "users"
    unique_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

class Todo(Base):
    __tablename__ = "todo"

    unique_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    owner_id = Column(Integer, ForeignKey("Users.unique_id"))
    complete = Column(Boolean, default=False)
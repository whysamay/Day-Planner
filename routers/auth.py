from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

# --- Internal Imports (Using relative paths for stability) ---
from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token 

db_dependency = Annotated[Session, Depends(get_db)]
form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter(
    tags=['Authentication']
)

@router.post('/register', response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, Create_User_Request: schemas.UserCreate):

    existing_user = db.query(models.Users).filter(
        models.Users.email == Create_User_Request.email
    ).first()

    if existing_user:
        # If user exists, raise a 400 Bad Request error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_pass = hash_password(Create_User_Request.password)

    Create_user_base = models.Users(
        email=Create_User_Request.email,
        phone_number=Create_User_Request.phone_number,
        role=Create_User_Request.role,
        password=hashed_pass
    )
    
    db.add(Create_user_base)
    db.commit()
    db.refresh(Create_user_base)
    # The 'response_model=schemas.UserOut' filter ensures the hashed_password is NOT returned
    return Create_user_base

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: form_dependency, 
    db: db_dependency
):
    user = db.query(models.Users).filter(
        models.Users.email == form_data.username
    ).first()
    
    if not user or not verify_password(form_data.password, user.password):
        # Raise generic 401 for security
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
     
    token_payload = {"sub": str(user.unique_id)} 
    
    # Generate the access token using the function from security.py
    access_token = create_access_token(token_payload)

    return schemas.Token(access_token=access_token, token_type="bearer")
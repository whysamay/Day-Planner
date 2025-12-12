from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

# --- Internal Imports (Using relative paths for stability) ---
import models, schemas
from database import get_db
from security import hash_password, verify_password, create_access_token 

router = APIRouter(
    tags=['Authentication']
)


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]
form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
token_dependency = Annotated[str, Depends(oauth2_bearer)]

def get_current_user(token: token_dependency, db: db_dependency) -> models.User:
    """Authenticates the user using the JWT token and fetches the User model."""
    
    try:
        user_id = verify_token(token, CREDENTIALS_EXCEPTION)
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None:
        raise CREDENTIALS_EXCEPTION
    
    return user

current_user_dependency = Annotated[models.User, Depends(get_current_user)]

@router.post('/register', response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, Create_User_Request: schemas.UserCreate):

    existing_user = db.query(models.User).filter(
        models.User.email == Create_User_Request.email
    ).first()

    if existing_user:
        # If user exists, raise a 400 Bad Request error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_pass = hash_password(Create_User_Request.password)

    Create_user_base = models.User(
        email=Create_User_Request.email,
        phone_number=Create_User_Request.phone_number,
        role=Create_User_Request.role,
        hashed_password=hashed_pass
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
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Raise generic 401 for security
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
     
    token_payload = {"user_id": str(user.id)} 
    
    # Generate the access token using the function from security.py
    access_token = create_access_token(token_payload)

    return schemas.Token(access_token=access_token, token_type="bearer")
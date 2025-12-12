from fastapi import APIRouter, status
from typing import Annotated, List, Optional

import schemas
from database import get_db
import models
from .auth import db_dependency, current_user_dependency


router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

def get_todo_and_check_owner(db: db_dependency, todo_id: int, user_id: int):
    """Fetches a specific Todo item and ensures it belongs to the given user ID."""
    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.owner_id == user_id
    ).first()
    
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    return todo

@router.post("/", response_model=schemas.TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(
    # Security: Authenticated user object is injected here (User who created the task)
    user: current_user_dependency,
    # Input: Validated data from the client
    todo_request: schemas.TodoCreate,
    db: db_dependency
):
    """Creates a new To-Do item for the authenticated user."""
    
    # 1. Create the SQLAlchemy Model instance
    db_todo = models.Todo(
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        
        # Server-managed fields:
        complete=False, # Always starts as False
        owner_id=user.id # CRITICAL: Links the task to the authenticated user ID
    )
    
    # 2. Save and commit
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo) # Refresh to load the database-generated ID

    # 3. Return the created object
    return db_todo


@router.get('/', response_model=List[schemas.TodoOut])
async def read_all_todos(
    user: current_user_dependency,
    db: db_dependency
):
    """Retrieves all To-Do items owned by the authenticated user."""
    
    # Query all Todo items, filtered by the owner_id matching the current user
    todos = db.query(models.Todo).filter(models.Todo.owner_id == user.id).all()
    
    return todos

@router.get("/{todo_id}", response_model=schemas.TodoOut)
async def read_todo_by_id(
    todo_id: int,
    user: current_user_dependency,
    db: db_dependency
):
    """Retrieves a specific To-Do item if it belongs to the authenticated user."""
    
    # Use the utility function to fetch the item, automatically checking ownership
    todo = get_todo_and_check_owner(db, todo_id, user.id)
    
    return todo


@router.put("/{todo_id}", response_model=schemas.TodoOut)
async def update_todo(
    todo_id: int,
    user: current_user_dependency,
    todo_request: schemas.TodoUpdate, # Use the update schema for partial changes
    db: db_dependency
):
    """Updates an existing To-Do item owned by the authenticated user."""
    
    # 1. Find the existing To-Do item, ensuring ownership
    todo_to_update = get_todo_and_check_owner(db, todo_id, user.id)
    
    # 2. Update fields if they are provided in the request (partial update)
    # The TodoUpdate schema handles fields being Optional
    
    # Check if title was provided
    if todo_request.title is not None:
        todo_to_update.title = todo_request.title
        
    # Check if description was provided
    if todo_request.description is not None:
        todo_to_update.description = todo_request.description
        
    # Check if priority was provided
    if todo_request.priority is not None:
        todo_to_update.priority = todo_request.priority
        
    # Check if complete status was provided
    if todo_request.complete is not None:
        todo_to_update.complete = todo_request.complete
        
    # 3. Save changes
    db.add(todo_to_update)
    db.commit()
    db.refresh(todo_to_update)
    
    return todo_to_update

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    user: current_user_dependency,
    db: db_dependency
):
    """Deletes a To-Do item owned by the authenticated user."""
    
    # 1. Find the existing To-Do item, ensuring ownership
    todo_to_delete = get_todo_and_check_owner(db, todo_id, user.id)

    # 2. Delete and commit
    db.delete(todo_to_delete)
    db.commit()
    
    # Returns 204 No Content upon success (as status_code is set above)
    return
from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(todos.router)
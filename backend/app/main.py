from fastapi import FastAPI
from sqlalchemy.orm import Session

from . import models
from .database import engine, Base
from .routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def startup():
	return "Backend started"

app.include_router(users.router, prefix="/users", tags=["users"])
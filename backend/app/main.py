from dotenv import load_dotenv
import os
load_dotenv()
from fastapi import FastAPI
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth


from . import models
from .config import engine, Base
from .routers import users, auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

print("\n\n\n SECRET KEY: ",os.getenv("SECRET_KEY"), "\n\n\n")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"), 
	same_site="lax", https_only=False, max_age=1800)



@app.get("/")
async def startup():
	return "Backend started"

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
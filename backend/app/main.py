from dotenv import load_dotenv
import os
load_dotenv()
from fastapi import FastAPI
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth


from app import models
from app.config import engine, Base
from app.routers import users, auth, profile, education, resume, project, experience

Base.metadata.create_all(bind=engine)

app = FastAPI()

#  ("\n\n\n SECRET KEY: ",os.getenv("SECRET_KEY"), "\n\n\n")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"), 
	same_site="lax", https_only=False, max_age=1800)



@app.get("/")
async def startup():
	return "Backend started"

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(education.router, prefix="/education", tags=["education"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(project.router, prefix="/project", tags=["project"])
app.include_router(experience.router, prefix="/experience", tags=["experience"])
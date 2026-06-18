from app.database import engine
from app.models import Base
from app.routers import documents, users, projects
from fastapi import FastAPI

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(documents.router)

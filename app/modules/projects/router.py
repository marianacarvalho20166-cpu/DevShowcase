import sqlite3

from fastapi import APIRouter, Depends, status

from app.core.database import get_db
from .schemas import ProjectCreate, ProjectResponse
from .service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, db: sqlite3.Connection = Depends(get_db)):
    return ProjectService(db).create(body)


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: sqlite3.Connection = Depends(get_db)):
    return ProjectService(db).list_all()

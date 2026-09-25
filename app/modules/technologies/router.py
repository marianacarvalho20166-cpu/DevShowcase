import sqlite3

from fastapi import APIRouter, Depends, status

from app.core.database import get_db
from .schemas import TechnologyCreate, TechnologyResponse
from .service import TechnologyService

router = APIRouter(prefix="/api/technologies", tags=["Technologies"])


@router.post("", response_model=TechnologyResponse, status_code=status.HTTP_201_CREATED)
def create_technology(body: TechnologyCreate, db: sqlite3.Connection = Depends(get_db)):
    return TechnologyService(db).create(body)


@router.get("", response_model=list[TechnologyResponse])
def list_technologies(db: sqlite3.Connection = Depends(get_db)):
    return TechnologyService(db).list_all()

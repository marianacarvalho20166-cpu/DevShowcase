import sqlite3

from fastapi import APIRouter, Depends, status

from app.core.database import get_db
from .schemas import ProfileCreate, ProfileResponse
from .service import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(body: ProfileCreate, db: sqlite3.Connection = Depends(get_db)):
    return ProfileService(db).create(body)


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: sqlite3.Connection = Depends(get_db)):
    return ProfileService(db).get(profile_id)

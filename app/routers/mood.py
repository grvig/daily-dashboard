from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MoodEntry

router = APIRouter(prefix="/api/mood", tags=["mood"])


class MoodCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    note: str | None = None


class MoodOut(BaseModel):
    id: int
    score: int
    note: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[MoodOut])
def list_moods(limit: int = 7, db: Session = Depends(get_db)):
    return (
        db.query(MoodEntry)
        .order_by(MoodEntry.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=MoodOut)
def create_mood(mood: MoodCreate, db: Session = Depends(get_db)):
    db_mood = MoodEntry(score=mood.score, note=mood.note)
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from database import get_connection

router=APIRouter(prefix="/events", tags=["Events"])

class EventCreate(BaseModel):
    name: str = Field(..., min_length=1)
    total_seats: int = Field(..., gt=0)
    event_date: datetime

    @field_validator("event_date")
    @classmethod
    def must_be_future(cls, v):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("Event date must be in the future")
        return v

@router.post("/",status_code=201)
def create_event(body:EventCreate):
    conn=get_connection()
    try:
        conn.execute(
            "INSERT INTO events (name, total_seats, available_seats, event_date) VALUES (?, ?, ?, ?)",
            (body.name, body.total_seats, body.total_seats, body.event_date.isoformat())
        )
        conn.commit()
        event = conn.execute(
            "SELECT * FROM events WHERE name = ?", (body.name,)
        ).fetchone()
        return dict(event)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail=f"An event named '{body.name}' already exists")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
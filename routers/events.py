from fastapi import APIRouter, HTTPException, Query
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
    
@router.get("/")
def list_events(
    upcoming_only: bool=Query(False),
    sort_by_date: bool=Query(True)
):
    conn=get_connection()
    now=datetime.now(timezone.utc).isoformat()

    if upcoming_only:
        query = "SELECT * FROM events WHERE event_date > ?"
        events = conn.execute(query, (now,)).fetchall()
    else:
        events = conn.execute("SELECT * FROM events").fetchall()

    result=[]
    for event in events:
        event = dict(event)
        event["total_registrations"] = conn.execute(
            "SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = 'active'",
            (event["id"],)
        ).fetchone()[0]
        result.append(event)

    if sort_by_date:
        result.sort(key=lambda x: x["event_date"])

    conn.close()
    return result

@router.get("/{event_id}")
def get_event(event_id: int):
    conn = get_connection()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event = dict(event)
    event["total_registrations"] = conn.execute(
        "SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = 'active'",
        (event_id,)
    ).fetchone()[0]

    conn.close()
    return event
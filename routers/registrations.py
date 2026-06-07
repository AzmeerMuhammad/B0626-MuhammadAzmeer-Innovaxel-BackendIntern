from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database import get_connection

router=APIRouter(prefix="/registrations", tags=["Registrations"])


class RegistrationCreate(BaseModel):
    user_name: str = Field(..., min_length=1)
    event_id: int = Field(..., gt=0)


@router.post("/",status_code=201)
def register_user(body:RegistrationCreate):
    conn=get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        event=conn.execute(
            "SELECT * FROM events WHERE id = ?", (body.event_id,)
        ).fetchone()

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event["available_seats"] <= 0:
            raise HTTPException(status_code=409, detail="Event is fully booked")

        existing = conn.execute(
            "SELECT * FROM registrations WHERE user_name = ? AND event_id = ?",
            (body.user_name, body.event_id)
        ).fetchone()

        if existing and existing["status"] == "active":
            raise HTTPException(status_code=409, detail="User is already registered for this event")

        conn.execute(
            "INSERT INTO registrations (user_name, event_id) VALUES (?, ?)",
            (body.user_name, body.event_id)
        )
        conn.execute(
            "UPDATE events SET available_seats = available_seats - 1 WHERE id = ?",
            (body.event_id,)
        )
        conn.commit()

        registration=conn.execute(
            "SELECT * FROM registrations WHERE user_name = ? AND event_id = ?",
            (body.user_name, body.event_id)
        ).fetchone()
        return dict(registration)

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="User is already registered for this event")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    
@router.get("/event/{event_id}")
def get_event_registrations(event_id: int):
    conn = get_connection()

    event = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registrations = conn.execute(
        "SELECT * FROM registrations WHERE event_id = ? AND status = 'active'",
        (event_id,)
    ).fetchall()

    conn.close()
    return [dict(r) for r in registrations]


@router.get("/user/{user_name}")
def get_user_registrations(user_name: str):
    conn = get_connection()

    registrations = conn.execute(
        "SELECT * FROM registrations WHERE user_name = ? AND status = 'active'",
        (user_name,)
    ).fetchall()

    conn.close()
    return [dict(r) for r in registrations]


@router.delete("/{registration_id}")
def cancel_registration(registration_id: int):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        registration = conn.execute(
            "SELECT * FROM registrations WHERE id = ?", (registration_id,)
        ).fetchone()

        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")

        if registration["status"] == "cancelled":
            raise HTTPException(status_code=409, detail="Registration is already cancelled")

        conn.execute(
            "UPDATE registrations SET status = 'cancelled' WHERE id = ?",
            (registration_id,)
        )
        conn.execute(
            "UPDATE events SET available_seats = available_seats + 1 WHERE id = ?",
            (registration["event_id"],)
        )
        conn.commit()

        registration = conn.execute(
            "SELECT * FROM registrations WHERE id = ?", (registration_id,)
        ).fetchone()
        return dict(registration)

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
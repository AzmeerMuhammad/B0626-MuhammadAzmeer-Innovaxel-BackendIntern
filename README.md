# B0626-MuhammadAzmeer-Innovaxel-BackendIntern
# Event Registration API

A simple REST API built with **FastAPI** and **SQLite** for managing events and registrations.

## Stack
- **FastAPI** — web framework
- **SQLite** — built into Python, no setup needed
- **Pydantic** — request validation
- **Uvicorn** — server

## Setup & Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Visit **http://127.0.0.1:8000/docs** for interactive API docs.

## Endpoints

### Events
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/events/` | Create event |
| GET | `/events/` | List all events |
| GET | `/events/?upcoming_only=true` | Upcoming events only |
| GET | `/events/{id}` | Get single event |

### Registrations
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/registrations/` | Register user |
| DELETE | `/registrations/{id}` | Cancel registration |
| GET | `/registrations/event/{event_id}` | List active registrations for event |

## Validation Rules
- Event name must be unique
- Total seats must be greater than 0
- Event date must be in the future
- Cannot register if event is full
- Same user cannot register twice for the same event
- Cancelling a registration frees the seat back up

## Race Condition Protection
Uses `BEGIN IMMEDIATE` transaction when registering or cancelling so two simultaneous requests can't both read `available_seats = 1` and both succeed. The `UNIQUE(user_name, event_id)` constraint on the registrations table is an extra safety net at the database level.

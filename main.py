from fastapi import FastAPI
from database import init_db
from routers import events

app=FastAPI(
    title="Event Registration API",
    description="Simple API to create events and manage user registrations.",
    version="1.0.0"
)

init_db()

app.include_router(events.router)

@app.get("/",tags=["Health"])
def root():
    return {"status":"running","docs":"/docs"}
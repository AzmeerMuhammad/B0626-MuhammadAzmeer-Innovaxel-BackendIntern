from fastapi import FastAPI
from database import init_db

app=FastAPI(
    title="Event Registration API",
    description="Simple API to create events and manage user registrations.",
    version="1.0.0"
)

init_db()

@app.get("/",tags=["Health"])
def root():
    return {"status":"running","docs":"/docs"}
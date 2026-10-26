from fastapi import FastAPI

from notes.routers import health, notes


app = FastAPI()
app.include_router(health.router)
app.include_router(notes.router)


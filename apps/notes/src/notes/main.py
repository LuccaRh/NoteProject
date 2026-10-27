from fastapi import FastAPI

from notes.routers import health


app = FastAPI()
app.include_router(health.router)


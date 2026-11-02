# Imports
from fastapi import FastAPI

from ichiro.handlers import add_handlers
from ichiro.routers import health, notes


# Global variables
app = FastAPI()
app.include_router(health.router)
app.include_router(notes.router)
add_handlers(app=app)

# Imports
from fastapi import FastAPI

from ichiro.handlers import add_handlers
from ichiro.routers import health, notes
from ichiro.user import read_user


# Global variables
app = FastAPI()
app.include_router(health.router)
app.include_router(notes.router)
app.middleware("http")(read_user)
add_handlers(app=app)

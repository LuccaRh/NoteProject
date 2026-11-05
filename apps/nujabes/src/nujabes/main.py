# Imports
from fastapi import FastAPI

from nujabes.handlers import add_handlers
from nujabes.routers import auth, health


# Global variables
app = FastAPI()
app.include_router(health.router)
app.include_router(auth.router)
add_handlers(app=app)

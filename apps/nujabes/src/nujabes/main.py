# Imports
from fastapi import FastAPI

from nujabes.routers import auth, health


# Global variables
app = FastAPI()
app.include_router(health.router)
app.include_router(auth.router)

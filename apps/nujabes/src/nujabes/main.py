# Imports
from fastapi import FastAPI

from nujabes.routers import health


# Global variables
app = FastAPI()
app.include_router(health.router)

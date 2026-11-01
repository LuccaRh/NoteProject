# Imports
from fastapi import FastAPI

from lonzo.routers import chat, health


# Global variables
app = FastAPI()
app.include_router(health.router)
app.include_router(chat.router)

# Imports
from fastapi import FastAPI

from lonzo.core.handlers import add_handlers
from lonzo.core.lifespan import lifespan
from lonzo.core.user import read_user
from lonzo.routers import chat, conversations, health, settings, workspaces


# Global variables
app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(settings.router)
app.middleware("http")(read_user)
add_handlers(app=app)

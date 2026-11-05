# Imports
from fastapi import FastAPI

from lonzo.handlers import add_handlers
from lonzo.lifespan import lifespan
from lonzo.routers import chat, conversations, health, workspaces
from lonzo.user import read_user


# Global variables
app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.middleware("http")(read_user)
add_handlers(app=app)

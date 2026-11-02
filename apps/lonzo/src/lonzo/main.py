# Imports
from fastapi import FastAPI

from lonzo.handlers import add_handlers
from lonzo.lifespan import lifespan
from lonzo.routers import chat, conversations, health, workspaces


# Global variables
app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(chat.router)
app.include_router(conversations.router)
add_handlers(app=app)

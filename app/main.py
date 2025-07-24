from fastapi import FastAPI
from .routers import (
    auth, user, task, comment,
    team, evaluation, meeting, calendar
)
from starlette.middleware.sessions import SessionMiddleware
from .admin_views import setup_admin
from .backend.db import engine
from config import ADMIN_SECRET_KEY
from contextlib import asynccontextmanager
from .create_admin import create_super_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_super_admin()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=ADMIN_SECRET_KEY)
setup_admin(app, engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(comment.router)
app.include_router(team.router)
app.include_router(evaluation.router)
app.include_router(meeting.router)
app.include_router(calendar.router)


@app.get("/healthy")
async def check_healthy():
    return {'is_healthy': True}

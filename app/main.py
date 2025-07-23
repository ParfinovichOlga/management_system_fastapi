from fastapi import FastAPI
from app.routers import (
    auth, user, task, comment,
    team, evaluation, meeting, calendar
)


app = FastAPI()

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

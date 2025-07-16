from fastapi import FastAPI
from app.routers import auth, user, task


app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(task.router)


@app.get("/healthy")
async def check_healthy():
    return {'is_healthy': True}

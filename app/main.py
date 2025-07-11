from fastapi import FastAPI
from app.users.routers import auth


app = FastAPI()

app.include_router(auth.router)


@app.get("/healthy")
async def check_healthy():
    return {'is_healthy': True}

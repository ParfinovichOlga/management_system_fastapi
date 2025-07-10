from fastapi import FastAPI


app = FastAPI()

@app.get("/healthy")
async def check_healthy():
    return {'is_healthy': True}




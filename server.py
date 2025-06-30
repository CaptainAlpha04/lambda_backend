from fastapi import FastAPI
from routes.mentor import router as mentor_router
from routes.exercises import router as exercise_router

app = FastAPI()

app.include_router(mentor_router, prefix="/api")
app.include_router(exercise_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
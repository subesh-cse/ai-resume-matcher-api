from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import auth, jobs, resumes, match

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="AI Resume Matcher API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(match.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Resume Matcher API. Visit /docs for documentation."}


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is live"}
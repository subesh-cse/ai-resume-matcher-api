from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import JobCreate, JobDescription
from app.services.matcher import HybridScoringEngine

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobDescription, status_code=status.HTTP_201_CREATED)
async def create_job(job_in: JobCreate, session: Session = Depends(get_session)):
    clean_title = job_in.title.strip()
    clean_description = job_in.description.strip()

    if not clean_title or not clean_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title and description cannot be empty.",
        )

    embeddings = await HybridScoringEngine.get_embeddings([clean_description])
    job_embedding = embeddings[0] if embeddings else None

    job = JobDescription(
        title=clean_title,
        description=clean_description,
        embedding=job_embedding,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.get("/", response_model=list[JobDescription])
def list_jobs(session: Session = Depends(get_session)):
    jobs = session.exec(select(JobDescription)).all()
    return jobs


@router.get("/{job_id}", response_model=JobDescription)
def get_job(job_id: int, session: Session = Depends(get_session)):
    job = session.get(JobDescription, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {job_id} not found.",
        )
    return job
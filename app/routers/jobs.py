from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import JobCreate, JobDescription

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobDescription, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, session: Session = Depends(get_session)):
    if not job_in.title.strip() or not job_in.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title and description cannot be empty.",
        )

    
    job = JobDescription(title=job_in.title.strip(), description=job_in.description.strip())
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
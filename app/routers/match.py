from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import MatchRequest, MatchResponse, Resume, JobDescription, User
from app.services.matcher import HybridScoringEngine
from app.routers.auth import get_current_user

router = APIRouter(prefix="/match", tags=["Match Engine"])


@router.post("/", response_model=MatchResponse)
async def match_resume_to_job(
    payload: MatchRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    resume = session.get(Resume, payload.resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {payload.resume_id} not found."
        )

    
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to use this resume for matching."
        )

    job = session.get(JobDescription, payload.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with id {payload.job_id} not found."
        )

    result = await HybridScoringEngine.calculate_match(
        resume_text=resume.extracted_text,
        job_text=job.description
    )

    return result
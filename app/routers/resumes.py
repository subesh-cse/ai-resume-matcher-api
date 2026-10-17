from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlmodel import Session, select

from app.database import get_session
from app.models import Resume, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}",
        )


@router.post("/upload", response_model=Resume, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    file_bytes = await file.read()
    extracted_text = extract_text_from_pdf(file_bytes)

    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract any readable text from the uploaded PDF.",
        )

    
    resume = Resume(
        filename=file.filename,
        extracted_text=extracted_text,
        user_id=current_user.id,
    )
    session.add(resume)
    session.commit()
    session.refresh(resume)

    return resume


@router.get("/", response_model=list[Resume])
def list_resumes(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    
    statement = select(Resume).where(Resume.user_id == current_user.id)
    resumes = session.exec(statement).all()
    return resumes


@router.get("/{resume_id}", response_model=Resume)
def get_resume(
    resume_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    resume = session.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume.",
        )

    return resume
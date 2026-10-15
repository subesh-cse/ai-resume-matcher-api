from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str


class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    extracted_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobDescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(SQLModel):
    email: str
    password: str


class UserResponse(SQLModel):
    id: int
    email: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    email: Optional[str] = None


class JobCreate(SQLModel):
    title: str
    description: str


class MatchRequest(SQLModel):
    resume_id: int
    job_id: int


class MatchResponse(SQLModel):
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str
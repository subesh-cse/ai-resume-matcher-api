from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column, JSON


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str


class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    extracted_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id", index=True)


class JobDescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



class MatchResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    resume_id: int = Field(foreign_key="resume.id", index=True)
    job_id: int = Field(foreign_key="jobdescription.id", index=True)
    match_score: float
    matched_skills: List[str] = Field(default=[], sa_column=Column(JSON))
    missing_skills: List[str] = Field(default=[], sa_column=Column(JSON))
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Schemas / DTOs ---
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
    id: Optional[int] = None
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str
    created_at: Optional[datetime] = None
from pydantic import BaseModel
from typing import List, Optional
from app.enums.job_ads_enums import ExperienceLevel, JobType, WorkMode

class CandidateCreate(BaseModel):
    firstname: str
    lastname: str
    skills: List[str]
    education_level: str
    years_experience: float
    city: str
    country: str

class CandidateUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    skills: Optional[List[str]] = None
    education_level: Optional[str] = None
    years_experience: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None

class JobAdCreate(BaseModel):
    title: str
    description: str
    experience_level: str
    job_type: str
    work_mode: str
    city: str
    country: str

class JobAdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class JobAdResult(BaseModel):
    id: str
    title: str
    description: str
    required_experience_level: str
    job_type: str
    work_mode: str
    city: str
    country: str
    score: Optional[float] = None

class JobAdsResponse(BaseModel):
    count: int
    results: List[JobAdResult]
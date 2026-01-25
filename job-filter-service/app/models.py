from pydantic import BaseModel
from typing import List, Optional
from app.enums.job_ads_enums import ExperienceLevel, JobType, WorkMode
from app.enums.candidates_enums import EducationLevel

class CandidateBase(BaseModel):
    firstname: str
    lastname: str
    education_level: EducationLevel 
    years_experience: float
    skills: List[str]
    city: str
    country: str


class CandidateCreate(BaseModel):
    firstname: str
    lastname: str
    skills: List[str]
    education_level: EducationLevel
    years_experience: float
    city: str
    country: str

class CandidateUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    skills: Optional[List[str]] = None
    education_level: Optional[EducationLevel] = None
    years_experience: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None

class JobBase(BaseModel):
    title: str
    description: str
    required_experience_level: ExperienceLevel
    job_type: JobType
    work_mode: WorkMode
    city: str
    country: str

class JobAdCreate(BaseModel):
    title: str
    description: str
    required_experience_level: ExperienceLevel
    job_type: JobType
    work_mode: WorkMode
    city: str
    country: str

class JobAdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_experience_level: Optional[ExperienceLevel] = None
    job_type: Optional[JobType] = None
    work_mode: Optional[WorkMode] = None
    city: Optional[str] = None
    country: Optional[str] = None

class JobAdResult(BaseModel):
    id: str
    title: str
    description: str
    required_experience_level: ExperienceLevel
    job_type: JobType
    work_mode: WorkMode
    city: str
    country: str
    score: Optional[float] = None

class JobAdsResponse(BaseModel):
    count: int
    results: List[JobAdResult]
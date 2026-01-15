from fastapi import APIRouter, HTTPException
from typing import List
from app.crud_operations.job_ads import create_job_ad, get_job_ad_by_id, update_job_ad, delete_job_ad
from app.enums.job_ads_enums import JobType, ExperienceLevel, WorkMode
from app.models import JobAdCreate, JobAdUpdate

router = APIRouter(prefix="/job_ads", tags=["Job Ads"])

@router.post("/")
def create_job_ad_endpoint(job: JobAdCreate):
    try:
        job_id = create_job_ad(
            title=job.title,
            description=job.description,
            experience_level=job.experience_level,
            job_type=job.job_type,
            work_mode=job.work_mode,
            city=job.city,
            country=job.country
        )
        return {"id": job_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{job_id}")
def get_job_ad_endpoint(job_id: str):
    job = get_job_ad_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ad not found")
    return job

@router.put("/{job_id}")
def update_job_ad_endpoint(job_id: str, job_update: JobAdUpdate):
    updates = {k: v for k, v in job_update.dict().items() if v is not None}
    
    success = update_job_ad(job_id, **updates)
    if not success:
        raise HTTPException(status_code=404, detail="Job ad not found")
    return {"status": "updated"}

@router.delete("/{job_id}")
def delete_job_ad_endpoint(job_id: str):
    delete_job_ad(job_id)
    return {"status": "deleted"}
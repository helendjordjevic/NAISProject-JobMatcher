from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.crud_operations.job_ads import create_job_ad, get_job_ad_by_id, update_job_ad, delete_job_ad, filter_job_ads
from app.enums.job_ads_enums import JobType, ExperienceLevel, WorkMode
from app.models import JobAdCreate, JobAdUpdate, JobAdsResponse
from app.generate_reports.pinecone_reports import filter_job_ads_for_report, generate_job_ads_pdf
from fastapi.responses import FileResponse

router = APIRouter(prefix="/job_ads", tags=["Job Ads"])

@router.get("/report", summary="Pinecone JobAds PDF report")
def generate_job_ads_report(
    job_type: List[str] = Query(None, description="Filter by job type"),
    city: Optional[str] = Query(None, description="Filter by city")
):
    cities = [city] if city else None
    job_ads = filter_job_ads_for_report(job_types=job_type, cities=cities, top_k=10)

    if not job_ads:
        raise HTTPException(status_code=404, detail="No job ads found for given filters")

    pdf_path = generate_job_ads_pdf(job_ads, job_type=job_type, city=city)
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.split("/")[-1])


@router.get("/filter", response_model=JobAdsResponse)
def filter_job_ads_endpoint(
    title_query: str | None = None,
    required_experience_level: ExperienceLevel | None = None,
    job_type: JobType | None = None,
    work_mode: WorkMode | None = None
):
    return filter_job_ads(
        title_query=title_query,
        required_experience_level=required_experience_level,
        job_type=job_type,
        work_mode=work_mode
    )

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
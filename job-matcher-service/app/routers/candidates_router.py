from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.crud_operations.candidates import create_candidate, get_candidate_by_id, update_candidate, delete_candidate, filter_candidates
from app.enums.candidates_enums import EducationLevel, SKILLS_POOL
from app.models import CandidateCreate, CandidateUpdate
from fastapi.responses import FileResponse
from app.generate_reports.pinecone_reports import filter_candidates_for_report, generate_candidates_pdf, filter_candidates_for_job_description, generate_candidates_by_job_pdf
import os

router = APIRouter(prefix="/candidates", tags=["Candidates"])
@router.get("/report", summary="Pinecone candidates PDF report")
def generate_candidates_report(
    skills: List[str] = Query(None, description="Skills list"),
    min_years: int = Query(None, description="Minimum years of experience")
):
    candidates = filter_candidates_for_report(
        skill_query=",".join(skills) if skills else None,
        min_years_experience=min_years
    )

    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No candidates found for given filters"
        )

    pdf_path = generate_candidates_pdf(candidates, skills, min_years)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )

@router.get("/complex-report", summary="Top candidates by job description")
def generate_report_by_job(
    job_description: str = Query(..., description="Job description for vector search"),
    top_k: int = Query(5, description="Number of top candidates to return")
):
    try:
        candidates = filter_candidates_for_job_description(job_description, top_k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found for this job description")

    pdf_path = generate_candidates_by_job_pdf(candidates, job_description)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_path.split("/")[-1]
    )

@router.get("/filter")
def filter_candidates_endpoint(
    skill_query: str | None = None,
    education_level: str | None = None,
    min_years_experience: float | None = None,
    page: int = Query(1, description="Stranica rezultata"),
    page_size: int = Query(20, description="Broj rezultata po stranici")

):
    all_matches = filter_candidates(
        skill_query=skill_query,
        education_level=education_level,
        min_years_experience=min_years_experience,
        top_k=500 
    )

    start = (page - 1) * page_size
    end = start + page_size
    paged_matches = all_matches[start:end]

    return {
        "count": len(all_matches),
        "page": page,
        "page_size": page_size,
        "results": paged_matches
    }

@router.post("/")
def create_candidate_endpoint(candidate: CandidateCreate):
    try:
        candidate_id = create_candidate(
            firstname=candidate.firstname,
            lastname=candidate.lastname,
            skills=candidate.skills,
            education_level=candidate.education_level,
            years_experience=candidate.years_experience,
            city=candidate.city,
            country=candidate.country
        )
        return {"id": candidate_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{candidate_id}")
def get_candidate_endpoint(candidate_id: str):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/{candidate_id}")
def update_candidate_endpoint(candidate_id: str, candidate_update: CandidateUpdate):
    updates = candidate_update.dict(exclude_unset=True)  # uzima samo polja koja su prosleđena
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update provided")

    success = update_candidate(candidate_id, **updates)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return {"status": "updated"}

@router.delete("/{candidate_id}")
def delete_candidate_endpoint(candidate_id: str):
    delete_candidate(candidate_id)
    return {"status": "deleted"}
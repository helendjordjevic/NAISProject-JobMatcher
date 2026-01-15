from fastapi import APIRouter, HTTPException
from typing import List
from app.crud_operations.candidates import create_candidate, get_candidate_by_id, update_candidate, delete_candidate
from app.enums.candidates_enums import EducationLevel, SKILLS_POOL
from app.models import CandidateCreate, CandidateUpdate

router = APIRouter(prefix="/candidates", tags=["Candidates"])

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
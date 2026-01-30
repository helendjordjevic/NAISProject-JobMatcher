from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import uuid
from app.models import CandidateCreate, CandidateUpdate, CandidateBase
from app.database import es
from elasticsearch.exceptions import NotFoundError
from app.crud_operations.candidates import search_by_experience_and_city, search_by_skills_and_education
from fastapi.responses import FileResponse
from app.generate_scripts.es_reports import fetch_candidates, generate_pdf_candidates   
from app.enums.candidates_enums import EducationLevel
import os

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)

@router.get("/report", summary="Generate Candidates PDF report")
def generate_candidates_report(
    education_level: EducationLevel = Query(None, description="Education level filter"),
    min_years_experience: int = Query(None, description="Minimal years of experience")
):
    filters = {
        "education_level": education_level.value if education_level else None,
        "min_years_experience": min_years_experience
    }

    try:
        candidates = fetch_candidates(filters)

        if not candidates:
            raise HTTPException(status_code=404, detail="No candidates found for the given filters")

        pdf_file = generate_pdf_candidates(candidates, filters)
        return FileResponse(pdf_file, media_type="application/pdf", filename=os.path.basename(pdf_file))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/by-experience-city", response_model=dict)
def search_candidates_by_experience_and_city(payload: dict):
    try:
        query = search_by_experience_and_city(payload)
        res = es.search(index="candidates", body=query)

        results = [hit["_source"] for hit in res["hits"]["hits"]]
        avg_exp = res.get("aggregations", {}).get("avg_experience", {}).get("value")

        return {
            "results": results,
            "avg_experience": avg_exp
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/search/by-skills-education", response_model=dict)
def search_candidates_by_skills_and_education(payload: dict):
    
    try:
        query = search_by_skills_and_education(payload)
        res = es.search(index="candidates", body=query)

        return {
            "results": [hit["_source"] for hit in res["hits"]["hits"]],
            "education_stats": res["aggregations"]["by_education_level"]["buckets"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict)
def create_candidate_endpoint(candidate: CandidateCreate):
    cid = str(uuid.uuid4())
    doc = candidate.dict()
    doc["candidate_id"] = cid
    es.index(index="candidates", id=cid, document=doc)
    return {"candidate_id": cid, "message": "Kandidat kreiran"}


@router.get("/{cid}", response_model=CandidateBase)
def read_candidate_endpoint(cid: str):
    try:
        res = es.get(index="candidates", id=cid)
        return res["_source"]
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Kandidat nije pronađen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{cid}", response_model=dict)
def update_candidate_endpoint(cid: str, updates: CandidateUpdate):
    try:
        es.update(index="candidates", id=cid, doc=updates.dict(exclude_unset=True))
        return {"message": f"Kandidat {cid} ažuriran"}
    except:
        raise HTTPException(status_code=404, detail="Kandidat nije pronađen")


@router.put("/{cid}", response_model=dict)
def update_candidate_endpoint(cid: str, updates: CandidateUpdate):
    try:
        es.update(
            index="candidates",
            id=cid,
            doc=updates.dict(exclude_unset=True)
        )
        return {"message": f"Kandidat {cid} ažuriran"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Kandidat nije pronađen")


@router.delete("/{cid}", response_model=dict)
def delete_candidate_endpoint(cid: str):
    try:
        es.delete(index="candidates", id=cid)
        return {"message": f"Kandidat {cid} obrisan"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Kandidat nije pronađen")
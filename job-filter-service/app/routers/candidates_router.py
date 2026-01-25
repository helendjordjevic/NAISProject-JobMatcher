from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import uuid
from app.models import CandidateCreate, CandidateUpdate, CandidateBase
from app.database import es
from elasticsearch.exceptions import NotFoundError


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)

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
    
@router.post("/search", response_model=List[CandidateBase])
def search_candidates_endpoint(query: dict):
    res = es.search(index="candidates", query=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]


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
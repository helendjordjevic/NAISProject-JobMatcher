from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from elasticsearch.exceptions import NotFoundError

from app.database import es
from app.models import JobAdCreate, JobAdUpdate, JobAdResult

router = APIRouter(
    prefix="/job_ads",
    tags=["Job Ads"]
)

@router.post("/", response_model=dict)
def create_job_endpoint(job: JobAdCreate):
    jid = str(uuid.uuid4())

    doc = job.dict()
    doc["job_id"] = jid

    es.index(index="job_ads", id=jid, document=doc)

    return {
        "job_id": jid,
        "message": "Oglas kreiran"
    }


@router.get("/{jid}", response_model=JobAdResult)
def read_job_endpoint(jid: str):
    try:
        res = es.get(index="job_ads", id=jid)
        source = res["_source"]

        return {
            "id": jid,
            **source
        }

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Oglas nije pronađen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[JobAdResult])
def search_jobs_endpoint(query: dict):
    res = es.search(index="job_ads", query=query)

    results = []
    for hit in res["hits"]["hits"]:
        results.append({
            "id": hit["_id"],
            **hit["_source"],
            "score": hit["_score"]
        })

    return results


@router.put("/{jid}", response_model=dict)
def update_job_endpoint(jid: str, updates: JobAdUpdate):
    try:
        es.update(
            index="job_ads",
            id=jid,
            doc=updates.dict(exclude_unset=True)
        )
        return {"message": f"Oglas {jid} ažuriran"}

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Oglas nije pronađen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{jid}", response_model=dict)
def delete_job_endpoint(jid: str):
    try:
        es.delete(index="job_ads", id=jid)
        return {"message": f"Oglas {jid} obrisan"}

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Oglas nije pronađen")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

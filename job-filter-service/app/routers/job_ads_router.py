from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from elasticsearch.exceptions import NotFoundError
from app.database import es
from app.models import JobAdCreate, JobAdUpdate, JobAdResult
from app.crud_operations.job_ads import search_by_desc_exp, create_job_ad_saga, create_job_ad_saga_simulation

router = APIRouter(
    prefix="/job_ads",
    tags=["Job Ads"]
)

@router.post("/search", response_model=dict)
def search_jobs(payload: dict):
    try:
        query = search_by_desc_exp(payload)
        res = es.search(index="job_ads", body=query)

        return {
            "results": [hit["_source"] for hit in res["hits"]["hits"]],
            "jobs_by_city": res["aggregations"]["jobs_by_city"]["buckets"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#   @router.post("/", response_model=dict)
#   def create_job_endpoint(job: JobAdCreate):
#    jid = str(uuid.uuid4())

#    doc = job.dict()
#    doc["job_id"] = jid

#    es.index(index="job_ads", id=jid, document=doc)

#    return {
#        "job_id": jid,
#        "message": "Oglas kreiran"
#    }

@router.post("/", response_model=dict)
def create_job_ad_endpoint(job: JobAdCreate):
    try:
        jid = create_job_ad_saga(job)

        return {"job_id": jid, "message": "Oglas kreiran i u ES i u Pinecone"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/simulation", response_model=dict)
def create_job_ad_endpoint(
    job: JobAdCreate,
    simulate_pinecone_fail: bool = False
):
    try:
        jid = create_job_ad_saga_simulation(
            job,
            simulate_pinecone_fail=simulate_pinecone_fail
        )
        return {"job_id": jid, "message": "Saga uspešna"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

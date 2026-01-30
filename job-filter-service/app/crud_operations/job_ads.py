# from elasticsearch import Elasticsearch
import uuid
from app.database import es
from app.pinecone.pinecone_client import index, generate_job_embedding
from app.models import JobAdCreate

# es = Elasticsearch("http://localhost:9200")

#def create_job(title, description, experience_level, job_type, work_mode, city, country):
#    jid = str(uuid.uuid4())
#    doc = {
#        "job_id": jid,
#        "title": title,
#        "description": description,
#        "required_experience_level": experience_level,
#        "job_type": job_type,
#        "work_mode": work_mode,
#        "city": city,
#        "country": country
#    }
#    es.index(index="job_ads", id=jid, document=doc)
#    print(f"Oglas kreiran: {jid}")
#    return jid

def create_job_ad_saga(job: JobAdCreate) -> str:

    jid = str(uuid.uuid4())
    doc = job.dict()
    doc["job_id"] = jid

        # ElasticSearch db
    try:
        es.index(index="job_ads", id=jid, document=doc)
    except Exception as e:
        raise Exception(f"ElasticSearch upis failed: {str(e)}")

        # Pinecone db
    try:
            
        embedding = generate_job_embedding(
            job.title,
            job.description,
            job.required_experience_level,
            job.job_type,
            job.work_mode,
            job.city,
            job.country
        )

        vector = {
            "id": jid,
            "values": embedding,
            "metadata": doc  
        }

        index.upsert(vectors=[vector], namespace="job_ads")

    except Exception as e:
            # rollback ElasticSearch upisa
        try:
            es.delete(index="job_ads", id=jid)
        except Exception as rollback_err:
                # loguj rollback grešku
            print(f"Rollback failed: {rollback_err}")
        raise Exception(f"Pinecone upis failed, rollback ElasticSearch: {str(e)}")

    return jid

def create_job_ad_saga_simulation(job: JobAdCreate, simulate_pinecone_fail: bool = False) -> str:
    jid = str(uuid.uuid4())
    doc = job.dict()
    doc["job_id"] = jid

    try:
        es.index(index="job_ads", id=jid, document=doc)
        print("ElasticSearch upis uspešan")
    except Exception as e:
        raise Exception(f"ElasticSearch upis failed: {e}")

    try:
        if simulate_pinecone_fail:
            raise Exception("Simulirani pad Pinecone servisa")

        print("Generisem embedding...")

        embedding = generate_job_embedding(
            job.title,
            job.description,
            job.required_experience_level,
            job.job_type,
            job.work_mode,
            job.city,
            job.country
        )

        print(" Embedding generisan, duzina:", len(embedding))
        print(" Upisujem u Pinecone...")

        vector = {
            "id": jid,
            "values": embedding,
            "metadata": doc
        }

        index.upsert(vectors=[vector], namespace="job_ads")
        print("Pinecone upis uspešan")

    except Exception as e:
        es.delete(index="job_ads", id=jid)
        raise Exception(f"Pinecone upis failed, rollback ES: {e}")

    return jid


def read_job(jid):
    res = es.get(index="job_ads", id=jid)
    return res["_source"]

def update_job(jid, updates: dict):
    es.update(index="job_ads", id=jid, doc=updates)
    print(f"Oglas {jid} ažuriran")

def delete_job(jid):
    es.delete(index="job_ads", id=jid)
    print(f"Oglas {jid} obrisan")

def search_by_desc_exp(payload: dict):

    must = []
    filters = []

    # FULL-TEXT SEARCH (title + description)
    if payload.get("query"):
        must.append({
            "multi_match": {
                "query": payload["query"],
                "fields": ["title", "description"],
                "operator": "or"
            }
        })

    if payload.get("required_experience_level"):
        filters.append({
            "term": {
                "required_experience_level": payload["required_experience_level"]
            }
        })

    if payload.get("work_modes"):
        filters.append({
            "terms": {
                "work_mode": payload["work_modes"]
            }
        })

    if payload.get("city"):
        filters.append({
            "term": {
                "city": payload["city"]
            }
        })

    query = {
        "query": {
            "bool": {
                "must": must if must else [{"match_all": {}}],
                "filter": filters
            }
        },
        "sort": [
            {"_score": {"order": "desc"}}
        ],
        "aggs": {
            "jobs_by_city": {
                "terms": {
                    "field": "city"
                }
            }
        }
    }

    return query

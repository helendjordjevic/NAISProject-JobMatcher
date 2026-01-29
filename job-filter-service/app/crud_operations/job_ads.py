from elasticsearch import Elasticsearch
import uuid

es = Elasticsearch("http://localhost:9200")

def create_job(title, description, experience_level, job_type, work_mode, city, country):
    jid = str(uuid.uuid4())
    doc = {
        "job_id": jid,
        "title": title,
        "description": description,
        "required_experience_level": experience_level,
        "job_type": job_type,
        "work_mode": work_mode,
        "city": city,
        "country": country
    }
    es.index(index="job_ads", id=jid, document=doc)
    print(f"Oglas kreiran: {jid}")
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

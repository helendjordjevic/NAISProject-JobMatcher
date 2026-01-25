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
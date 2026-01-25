from elasticsearch import Elasticsearch
import uuid

es = Elasticsearch("http://localhost:9200")

def create_candidate(firstname, lastname, education, years_exp, skills, city, country):
    cid = str(uuid.uuid4())
    doc = {
        "candidate_id": cid,
        "firstname": firstname,
        "lastname": lastname,
        "education_level": education,
        "years_experience": years_exp,
        "skills": skills,
        "city": city,
        "country": country
    }
    es.index(index="candidates", id=cid, document=doc)
    print(f"Kandidat kreiran: {cid}")
    return cid

def read_candidate(cid):
    res = es.get(index="candidates", id=cid)
    return res["_source"]

def search_candidates(query):
    res = es.search(index="candidates", query=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]

def update_candidate(cid, updates: dict):
    es.update(index="candidates", id=cid, doc=updates)
    print(f"Kandidat {cid} ažuriran")

def delete_candidate(cid):
    es.delete(index="candidates", id=cid)
    print(f"Kandidat {cid} obrisan")
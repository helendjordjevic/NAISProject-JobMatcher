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

def update_candidate(cid, updates: dict):
    es.update(index="candidates", id=cid, doc=updates)
    print(f"Kandidat {cid} ažuriran")

def delete_candidate(cid):
    es.delete(index="candidates", id=cid)
    print(f"Kandidat {cid} obrisan")

def search_by_experience_and_city(payload: dict):
    filters = []

    if payload.get("min_years") is not None:
        filters.append({
            "range": {
                "years_experience": {
                    "gte": payload["min_years"]
                }
            }
        })

    if payload.get("city"):
        filters.append({
            "term": {
                "city": payload["city"]   # samo "city" posto je već keyword u mappingu
            }
        })

    if filters:
        query = {
            "query": {
                "bool": {
                    "filter": filters
                }
            }
        }
    else:
        query = {"query": {"match_all": {}}}

    sort = []
    if payload.get("min_years") is not None:
        sort.append({"years_experience": {"order": "desc"}})

    if sort:
        query["sort"] = sort

    if payload.get("min_years") is not None:
        query["aggs"] = {
            "avg_experience": {"avg": {"field": "years_experience"}}
        }

    return query


def search_by_skills_and_education(payload: dict):
    filters = []

    if payload.get("skills"):
        filters.append({
            "terms": {
                "skills": payload["skills"]
            }
        })

    if payload.get("education_level"):
        filters.append({
            "term": {
                "education_level": payload["education_level"]
            }
        })

    query = {
        "query": {
            "bool": {
                "filter": filters
               
            }
        },
        "sort": [
            {
                payload.get("sort_by", "years_experience"): {
                    "order": payload.get("order", "desc")
                }
            }
        ],
        "aggs": {
            "by_education_level": {
                "terms": {
                    "field": "education_level"
                }
            }
        }
    }

    return query

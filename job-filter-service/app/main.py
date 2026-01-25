import os
from fastapi import FastAPI
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from app.routers import candidates_router, job_ads_router

# ---- učitavanje .env ----
load_dotenv()

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")

# ---- Elasticsearch klijent ----
es = Elasticsearch(ELASTICSEARCH_HOST)

# ---- FastAPI app ----
app = FastAPI(title="Job Filter API")

app.include_router(candidates_router.router, tags=["Candidates"])
app.include_router(job_ads_router.router, tags=["Job Ads"])

@app.get("/health")
def health():
    return {
        "elasticsearch_host": ELASTICSEARCH_HOST,
        "es_alive": es.ping()
    }

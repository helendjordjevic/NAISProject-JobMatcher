import os
from elasticsearch import Elasticsearch
from fastapi import FastAPI

app = FastAPI()

es = Elasticsearch(
    os.getenv("ELASTICSEARCH_HOST")
)

@app.get("/health")
def health():
    return {
        "elasticsearch_host": os.getenv("ELASTICSEARCH_HOST"),
        "es_alive": es.ping()
    }

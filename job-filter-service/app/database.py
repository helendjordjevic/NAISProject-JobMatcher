import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")

es = Elasticsearch(ELASTICSEARCH_HOST)

import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from app.enums.job_ads_enums import ExperienceLevel, JobType, WorkMode

load_dotenv()  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

client = OpenAI(api_key=OPENAI_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pc.Index(INDEX_NAME)

def generate_job_embedding(title, description, experience_level, job_type, work_mode, city, country):
    text = f"{title}: {description}. Required level: {experience_level}, Job type: {job_type}, Work mode: {work_mode}, Location: {city}, {country}"
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


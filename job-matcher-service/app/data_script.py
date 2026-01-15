import os
import uuid
import random
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# -----------------------------
# Setup OpenAI client
# -----------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# Setup Pinecone client
# -----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# -----------------------------
# Predefinisani podaci
# -----------------------------
candidate_firstnames = ["Ana", "Marko", "Jelena", "Ivan", "Helena", "Petar", "Maja", "Nikola", "Sara", "Luka"]
candidate_lastnames = ["Petrovic", "Jovanovic", "Djordjevic", "Nikolic", "Stojanovic", "Markovic"]
education_levels = ["junior", "bachelor", "master"]
skills_pool = ["Python", "Docker", "FastAPI", "SQL", "Java", "React", "AWS", "Kubernetes", "Git"]
cities = ["Belgrade", "Novi Sad", "Nis", "Subotica", "Kragujevac"]
countries = ["Serbia"]

job_titles = ["Backend Engineer", "Frontend Developer", "Fullstack Developer", "Data Analyst", "DevOps Engineer"]
job_descriptions = [
    "Develop scalable backend services",
    "Work on frontend UI/UX",
    "Analyze data and generate reports",
    "Manage cloud infrastructure",
    "Implement APIs and microservices"
]
experience_levels = ["junior", "mid", "senior"]
job_types = ["full-time", "part-time", "internship", "contract"]
work_modes = ["remote", "onsite", "hybrid"]

# -----------------------------
# Helper function: OpenAI embedding
# -----------------------------
def generate_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# -----------------------------
# Helper function: prepare text for embedding
# -----------------------------
def candidate_text(firstname, lastname, skills, education, years_exp, city, country):
    return f"{firstname} {lastname}, Education: {education}, Skills: {', '.join(skills)}, Experience: {years_exp} years, Location: {city}, {country}"

def job_text(title, description, experience_level, job_type, work_mode, city, country):
    return f"{title}: {description}. Required level: {experience_level}, Job type: {job_type}, Work mode: {work_mode}, Location: {city}, {country}"

# -----------------------------
# Generate and insert candidates
# -----------------------------
for _ in range(200):
    firstname = random.choice(candidate_firstnames)
    lastname = random.choice(candidate_lastnames)
    education = random.choice(education_levels)
    years_exp = round(random.uniform(0.5, 10), 1)
    skills = random.sample(skills_pool, k=random.randint(1, 5))
    city = random.choice(cities)
    country = random.choice(countries)

    text_for_embedding = candidate_text(firstname, lastname, skills, education, years_exp, city, country)
    embedding_vector = generate_embedding(text_for_embedding)

    candidate = {
        "id": str(uuid.uuid4()),
        "values": embedding_vector,
        "metadata": {
            "firstname": firstname,
            "lastname": lastname,
            "education_level": education,
            "years_experience": years_exp,
            "skills": skills,
            "city": city,
            "country": country
        }
    }

    index.upsert(vectors=[candidate], namespace="candidates")

print("200 kandidata ubačeno u Pinecone!")

# -----------------------------
# Generate and insert job ads
# -----------------------------
for _ in range(200):
    title = random.choice(job_titles)
    description = random.choice(job_descriptions)
    experience_level = random.choice(experience_levels)
    job_type = random.choice(job_types)
    work_mode = random.choice(work_modes)
    city = random.choice(cities)
    country = random.choice(countries)

    text_for_embedding = job_text(title, description, experience_level, job_type, work_mode, city, country)
    embedding_vector = generate_embedding(text_for_embedding)

    job = {
        "id": str(uuid.uuid4()),
        "values": embedding_vector,
        "metadata": {
            "title": title,
            "description": description,
            "required_experience_level": experience_level,
            "job_type": job_type,
            "work_mode": work_mode,
            "city": city,
            "country": country
        }
    }

    index.upsert(vectors=[job], namespace="job_ads")

print("200 oglasa ubačeno u Pinecone!")

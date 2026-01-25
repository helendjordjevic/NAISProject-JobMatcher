# populate elasticsearch db with script data - fisrt added to sample data folder
import os
import uuid
import random
import json

# -----------------------------
# Folder gde se nalaze tvoji sample fajlovi
# -----------------------------
output_folder = "sample_data"
os.makedirs(output_folder, exist_ok=True)

# -----------------------------
# Predefinisani podaci
# -----------------------------
candidate_firstnames = ["Teodora", "Vuk", "Milica", "Stefan", "Lara", "Filip", "Katarina", "Mihailo", "Sara", "Nenad"]
candidate_lastnames = ["Ristic", "Savic", "Ilic", "Popovic", "Dragovic", "Milosevic"]
education_levels = ["junior", "bachelor", "master"]
skills_pool = ["Python", "Docker", "FastAPI", "SQL", "Java", "React", "AWS", "Kubernetes", "Git", "Node.js", "TypeScript", "Machine Learning"]
cities = ["Belgrade", "Novi Sad", "Nis", "Subotica", "Kragujevac", "Zrenjanin", "Sombor"]
countries = ["Serbia"]

job_titles = ["Backend Engineer", "Frontend Developer", "Fullstack Developer", "Data Analyst", "DevOps Engineer", "Cloud Architect", "Machine Learning Engineer", "QA Engineer"]
job_descriptions = [
    "Develop scalable backend services using modern frameworks",
    "Work on responsive frontend UI/UX design",
    "Analyze large datasets and generate actionable insights",
    "Manage cloud infrastructure and CI/CD pipelines",
    "Implement APIs and microservices with high availability",
    "Optimize database queries and ensure performance",
    "Design and deploy machine learning models",
    "Perform automated and manual QA testing for applications"
]
experience_levels = ["junior", "mid", "senior"]
job_types = ["full-time", "part-time", "internship", "contract"]
work_modes = ["remote", "onsite", "hybrid"]

NUM_CANDIDATES = 1000
NUM_JOBS = 1000

# -----------------------------
# Funkcija za generisanje kandidata u bulk formatu
# -----------------------------
def generate_candidates_bulk(num, filepath):
    with open(filepath, "w") as f:
        for _ in range(num):
            cid = str(uuid.uuid4())
            firstname = random.choice(candidate_firstnames)
            lastname = random.choice(candidate_lastnames)
            education = random.choice(education_levels)
            years_exp = round(random.uniform(0.5, 12), 1)
            skills = random.sample(skills_pool, k=random.randint(1, 6))
            city = random.choice(cities)
            country = random.choice(countries)

            f.write(json.dumps({"index": {"_index": "candidates", "_id": cid}}) + "\n")
            f.write(json.dumps({
                "candidate_id": cid,
                "firstname": firstname,
                "lastname": lastname,
                "education_level": education,
                "years_experience": years_exp,
                "skills": skills,
                "city": city,
                "country": country
            }) + "\n")

# -----------------------------
# Funkcija za generisanje oglasa u bulk formatu
# -----------------------------
def generate_jobs_bulk(num, filepath):
    with open(filepath, "w") as f:
        for _ in range(num):
            jid = str(uuid.uuid4())
            title = random.choice(job_titles)
            description = random.choice(job_descriptions)
            experience_level = random.choice(experience_levels)
            job_type = random.choice(job_types)
            work_mode = random.choice(work_modes)
            city = random.choice(cities)
            country = random.choice(countries)

            f.write(json.dumps({"index": {"_index": "job_ads", "_id": jid}}) + "\n")
            f.write(json.dumps({
                "job_id": jid,
                "title": title,
                "description": description,
                "required_experience_level": experience_level,
                "job_type": job_type,
                "work_mode": work_mode,
                "city": city,
                "country": country
            }) + "\n")

# -----------------------------
# Generisanje bulk fajlova
# -----------------------------
generate_candidates_bulk(NUM_CANDIDATES, os.path.join(output_folder, "candidates_sample.txt"))
generate_jobs_bulk(NUM_JOBS, os.path.join(output_folder, "job_ads_sample.txt"))

print(f"Gotovo! Fajlovi u '{output_folder}':")
print("- candidates_sample.txt")
print("- jobads_sample.txt")

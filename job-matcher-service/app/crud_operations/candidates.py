from urllib import response
import uuid

from app.enums.candidates_enums import EducationLevel, SKILLS_POOL
from app.database import index, client 

def generate_candidate_embedding(firstname, lastname, skills, education_level, years_experience, city, country):
    text = f"{firstname} {lastname}, Education: {education_level}, Skills: {', '.join(skills)}, Experience: {years_experience} years, Location: {city}, {country}"
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def create_candidate(firstname: str, lastname: str, skills: list[str], education_level: str, years_experience: float, city: str, country: str) -> str:
    if education_level not in [e.value for e in EducationLevel]:
        raise ValueError(f"Education level mora biti jedan od {[e.value for e in EducationLevel]}")
    if not all(skill in SKILLS_POOL for skill in skills):
        raise ValueError(f"Svi skills moraju biti iz predefinisanog skupa {SKILLS_POOL}")

    candidate_id = str(uuid.uuid4())
    embedding = generate_candidate_embedding(firstname, lastname, skills, education_level, years_experience, city, country)

    vector = {
        "id": candidate_id,
        "values": embedding,
        "metadata": {
            "firstname": firstname,
            "lastname": lastname,
            "skills": skills,
            "education_level": education_level,
            "years_experience": years_experience,
            "city": city,
            "country": country
        }
    }

    index.upsert(vectors=[vector], namespace="candidates")
    return candidate_id

def get_candidate_by_id(candidate_id: str) -> dict | None:
    response = index.fetch(ids=[candidate_id], namespace="candidates")
    if response.vectors:
        return response.vectors.get(candidate_id)
    return None

def delete_candidate(candidate_id: str) -> bool:
    response = index.delete(ids=[candidate_id], namespace="candidates")
    return True

def update_candidate(candidate_id: str, **kwargs) -> bool:
    """
    Može da se update-uje firstname, lastname, skills, education_level, years_experience, city, country
    """
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return False

    metadata = candidate['metadata']

    for key, value in kwargs.items():
        if key == "education_level" and value not in [e.value for e in EducationLevel]:
            raise ValueError(f"Education level mora biti jedan od {[e.value for e in EducationLevel]}")
        if key == "skills" and not all(skill in SKILLS_POOL for skill in value):
            raise ValueError(f"Svi skills moraju biti iz predefinisanog skupa {SKILLS_POOL}")
        metadata[key] = value

    embedding = generate_candidate_embedding(
        metadata["firstname"],
        metadata["lastname"],
        metadata["skills"],
        metadata["education_level"],
        metadata["years_experience"],
        metadata["city"],
        metadata["country"]
    )

    vector = {
        "id": candidate_id,
        "values": embedding,
        "metadata": metadata
    }

    index.upsert(vectors=[vector], namespace="candidates")
    return True

def generate_skills_embedding(skill_query: str):
    text = f"Skills: {skill_query}"
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def filter_candidates(
    skill_query: str | None = None,   
    education_level: str | None = None,
    min_years_experience: float | None = None,
    top_k: int = 200,

):
    filter_query = {}

    if education_level:
        filter_query["education_level"] = {"$eq": education_level}

    if min_years_experience is not None:
        filter_query["years_experience"] = {"$gte": min_years_experience}

# ako imamo skill generišem embedding za semantičko pretraživanje
    if skill_query:
        embedding = generate_skills_embedding(skill_query)
    else:
        # dummy vector
        embedding = [0.0] * 1536

    all_matches = []

    while True:
        response = index.query(
            namespace="candidates",
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_query if filter_query else None,
        )

        #print("Response:", response)
        print("Next token:", getattr(response, "next_token", None))
        print("Broj match-eva u ovom batch-u:", len(response.matches))

        all_matches = []
        for match in response.matches:
            match_dict = {
                "id": match.id,
                "metadata": match.metadata
            }
            if skill_query:
                match_dict["score"] = match.score
            all_matches.append(match_dict)

        return all_matches
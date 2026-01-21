import uuid

from app.enums.job_ads_enums import JobType, ExperienceLevel, WorkMode
from app.database import index, client 


def generate_job_embedding(title, description, experience_level, job_type, work_mode, city, country):
    text = f"{title}: {description}. Required level: {experience_level}, Job type: {job_type}, Work mode: {work_mode}, Location: {city}, {country}"
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def create_job_ad(title: str, description: str, experience_level: str, job_type: str, work_mode: str, city: str, country: str) -> str:
    if experience_level not in [e.value for e in ExperienceLevel]:
        raise ValueError(f"Experience level mora biti jedan od {[e.value for e in ExperienceLevel]}")
    if job_type not in [e.value for e in JobType]:
        raise ValueError(f"Job type mora biti jedan od {[e.value for e in JobType]}")
    if work_mode not in [e.value for e in WorkMode]:
        raise ValueError(f"Work mode mora biti jedan od {[e.value for e in WorkMode]}")

    job_id = str(uuid.uuid4())
    embedding = generate_job_embedding(title, description, experience_level, job_type, work_mode, city, country)

    vector = {
        "id": job_id,
        "values": embedding,
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

    index.upsert(vectors=[vector], namespace="job_ads")
    return job_id


def get_job_ad_by_id(job_id: str) -> dict | None:
    response = index.fetch(ids=[job_id], namespace="job_ads")
    if response.vectors:
        return response.vectors.get(job_id)
    return None

def delete_job_ad(job_id: str) -> bool:
    index.delete(ids=[job_id], namespace="job_ads")
    return True

def update_job_ad(job_id: str, **kwargs) -> bool:
    """
    Može da se update-uje: title, description, experience_level, job_type, work_mode, city, country
    """
    job = get_job_ad_by_id(job_id)
    if not job:
        return False

    metadata = job['metadata']

    for key, value in kwargs.items():
        if key == "experience_level" and value not in [e.value for e in ExperienceLevel]:
            raise ValueError(f"Experience level mora biti jedan od {[e.value for e in ExperienceLevel]}")
        if key == "job_type" and value not in [e.value for e in JobType]:
            raise ValueError(f"Job type mora biti jedan od {[e.value for e in JobType]}")
        if key == "work_mode" and value not in [e.value for e in WorkMode]:
            raise ValueError(f"Work mode mora biti jedan od {[e.value for e in WorkMode]}")
        metadata[key] = value

    embedding = generate_job_embedding(
        metadata["title"],
        metadata["description"],
        metadata["required_experience_level"],
        metadata["job_type"],
        metadata["work_mode"],
        metadata["city"],
        metadata["country"]
    )

    vector = {
        "id": job_id,
        "values": embedding,
        "metadata": metadata
    }

    index.upsert(vectors=[vector], namespace="job_ads")
    return True

def generate_job_title_embedding(title_query: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=f"Job title: {title_query}"
    )
    return response.data[0].embedding

def filter_job_ads(
    title_query: str | None = None,
    required_experience_level: ExperienceLevel | None = None,
    job_type: JobType | None = None,
    work_mode: WorkMode | None = None,
    top_k: int = 50
):
    filter_dict = {}

    if required_experience_level:
        filter_dict["required_experience_level"] = required_experience_level.value
    if job_type:
        filter_dict["job_type"] = job_type.value
    if work_mode:
        filter_dict["work_mode"] = work_mode.value

    if title_query:
        embedding = generate_job_title_embedding(title_query)
    else:
        embedding = [0.0] * 1536
        
    res = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        namespace="job_ads",
        filter=filter_dict if filter_dict else None
    )

    matches = []
    for match in res.matches:
        m = {
            "id": match.id,
            "title": match.metadata["title"],
            "description": match.metadata["description"],
            "required_experience_level": match.metadata["required_experience_level"],
            "job_type": match.metadata["job_type"],
            "work_mode": match.metadata["work_mode"],
            "city": match.metadata["city"],
            "country": match.metadata["country"],
        }
        if title_query and hasattr(match, "score"):
            m["score"] = match.score
        matches.append(m)

    return {
        "count": len(matches),
        "results": matches
    }
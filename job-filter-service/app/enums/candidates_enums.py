from enum import Enum

class EducationLevel(str, Enum):
    JUNIOR = "junior"
    BACHELOR = "bachelor"
    MASTER = "master"

SKILLS_POOL = ["Python", "Docker", "FastAPI", "SQL", "Java", "React", "AWS", "Kubernetes", "Git"]

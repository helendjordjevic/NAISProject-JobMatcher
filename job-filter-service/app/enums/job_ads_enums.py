from enum import Enum

class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"

class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"

class WorkMode(str, Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"

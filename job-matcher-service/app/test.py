from app.database import index

candidate_id = "5815cfbd-876b-4749-9742-7b8fc9e6c8d3"
res = index.fetch(ids=[candidate_id], namespace="candidates")
print(res)
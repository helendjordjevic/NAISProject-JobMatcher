from fastapi import FastAPI
from app.routers import candidates_router, job_ads_router

app = FastAPI(title="Job Matcher API")

app.include_router(candidates_router.router, tags=["Candidates"])
app.include_router(job_ads_router.router, tags=["Job Ads"])
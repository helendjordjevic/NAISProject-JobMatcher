from app.database import index
from fpdf import FPDF
from datetime import datetime
import os
from app.crud_operations.candidates import generate_skills_embedding

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

VECTOR_DIM = 1536
#############################################################
# query 1 - candidates report easy
def filter_candidates_for_report(
    skill_query: str | None = None,
    min_years_experience: int | None = None,
    top_k: int = 10
):
    """Vraća listu kandidata iz Pinecone po skill-u i minimalnom iskustvu"""
    filter_query = {}

    if min_years_experience is not None:
        filter_query["years_experience"] = {"$gte": min_years_experience}

    # semantičko pretraživanje po skill-u
    embedding = generate_skills_embedding(skill_query) if skill_query else [0.0] * 1536

    response = index.query(
        namespace="candidates",
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_query if filter_query else None
    )

    candidates = []
    for match in response.matches:
        md = match.metadata
        candidates.append({
            "firstname": md.get("firstname", ""),
            "lastname": md.get("lastname", ""),
            "education_level": md.get("education_level", ""),
            "years_experience": md.get("years_experience", 0),
            "skills": ", ".join(md.get("skills", [])),
            "city": md.get("city", ""),
            "country": md.get("country", ""),
            "score": match.score
        })

    return candidates

def generate_candidates_pdf(candidates, skills, min_years):
    """Generiše PDF izveštaj za Pinecone kandidate"""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Candidates Report - by skill and minimum years of experience", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Filters: skills={skills}, min_years={min_years}", ln=True)
    pdf.cell(0, 10, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    for idx, c in enumerate(candidates, start=1):

        candidate_block_height = 40  # aproksimacija visine jednog kandidata

        if pdf.get_y() + candidate_block_height > pdf.page_break_trigger:
            pdf.add_page() 

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Candidate {idx}", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, f"""\
            Name: {c['firstname']} {c['lastname']}
            Education: {c.get('education_level', 'N/A')}
            Experience: {c.get('years_experience', 0)} years
            Skills: {c.get('skills', '')}
            Location: {c.get('city', '')}, {c.get('country', '')}
            Score: {c.get('score', 0):.2f}
            """)
        pdf.ln(2)

    output_path = os.path.join(
        REPORTS_DIR,
        f"candidates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    pdf.output(output_path)
    return output_path

############################################################
# query 2 - jobs report easy
def filter_job_ads_for_report(job_types: list[str] | None = None, cities: list[str] | None = None, top_k: int = 10):
    """Vraća prvih top_k JobAds iz Pinecone po job_type i city"""
    filter_query = {}

    if job_types:
        filter_query["job_type"] = {"$in": job_types}
    if cities:
        filter_query["city"] = {"$in": cities}

    # dummy vektor, Pinecone zahteva vector, ali nam nije bitan za običan filter
    vector = [0.0] * VECTOR_DIM

    response = index.query(
        namespace="job_ads",
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter_query if filter_query else None
    )

    job_ads = []
    for match in response.matches:
        md = match.metadata
        job_ads.append({
            "title": md.get("title", ""),
            "description": md.get("description", ""),
            "job_type": md.get("job_type", ""),
            "work_mode": md.get("work_mode", ""),
            "city": md.get("city", ""),
            "country": md.get("country", ""),
            "score": match.score
        })

    return job_ads

def generate_job_ads_pdf(job_ads, job_type=None, city=None):
    """Generiše PDF izveštaj za Pinecone JobAds (max 10 oglasa, ne preseče oglas)"""
    pdf = FPDF()
    pdf.add_page()  # obavezno dodaj prvu stranicu
    pdf.set_auto_page_break(auto=False)  # isključujemo automatsko prelamanje

    # Header + filter info na prvoj strani
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Job Ads Report - by job type and city", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Filter applied: job_type={job_type}, city={city}", ln=True)
    pdf.cell(0, 8, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    max_ads = 10  # ograničavamo na prvih 10
    for idx, job in enumerate(job_ads[:max_ads], start=1):
        # aproksimacija visine jednog job ad bloka
        job_block_height = 60  # prilagodi po dužini teksta

        # Proveri da li ima mesta na stranici, ako nema, dodaj novu
        if pdf.get_y() + job_block_height > pdf.page_break_trigger:
            pdf.add_page()

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, f"Job Ad {idx}", ln=True)
        pdf.ln(2)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "Title:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, job.get("title", "N/A"))

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "Description:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, job.get("description", "N/A"))

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "Job Type / Work Mode:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"{job.get('job_type', 'N/A')} / {job.get('work_mode', 'N/A')}", ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "Location:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"{job.get('city', 'N/A')}, {job.get('country', 'N/A')}", ln=True)

        pdf.ln(8)  # razmak do sledećeg oglasa

    output_path = os.path.join(
        REPORTS_DIR,
        f"jobads_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    pdf.output(output_path)
    return output_path

#############################################################
# query 3 - job ads report complex
def filter_candidates_for_job_description(job_description: str, top_k: int = 5):
    """Vraća listu kandidata iz Pinecone na osnovu opisa posla"""
    # generišemo embedding za opis posla - koristim stari al isti je princip samo se prosledjuje desc a ne skill 

    if not job_description:
        raise ValueError("Job description is required for vector search")
    
    embedding = generate_skills_embedding(job_description)

    response = index.query(
        namespace="candidates",
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )

    candidates = []
    for match in response.matches:
        md = match.metadata
        candidates.append({
            "firstname": md.get("firstname", ""),
            "lastname": md.get("lastname", ""),
            "education_level": md.get("education_level", ""),
            "years_experience": md.get("years_experience", 0),
            "skills": ", ".join(md.get("skills", [])),
            "city": md.get("city", ""),
            "country": md.get("country", ""),
            "score": match.score
        })

    return candidates

def generate_candidates_by_job_pdf(candidates, job_description):
    """
    Generiše PDF izveštaj top kandidata za dati opis posla.
    Kandidati se ne prelamaju preko stranica.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, f"Top Candidates Report\nfor Job Description:\n{job_description}")
    pdf.ln(5)

    for idx, c in enumerate(candidates, start=1):
        candidate_block_height = 50  # aproksimacija visine jednog kandidata

        # Ako nema dovoljno prostora, dodaj novu stranicu
        if pdf.get_y() + candidate_block_height > pdf.page_break_trigger:
            pdf.add_page()

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Candidate {idx}", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, f"""
            Name: {c['firstname']} {c['lastname']}
            Education: {c.get('education_level', 'N/A')}
            Experience: {c.get('years_experience', 0)} years
            Skills: {c.get('skills', '')}
            Location: {c.get('city', '')}, {c.get('country', '')}
            Score (similarity): {c.get('score', 0):.2f} 
            """)
        pdf.ln(2)

    output_path = os.path.join(
        REPORTS_DIR,
        f"top_candidates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    pdf.output(output_path)
    return output_path



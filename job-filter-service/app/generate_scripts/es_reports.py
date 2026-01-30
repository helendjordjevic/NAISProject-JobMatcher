from app.database import es
from fpdf import FPDF
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ide iz generate_scripts/ u app/
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

#####################################################################
# query 1 - job ads easy 
def build_query_job_ads(filters):
    """Dinamički pravi ES query na osnovu prosleđenih filtera"""
    must_clauses = []
    if "job_type" in filters and filters["job_type"]:
        must_clauses.append({"match": {"job_type": filters["job_type"]}})
    if "experience_level" in filters and filters["experience_level"]:
        must_clauses.append({"match": {"required_experience_level": filters["experience_level"]}})
    return {"query": {"bool": {"must": must_clauses}}}

def fetch_job_ads(filters):
    """Vraća JobAds iz Elasticsearch po zadatim filterima"""
    query = build_query_job_ads(filters)
    res = es.search(index="job_ads", body=query, size=1000)
    hits = res["hits"]["hits"]
    jobs = []
    for hit in hits:
        source = hit["_source"]
        jobs.append({
            "title": source.get("title", ""),
            "description": source.get("description", ""),
            "work_mode": source.get("work_mode", ""),
            "city": source.get("city", ""),
            "country": source.get("country", "")
        })
    return jobs

def generate_pdf_job_ads(jobs, filters):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)  # isključujemo automatski break

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "JobAds Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    section_title = " - ".join([f"{k.replace('_',' ').capitalize()}: {v}" 
                                for k, v in filters.items() if v])
    pdf.cell(0, 10, f"Section: {section_title}", ln=True)
    pdf.ln(5)

    line_height = 6
    page_bottom = pdf.h - pdf.b_margin  # donja margina stranice

    for job in jobs:
        # Procena visine bloka
        pdf.set_font("Arial", "B", 12)
        title_height = line_height
        pdf.set_font("Arial", "", 12)
        # koliko linija description zauzima
        desc_lines = pdf.multi_cell(0, line_height, f"Description: {job['description']}", border=0, split_only=True)
        desc_height = line_height * len(desc_lines)
        other_height = line_height*3 + 10  # work_mode, city, country, razmak i separator
        block_height = title_height + desc_height + other_height

        # Page break ako blok ne stane
        if pdf.get_y() + block_height > page_bottom:
            pdf.add_page()

        # Crtanje bloka
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Title: {job['title']}", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, line_height, f"Description: {job['description']}")
        pdf.cell(0, 8, f"Work Mode: {job['work_mode']}", ln=True)
        pdf.cell(0, 8, f"City: {job['city']}", ln=True)
        pdf.cell(0, 8, f"Country: {job['country']}", ln=True)

        pdf.ln(5)
        pdf.cell(0, 0, "-"*100, ln=True)
        pdf.ln(5)

    # Sačuvaj PDF
    output_file = os.path.join(REPORTS_DIR, f"jobads_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(output_file)
    print(f"PDF generated successfully: {output_file}")
    return output_file


##########################################################
# query 2 - candidates easy
def build_query_candidates(filters):
    """Dinamički pravi ES query za Candidates na osnovu prosleđenih filtera"""
    must_clauses = []
    if "education_level" in filters and filters["education_level"]:
        must_clauses.append({"match": {"education_level": filters["education_level"]}})
    if "min_years_experience" in filters and filters["min_years_experience"] is not None:
        must_clauses.append({"range": {"years_experience": {"gte": filters["min_years_experience"]}}})
    return {"query": {"bool": {"must": must_clauses}}}

def fetch_candidates(filters):
    """Vraća kandidata iz Elasticsearch po zadatim filterima"""
    query = build_query_candidates(filters)
    res = es.search(index="candidates", body=query, size=1000)
    hits = res["hits"]["hits"]
    candidates = []
    for hit in hits:
        source = hit["_source"]
        candidates.append({
            "firstname": source.get("firstname", ""),
            "lastname": source.get("lastname", ""),
            "education_level": source.get("education_level", ""),
            "years_experience": source.get("years_experience", 0),
            "city": source.get("city", "")
        })
    return candidates

def generate_pdf_candidates(candidates, filters):
    """Generiše PDF izveštaj sa Candidates podacima u istom stilu kao JobAds"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Candidates Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    section_title = " - ".join([f"{k.replace('_',' ').capitalize()}: {v}" 
                                for k, v in filters.items() if v is not None])
    pdf.cell(0, 10, f"Section: {section_title}", ln=True)
    pdf.ln(5)

    line_height = 6
    page_bottom = pdf.h - pdf.b_margin

    for candidate in candidates:
        # procena visine bloka
        block_height = line_height*6 + 10  # title, lastname, education, experience, city, razmak/separator

        if pdf.get_y() + block_height > page_bottom:
            pdf.add_page()

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Firstname: {candidate['firstname']}", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Lastname: {candidate['lastname']}", ln=True)
        pdf.cell(0, 8, f"Education Level: {candidate['education_level']}", ln=True)
        pdf.cell(0, 8, f"Years Experience: {candidate['years_experience']}", ln=True)
        pdf.cell(0, 8, f"City: {candidate['city']}", ln=True)

        pdf.ln(5)
        pdf.cell(0, 0, "-"*100, ln=True)
        pdf.ln(5)

    output_file = os.path.join(REPORTS_DIR, f"candidates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(output_file)
    print(f"PDF generated successfully: {output_file}")
    return output_file

###################################################################
# query 3 - job ads complex 

def build_complex_jobads_query(description_keywords=None, work_mode=None):
    """
    Dinamički ES query:
    - description sadrži ključne reči
    - filter po work_mode
    """
    must_clauses = []

    # Tekstualni search
    if description_keywords:
        must_clauses.append({
            "match": {
                "description": description_keywords
            }
        })

    # Filter po work_mode
    if work_mode:
        must_clauses.append({
            "match": {
                "work_mode": work_mode
            }
        })

    return {
        "query": {
            "bool": {
                "must": must_clauses
            }
        }
    }

def fetch_complex_jobads(description_keywords=None, work_mode=None):
    query = build_complex_jobads_query(description_keywords, work_mode)
    res = es.search(index="job_ads", body=query, size=1000)
    hits = res["hits"]["hits"]
    jobs = []
    for hit in hits:
        source = hit["_source"]
        jobs.append({
            "title": source.get("title", ""),
            "description": source.get("description", ""),
            "work_mode": source.get("work_mode", ""),
            "city": source.get("city", ""),
            "country": source.get("country", "")
        })
    return jobs

def generate_complex_jobads_pdf(jobs, description_keywords, work_mode):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Complex JobAds Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 10, f"Description keywords: {description_keywords}", ln=True)
    pdf.cell(0, 10, f"Work Mode filter: {work_mode}", ln=True)
    pdf.ln(5)

    line_height = 6
    page_bottom = pdf.h - pdf.b_margin

    for job in jobs:
        # procena visine bloka
        desc_lines = pdf.multi_cell(0, line_height, f"Description: {job['description']}", border=0, split_only=True)
        block_height = line_height*(len(desc_lines)+5)

        if pdf.get_y() + block_height > page_bottom:
            pdf.add_page()

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Title: {job['title']}", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, line_height, f"Description: {job['description']}")
        pdf.cell(0, 8, f"Work Mode: {job['work_mode']}", ln=True)
        pdf.cell(0, 8, f"City: {job['city']}", ln=True)
        pdf.cell(0, 8, f"Country: {job['country']}", ln=True)

        pdf.ln(5)
        pdf.cell(0, 0, "-"*100, ln=True)
        pdf.ln(5)

    output_file = os.path.join(REPORTS_DIR, f"complex_jobads_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(output_file)
    print(f"PDF generated successfully: {output_file}")
    return output_file



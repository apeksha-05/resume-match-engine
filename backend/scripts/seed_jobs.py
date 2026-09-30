"""Seeds 20 fictional demo job postings.

All postings are clearly fictional and marked is_demo=True.
Run with: python -m scripts.seed_jobs
"""

from app.core.database import SessionLocal
from app.models.job import Job

JOBS: list[dict] = [
    dict(
        title="Backend Engineer",
        company="Acme Cloud",
        location="Bengaluru",
        work_mode="hybrid",
        min_years=3,
        description="Design and build REST APIs, write tests, and work with relational databases in an agile team.",
        required_skills=["Python", "FastAPI", "SQL", "REST APIs", "Docker", "AWS"],
        preferred_skills=["PostgreSQL", "Redis", "CI/CD"],
    ),
    dict(
        title="Junior Python Developer",
        company="Brightwave Labs",
        location="Remote (India)",
        work_mode="remote",
        min_years=0,
        description="Build internal tools and automation scripts in Python with guidance from senior engineers.",
        required_skills=["Python", "Git", "SQL"],
        preferred_skills=["FastAPI", "Docker"],
    ),
    dict(
        title="Data Engineering Intern",
        company="Northlake Analytics",
        location="Pune",
        work_mode="hybrid",
        min_years=0,
        description="Help build data pipelines and clean datasets for the analytics team.",
        required_skills=["Python", "SQL", "Pandas"],
        preferred_skills=["Airflow", "PostgreSQL"],
    ),
    dict(
        title="Full Stack Developer",
        company="Lumen Retail Tech",
        location="Jaipur",
        work_mode="onsite",
        min_years=2,
        description="Build customer-facing web features using React on the front end and Python services on the back end.",
        required_skills=["React", "TypeScript", "Python", "REST APIs"],
        preferred_skills=["Tailwind CSS", "PostgreSQL"],
    ),
    dict(
        title="Frontend Developer",
        company="Vividpath Media",
        location="Remote (India)",
        work_mode="remote",
        min_years=1,
        description="Implement responsive UI components and collaborate closely with designers.",
        required_skills=["JavaScript", "React", "HTML", "CSS"],
        preferred_skills=["TypeScript", "Tailwind CSS"],
    ),
    dict(
        title="DevOps Engineer",
        company="Skyline Systems",
        location="Hyderabad",
        work_mode="hybrid",
        min_years=3,
        description="Maintain CI/CD pipelines and manage containerized deployments on the cloud.",
        required_skills=["Docker", "Kubernetes", "AWS", "CI/CD"],
        preferred_skills=["Python", "Git"],
    ),
    dict(
        title="Machine Learning Intern",
        company="Northlake Analytics",
        location="Pune",
        work_mode="onsite",
        min_years=0,
        description="Assist in building and evaluating machine learning models for internal products.",
        required_skills=["Python", "Machine Learning", "Pandas", "NumPy"],
        preferred_skills=["SQL"],
    ),
    dict(
        title="Software Engineer, Platform",
        company="Acme Cloud",
        location="Bengaluru",
        work_mode="onsite",
        min_years=4,
        description="Own core platform services used across multiple product teams.",
        required_skills=["Java", "SQL", "REST APIs", "AWS"],
        preferred_skills=["Kubernetes", "Docker"],
    ),
    dict(
        title="Associate Software Engineer",
        company="Brightwave Labs",
        location="Remote (India)",
        work_mode="remote",
        min_years=0,
        description="Entry-level role building features across the stack under mentorship.",
        required_skills=["JavaScript", "Node.js", "SQL"],
        preferred_skills=["React", "MongoDB"],
    ),
    dict(
        title="Backend Developer (Django)",
        company="Coral Health Systems",
        location="Chennai",
        work_mode="hybrid",
        min_years=2,
        description="Build and maintain healthcare scheduling APIs using Django.",
        required_skills=["Python", "Django", "SQL", "REST APIs"],
        preferred_skills=["PostgreSQL", "Docker"],
    ),
    dict(
        title="Cloud Support Engineer",
        company="Skyline Systems",
        location="Remote (India)",
        work_mode="remote",
        min_years=1,
        description="Support customers troubleshooting cloud infrastructure issues.",
        required_skills=["AWS", "Git", "SQL"],
        preferred_skills=["Python", "Docker"],
    ),
    dict(
        title="Full Stack Intern",
        company="Vividpath Media",
        location="Remote (India)",
        work_mode="remote",
        min_years=0,
        description="Contribute to both frontend and backend of an internal content platform.",
        required_skills=["JavaScript", "React", "Node.js"],
        preferred_skills=["MongoDB", "TypeScript"],
    ),
    dict(
        title="Data Analyst",
        company="Coral Health Systems",
        location="Chennai",
        work_mode="onsite",
        min_years=1,
        description="Analyze operational data and build dashboards for hospital administrators.",
        required_skills=["SQL", "Python", "Pandas"],
        preferred_skills=["Machine Learning"],
    ),
    dict(
        title="Site Reliability Engineer",
        company="Acme Cloud",
        location="Bengaluru",
        work_mode="hybrid",
        min_years=3,
        description="Keep production systems reliable and improve deployment automation.",
        required_skills=["Kubernetes", "Docker", "Python", "AWS"],
        preferred_skills=["CI/CD", "Git"],
    ),
    dict(
        title="QA Automation Engineer",
        company="Lumen Retail Tech",
        location="Jaipur",
        work_mode="onsite",
        min_years=1,
        description="Build automated test suites for web applications.",
        required_skills=["Python", "Git", "SQL"],
        preferred_skills=["React", "CI/CD"],
    ),
    dict(
        title="Backend Engineer (Node)",
        company="Vividpath Media",
        location="Remote (India)",
        work_mode="remote",
        min_years=2,
        description="Build backend services for a media streaming platform.",
        required_skills=["Node.js", "JavaScript", "MongoDB", "REST APIs"],
        preferred_skills=["TypeScript", "Redis"],
    ),
    dict(
        title="Cloud Data Engineer",
        company="Northlake Analytics",
        location="Pune",
        work_mode="hybrid",
        min_years=2,
        description="Design data pipelines on cloud infrastructure for analytics workloads.",
        required_skills=["Python", "SQL", "AWS", "Airflow"],
        preferred_skills=["Docker", "Pandas"],
    ),
    dict(
        title="Software Engineering Intern",
        company="Coral Health Systems",
        location="Chennai",
        work_mode="hybrid",
        min_years=0,
        description="Support the engineering team on healthcare software features.",
        required_skills=["Python", "SQL", "Git"],
        preferred_skills=["Django", "REST APIs"],
    ),
    dict(
        title="Platform Engineer",
        company="Skyline Systems",
        location="Hyderabad",
        work_mode="onsite",
        min_years=4,
        description="Design and operate internal developer platform tooling.",
        required_skills=["Kubernetes", "AWS", "Python", "CI/CD"],
        preferred_skills=["Docker", "Git"],
    ),
    dict(
        title="Junior Frontend Engineer",
        company="Lumen Retail Tech",
        location="Jaipur",
        work_mode="onsite",
        min_years=0,
        description="Build and style UI components for an e-commerce storefront.",
        required_skills=["HTML", "CSS", "JavaScript", "React"],
        preferred_skills=["Tailwind CSS", "TypeScript"],
    ),
]


def run() -> None:
    db = SessionLocal()
    try:
        created = 0
        for job_data in JOBS:
            exists = (
                db.query(Job)
                .filter_by(title=job_data["title"], company=job_data["company"])
                .first()
            )
            if exists is None:
                db.add(Job(**job_data, is_demo=True, source="seed script"))
                created += 1

        db.commit()
        print(f"Seed complete. Created {created} job postings (of {len(JOBS)} defined).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
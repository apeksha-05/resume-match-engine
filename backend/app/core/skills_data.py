"""Canonical skill names, categories, and aliases.
Shared by the database seed script (scripts/seed_skills.py) and the mock
resume/JD extraction backend (app/services/mock_resume_extraction.py), so
both always agree on what counts as a recognized skill.
"""

# Canonical skill name -> (category, [aliases])
SKILLS: dict[str, tuple[str, list[str]]] = {
    "Python": ("language", ["py"]),
    "JavaScript": ("language", ["js"]),
    "TypeScript": ("language", ["ts"]),
    "SQL": ("language", []),
    "Java": ("language", []),
    "C++": ("language", ["cpp", "c plus plus"]),
    "FastAPI": ("framework", []),
    "React": ("framework", ["react.js", "reactjs"]),
    "Node.js": ("framework", ["nodejs", "node"]),
    "Django": ("framework", []),
    "Flask": ("framework", []),
    "PostgreSQL": ("database", ["postgres"]),
    "MySQL": ("database", []),
    "MongoDB": ("database", ["mongo"]),
    "Redis": ("database", []),
    "REST APIs": ("concept", ["rest api", "restful api", "rest"]),
    "Git": ("tool", []),
    "Docker": ("tool", []),
    "Kubernetes": ("tool", ["k8s"]),
    "AWS": ("cloud", ["amazon web services"]),
    "Azure": ("cloud", []),
    "GCP": ("cloud", ["google cloud", "google cloud platform"]),
    "CI/CD": ("practice", ["ci cd", "continuous integration"]),
    "Pandas": ("library", []),
    "NumPy": ("library", []),
    "Airflow": ("tool", ["apache airflow"]),
    "Tailwind CSS": ("framework", ["tailwind"]),
    "HTML": ("language", ["html5"]),
    "CSS": ("language", ["css3"]),
    "Machine Learning": ("concept", ["ml"]),
}
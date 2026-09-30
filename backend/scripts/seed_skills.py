"""Seeds the skills and skill_aliases tables.

Run with: python -m scripts.seed_skills
"""

from app.core.database import SessionLocal
from app.models.skill import Skill, SkillAlias

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


def run() -> None:
    db = SessionLocal()
    try:
        created_skills = 0
        created_aliases = 0

        for canonical_name, (category, aliases) in SKILLS.items():
            skill = db.query(Skill).filter_by(canonical_name=canonical_name).first()
            if skill is None:
                skill = Skill(canonical_name=canonical_name, category=category)
                db.add(skill)
                db.flush()  # assigns skill.id before we reference it below
                created_skills += 1

            for alias_text in aliases:
                normalized = alias_text.strip().lower()
                existing_alias = db.query(SkillAlias).filter_by(alias=normalized).first()
                if existing_alias is None:
                    db.add(SkillAlias(alias=normalized, skill_id=skill.id))
                    created_aliases += 1

        db.commit()
        print(f"Seed complete. Created {created_skills} skills and {created_aliases} aliases.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
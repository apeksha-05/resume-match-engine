"""Mock learning roadmap generator, based on missing required skills.
Uses generic, category-based learning steps rather than AI-personalized
advice. See mock_suggestions.py for the same honesty rationale.
"""

from app.core.skills_data import SKILLS
from app.schemas.feedback import RoadmapItem

MAX_ROADMAP_ITEMS = 4

# Generic first-step templates by skill category. A real LLM integration
# could tailor these far more specifically to the person's existing skills.
CATEGORY_STEPS: dict[str, list[str]] = {
    "language": [
        "Complete an interactive tutorial covering core syntax and data structures.",
        "Build a small project using this language end to end.",
        "Read the official style guide and apply it to your project.",
    ],
    "framework": [
        "Follow the official 'getting started' guide and build the sample app.",
        "Recreate one of your existing projects using this framework.",
        "Read the framework's documentation on testing and best practices.",
    ],
    "database": [
        "Learn basic setup, connection, and query syntax.",
        "Integrate it into one of your existing projects.",
        "Practice common operations: joins, indexes, and basic performance tuning.",
    ],
    "cloud": [
        "Create a free-tier account and explore the console.",
        "Deploy a simple project using this cloud provider.",
        "Study the provider's core certification exam outline as a study guide.",
    ],
    "tool": [
        "Install it and complete the official quickstart tutorial.",
        "Use it in one of your existing projects.",
        "Learn common commands or workflows used in real teams.",
    ],
    "concept": [
        "Study the fundamentals through a reputable free course.",
        "Apply the concept in a small practice project.",
        "Read how it's used in production systems via case studies or blog posts.",
    ],
    "practice": [
        "Learn the fundamentals of this practice through documentation or a course.",
        "Set it up for one of your existing projects.",
        "Study how established teams implement it, via blog posts or open-source examples.",
    ],
    "library": [
        "Work through the library's official quickstart or tutorial.",
        "Use it in a small data or scripting task.",
        "Read example notebooks or projects that use it.",
    ],
}

DEFAULT_STEPS = [
    "Find the official documentation or a reputable course and learn the basics.",
    "Apply it in a small practice project.",
    "Review how it's commonly used in real-world projects.",
]

ESTIMATED_WEEKS_BY_CATEGORY: dict[str, int] = {
    "language": 4,
    "framework": 2,
    "database": 2,
    "cloud": 3,
    "tool": 2,
    "concept": 3,
    "practice": 2,
    "library": 1,
}


def generate_roadmap_mock(missing_required_skills: list[str]) -> list[RoadmapItem]:
    roadmap: list[RoadmapItem] = []

    for skill_name in missing_required_skills[:MAX_ROADMAP_ITEMS]:
        category_info = SKILLS.get(skill_name)
        category = category_info[0] if category_info else "concept"

        roadmap.append(
            RoadmapItem(
                skill=skill_name,
                reason=(
                    f"Required by this job and not currently shown on your resume, "
                    f"so it's a skill to learn rather than one you've demonstrated."
                ),
                steps=CATEGORY_STEPS.get(category, DEFAULT_STEPS),
                estimated_weeks=ESTIMATED_WEEKS_BY_CATEGORY.get(category, 3),
            )
        )

    return roadmap
from pydantic import BaseModel, Field


class EvidencedSkill(BaseModel):
    name: str = Field(description="The skill name, as close to standard naming as possible")
    evidence: str = Field(description="The exact snippet from the resume text that mentions this skill")


class WorkExperience(BaseModel):
    job_title: str
    company: str
    duration: str = Field(description="As written in the resume, e.g. 'Jan 2024 - Present'")
    responsibilities: list[str] = Field(description="Bullet points describing the role, copied or lightly condensed from the resume")


class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: str | None = None
    field_of_study: str | None = None


class Project(BaseModel):
    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)


class Certification(BaseModel):
    name: str
    issuer: str | None = None
    year: str | None = None


class ParsedResume(BaseModel):
    """The full structured resume, extracted and validated from raw PDF text.
    Every field must be grounded in the resume's actual text. Nothing is invented."""

    skills: list[EvidencedSkill] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    job_titles_held: list[str] = Field(
        default_factory=list, description="Distinct job titles found across work experience"
    )


class ResumeExtractionOut(BaseModel):
    filename: str
    word_count: int
    parsed: ParsedResume
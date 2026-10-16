from pydantic import BaseModel


class AccountSummaryOut(BaseModel):
    resumes: int
    analyses: int
    job_descriptions: int

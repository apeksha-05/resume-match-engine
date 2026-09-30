from pydantic import BaseModel


class WeightsOut(BaseModel):
    skills: float
    semantic: float
    experience: float
    education: float
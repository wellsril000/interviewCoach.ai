"""Models related to job description analysis."""
from typing import List

from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    """Incoming request containing the raw job description text."""

    job_description: str = Field(..., description="Full job description text to analyze")


class JobAnalysisResult(BaseModel):
    """Structured job analysis returned to the frontend."""

    skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    competencies: List[str] = Field(default_factory=list)
    values: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    summary: str = Field("", description="Concise summary of the role")

    model_config = {
        "json_schema_extra": {
            "example": {
                "skills": ["Python", "FastAPI", "System Design"],
                "responsibilities": ["Build APIs", "Collaborate with product"],
                "competencies": ["Leadership", "Communication"],
                "values": ["Customer obsession"],
                "themes": ["Scalability", "Cross-functional partnership"],
                "summary": "You will lead API development for a rapidly growing SaaS company.",
            }
        }
    }

"""Interview flow related models."""
from typing import Literal, List

from pydantic import BaseModel, Field

from .job_models import JobAnalysisResult

InterviewMode = Literal["behavioral", "general", "role"]


class StartInterviewRequest(BaseModel):
    """Payload for initializing an interview session."""

    mode: InterviewMode
    job_analysis: JobAnalysisResult


class StartInterviewResponse(BaseModel):
    """Response returned when an interview session begins."""

    session_id: str
    mode: InterviewMode
    question: str
    job_analysis: JobAnalysisResult


class STARBreakdown(BaseModel):
    """STAR method breakdown of an answer."""

    situation: str = Field("", description="Context for the story")
    task: str = Field("", description="Goal or responsibility")
    action: str = Field("", description="Actions taken")
    result: str = Field("", description="Outcome of the actions")


class EvaluateAnswerRequest(BaseModel):
    """Payload for analyzing an interview response."""

    session_id: str
    question: str
    answer: str


class EvaluateAnswerResponse(BaseModel):
    """Structured feedback for the provided answer."""

    star: STARBreakdown
    strengths: List[str]
    weaknesses: List[str]
    fit_summary: str
    score: int = Field(..., ge=1, le=5)
    improvements: List[str]
    next_question: str

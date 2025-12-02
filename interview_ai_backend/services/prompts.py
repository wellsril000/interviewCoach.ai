"""Prompt builders to keep instructions consistent."""
from __future__ import annotations

import json
from typing import Any, Dict

from models.job_models import JobAnalysisResult


def build_job_analysis_prompt(job_description: str) -> str:
    """Prompt LLM to extract structured insights from a job description."""

    return (
        f"Read the following job description and extract the requested information.\n"
        f"Return ONLY valid minified JSON with the keys: skills, responsibilities, competencies, values, themes, summary.\n"
        f"Each list must contain concise bullet phrases (max 12 words each). The summary must be a single sentence.\n\n"
        f"Job Description:\n"
        f"{job_description}\n"
    )


def build_role_question_prompt(job_analysis: JobAnalysisResult) -> str:
    """Prompt LLM to craft a role-specific interview question."""

    context = json.dumps(job_analysis.model_dump(), indent=2)
    return (
        "Given the analyzed job data below, craft ONE thoughtful role-specific interview question\n"
        "that probes the candidate's fit for the themes and responsibilities. Return JSON like:\n"
        '{"question": "..."}\n\n'
        f"Job Analysis:\n{context}\n"
    )


def build_star_prompt(
    *,
    question: str,
    answer: str,
    job_analysis: JobAnalysisResult,
    mode: str,
    include_next_question: bool,
) -> str:
    """Prompt the LLM to evaluate an answer using the STAR method."""

    job_json = json.dumps(job_analysis.model_dump(), indent=2)
    next_q_instruction = (
        "Include a `next_question` field with a follow-up question aligned to the job themes."
        if include_next_question
        else "Do NOT include `next_question`."
    )

    return (
        "You are an expert interview coach analyzing a candidate's answer.\n"
        "Use the STAR method and evaluate the response to the provided question.\n"
        f"Return ONLY JSON with keys: star, strengths, weaknesses, fit_summary, score, improvements"
        f"{', next_question' if include_next_question else ''}.\n"
        "score must be an integer between 1 and 5.\n"
        "STAR must contain situation, task, action, result fields.\n"
        f"{next_q_instruction}\n\n"
        f"Interview mode: {mode}\n"
        "Job analysis:\n"
        f"{job_json}\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
    )

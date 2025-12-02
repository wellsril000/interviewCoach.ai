"""Primary API routes for the Interview AI backend."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from models.job_models import JobAnalysisRequest, JobAnalysisResult
from models.interview_models import (
    EvaluateAnswerRequest,
    EvaluateAnswerResponse,
    STARBreakdown,
    StartInterviewRequest,
    StartInterviewResponse,
)
from services.interview_manager import (
    BEHAVIORAL_QUESTIONS,
    GENERAL_QUESTIONS,
    InterviewManager,
)
from services.llm_client import LLMClient
from services import prompts

router = APIRouter()
llm_client = LLMClient()
interview_manager = InterviewManager()


@router.post("/analyze-job", response_model=JobAnalysisResult)
async def analyze_job(payload: JobAnalysisRequest) -> JobAnalysisResult:
    """Analyze a job description and return structured JSON."""

    prompt = prompts.build_job_analysis_prompt(payload.job_description)
    try:
        data = await llm_client.request_json(prompt)
    except (RuntimeError, ValueError):
        data = _fallback_job_analysis(payload.job_description)
    except Exception as exc:  # pragma: no cover - network errors
        raise HTTPException(status_code=500, detail=f"Job analysis failed: {exc}") from exc

    normalized = _normalize_job_analysis(data)
    return JobAnalysisResult(**normalized)


@router.post("/start-interview", response_model=StartInterviewResponse)
async def start_interview(payload: StartInterviewRequest) -> StartInterviewResponse:
    """Kick off an interview session and return the first question."""

    if payload.mode not in {"behavioral", "general", "role"}:
        raise HTTPException(status_code=400, detail="Unsupported interview mode")

    if payload.mode == "behavioral":
        question = BEHAVIORAL_QUESTIONS[0]
    elif payload.mode == "general":
        question = GENERAL_QUESTIONS[0]
    else:
        question = await _generate_role_question(payload.job_analysis)

    session_id = interview_manager.create_session(payload.mode, payload.job_analysis, question)
    return StartInterviewResponse(
        session_id=session_id,
        mode=payload.mode,
        question=question,
        job_analysis=payload.job_analysis,
    )


@router.post("/evaluate-answer", response_model=EvaluateAnswerResponse)
async def evaluate_answer(payload: EvaluateAnswerRequest) -> EvaluateAnswerResponse:
    """Evaluate an answer, return STAR feedback, and provide the next question."""

    try:
        session = interview_manager.get_session(payload.session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    include_next_question = session.mode == "role"
    prompt = prompts.build_star_prompt(
        question=payload.question,
        answer=payload.answer,
        job_analysis=session.job_analysis,
        mode=session.mode,
        include_next_question=include_next_question,
    )

    try:
        evaluation = await llm_client.request_json(prompt)
    except (RuntimeError, ValueError):
        evaluation = _fallback_star_response(payload.question, payload.answer, session.job_analysis)
    except Exception as exc:  # pragma: no cover - network errors
        raise HTTPException(status_code=500, detail=f"Answer evaluation failed: {exc}") from exc

    star_block = evaluation.get("star", {})
    star = STARBreakdown(
        situation=star_block.get("situation", ""),
        task=star_block.get("task", ""),
        action=star_block.get("action", ""),
        result=star_block.get("result", ""),
    )
    strengths = _ensure_list(evaluation.get("strengths"))
    weaknesses = _ensure_list(evaluation.get("weaknesses"))
    fit_summary = evaluation.get("fit_summary", "")
    score = _clamp_score(evaluation.get("score"))
    improvements = _ensure_list(evaluation.get("improvements"))

    if session.mode == "role":
        next_question = evaluation.get("next_question")
        if not next_question:
            next_question = await _generate_role_question(session.job_analysis)
        interview_manager.record_question(session.session_id, next_question)
    else:
        next_question = interview_manager.next_fixed_question(session.session_id)

    return EvaluateAnswerResponse(
        star=star,
        strengths=strengths,
        weaknesses=weaknesses,
        fit_summary=fit_summary,
        score=score,
        improvements=improvements,
        next_question=next_question,
    )


def _normalize_job_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the job analysis payload has every required key."""

    normalized = {
        "skills": _ensure_list(data.get("skills")),
        "responsibilities": _ensure_list(data.get("responsibilities")),
        "competencies": _ensure_list(data.get("competencies")),
        "values": _ensure_list(data.get("values")),
        "themes": _ensure_list(data.get("themes")),
        "summary": (data.get("summary") or "").strip(),
    }

    if not normalized["summary"] and normalized["responsibilities"]:
        normalized["summary"] = normalized["responsibilities"][0]
    return normalized


async def _generate_role_question(job_analysis: JobAnalysisResult) -> str:
    prompt = prompts.build_role_question_prompt(job_analysis)
    try:
        response = await llm_client.request_json(prompt)
    except (RuntimeError, ValueError):
        return _fallback_role_question(job_analysis)
    question = response.get("question")
    if not question:
        return _fallback_role_question(job_analysis)
    return question.strip()


def _ensure_list(value: Any) -> List[str]:
    """Normalize inputs into a list of trimmed strings."""

    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _clamp_score(value: Any) -> int:
    """Clamp the score to the required 1-5 range."""

    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 3
    return max(1, min(5, score))


def _fallback_job_analysis(job_description: str) -> Dict[str, Any]:
    """Provide a deterministic job analysis when the LLM is unavailable."""

    lines = [line.strip("•- ").strip() for line in job_description.splitlines() if line.strip()]
    sentences = [segment.strip() for segment in re.split(r"[.\\n]", job_description) if segment.strip()]

    keywords = _extract_keywords(job_description)
    skills = keywords[:6]
    responsibilities = lines[:6] or sentences[:6]

    competencies = [kw for kw in keywords if kw.lower().endswith(("ship", "ment"))][:4]
    if len(competencies) < 2:
        competencies.extend([kw for kw in keywords if kw not in competencies][: (4 - len(competencies))])

    values = [phrase for phrase in lines if any(word in phrase.lower() for word in ["value", "culture", "mission"])]
    if not values:
        values = [f"Emphasis on {kw.lower()} excellence" for kw in keywords[:2]]

    themes = [kw for kw in keywords if kw.lower() not in {k.lower() for k in skills}][:3]
    summary = sentences[0] if sentences else "Review the full job description for details."

    return {
        "skills": skills or ["Communication", "Problem solving"],
        "responsibilities": responsibilities or ["Deliver high-quality work", "Collaborate across teams"],
        "competencies": competencies or ["Leadership", "Execution"],
        "values": values or ["Customer focus", "Integrity"],
        "themes": themes or ["Impact", "Ownership"],
        "summary": summary,
    }


def _fallback_role_question(job_analysis: JobAnalysisResult) -> str:
    focus_pool = job_analysis.themes or job_analysis.responsibilities or ["impact"]
    focus = focus_pool[0]
    return f"How have you demonstrated {focus.lower()} in your previous roles?"


def _fallback_star_response(
    question: str, answer: str, job_analysis: JobAnalysisResult
) -> Dict[str, Any]:
    """Deterministic placeholder for STAR feedback."""

    word_count = len(answer.split())
    score = 5 if word_count > 180 else 4 if word_count > 120 else 3 if word_count > 60 else 2

    strengths = [
        "Clear narrative structure" if word_count > 80 else "Concise overview",
        f"Relates to {job_analysis.themes[0]}" if job_analysis.themes else "Shows ownership",
    ]
    weaknesses = [
        "Could include more measurable outcomes" if word_count < 200 else "",
        "Add more detail on the result" if "result" not in answer.lower() else "",
    ]
    weaknesses = [w for w in weaknesses if w]

    improvements = [
        "Incorporate quantifiable impact metrics",
        "Tie the story back to the employer's current priorities",
    ]

    star = {
        "situation": answer[:120] + "..." if len(answer) > 120 else answer,
        "task": "Clarify the specific goal or expectation you owned.",
        "action": "Highlight 2-3 concrete actions you personally led.",
        "result": "Describe the measurable outcome and what you learned.",
    }

    return {
        "star": star,
        "strengths": strengths,
        "weaknesses": weaknesses or ["Could add richer detail"],
        "fit_summary": job_analysis.summary or "Demonstrate alignment with the employer's themes.",
        "score": score,
        "improvements": improvements,
    }


def _extract_keywords(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z+]{3,}", text)
    unique: List[str] = []
    for token in tokens:
        word = token.capitalize()
        if word not in unique:
            unique.append(word)
    return unique

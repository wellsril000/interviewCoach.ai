"""Helpers for managing question banks and lightweight sessions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.job_models import JobAnalysisResult

BEHAVIORAL_QUESTIONS = [
    "Tell me about a time you faced a challenge at work or school.",
    "Describe a time when you had to work under pressure.",
    "Tell me about a time you took initiative.",
    "Describe a time you worked on a team project.",
    "Tell me about a conflict you had and how you resolved it.",
    "Describe a time you solved a complex problem.",
    "Tell me about a time you had to learn something quickly.",
    "Describe a time you made a mistake and how you handled it.",
    "Tell me about a time you had to persuade someone.",
    "Describe a time you showed leadership.",
]

GENERAL_QUESTIONS = [
    "Tell me about yourself.",
    "Why do you want this job?",
    "Why this company?",
    "What are your strengths?",
    "What is a weakness you're working on?",
]


@dataclass
class InterviewSessionState:
    """In-memory representation of an interview session."""

    session_id: str
    mode: str
    job_analysis: JobAnalysisResult
    pointer: int = 1  # index for the next fixed question (first question already served)
    asked_questions: List[str] = field(default_factory=list)


class InterviewManager:
    """Provides question banks and tracks lightweight session state."""

    def __init__(self) -> None:
        self._sessions: Dict[str, InterviewSessionState] = {}
        self._banks = {
            "behavioral": BEHAVIORAL_QUESTIONS,
            "general": GENERAL_QUESTIONS,
        }

    def create_session(self, mode: str, job_analysis: JobAnalysisResult, initial_question: str) -> str:
        session_id = str(uuid.uuid4())
        state = InterviewSessionState(
            session_id=session_id,
            mode=mode,
            job_analysis=job_analysis,
            pointer=1,
            asked_questions=[initial_question],
        )
        self._sessions[session_id] = state
        return session_id

    def get_session(self, session_id: str) -> InterviewSessionState:
        if session_id not in self._sessions:
            raise ValueError("Session not found")
        return self._sessions[session_id]

    def next_fixed_question(self, session_id: str) -> str:
        state = self.get_session(session_id)
        bank = self._banks.get(state.mode)
        if not bank:
            raise ValueError("No fixed question bank for this mode")
        question = bank[state.pointer % len(bank)]
        state.pointer += 1
        state.asked_questions.append(question)
        return question

    def record_question(self, session_id: str, question: str) -> None:
        state = self.get_session(session_id)
        state.asked_questions.append(question)

    def last_question(self, session_id: str) -> Optional[str]:
        state = self.get_session(session_id)
        return state.asked_questions[-1] if state.asked_questions else None

    def close_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

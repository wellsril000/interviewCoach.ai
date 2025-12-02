import type {
  EvaluateAnswerResponse,
  InterviewMode,
  JobAnalysisResult,
  StartInterviewResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = 'Request failed';
    try {
      const errorBody = await response.json();
      detail = errorBody.detail ?? detail;
    } catch (error) {
      // no-op, keep default detail
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function analyzeJob(jobDescription: string): Promise<JobAnalysisResult> {
  return postJson<JobAnalysisResult>('/analyze-job', { job_description: jobDescription });
}

export function startInterview(
  mode: InterviewMode,
  jobAnalysis: JobAnalysisResult,
): Promise<StartInterviewResponse> {
  return postJson<StartInterviewResponse>('/start-interview', {
    mode,
    job_analysis: jobAnalysis,
  });
}

export function evaluateAnswer(
  sessionId: string,
  question: string,
  answer: string,
): Promise<EvaluateAnswerResponse> {
  return postJson<EvaluateAnswerResponse>('/evaluate-answer', {
    session_id: sessionId,
    question,
    answer,
  });
}

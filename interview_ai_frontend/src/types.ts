export type InterviewMode = 'behavioral' | 'general' | 'role';

export interface JobAnalysisResult {
  skills: string[];
  responsibilities: string[];
  competencies: string[];
  values: string[];
  themes: string[];
  summary: string;
}

export interface StartInterviewResponse {
  session_id: string;
  mode: InterviewMode;
  question: string;
  job_analysis: JobAnalysisResult;
}

export interface StarBreakdown {
  situation: string;
  task: string;
  action: string;
  result: string;
}

export interface EvaluateAnswerResponse {
  star: StarBreakdown;
  strengths: string[];
  weaknesses: string[];
  fit_summary: string;
  score: number;
  improvements: string[];
  next_question: string;
}

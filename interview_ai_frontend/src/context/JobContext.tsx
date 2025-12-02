import { createContext, useContext, useState } from 'react';
import type { JobAnalysisResult, InterviewMode } from '../types';
import type { ReactNode } from 'react';

interface JobContextValue {
  jobAnalysis: JobAnalysisResult | null;
  setJobAnalysis: (analysis: JobAnalysisResult | null) => void;
  mode: InterviewMode | null;
  setMode: (mode: InterviewMode | null) => void;
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
  currentQuestion: string | null;
  setCurrentQuestion: (question: string | null) => void;
}

const JobContext = createContext<JobContextValue | undefined>(undefined);

export function JobProvider({ children }: { children: ReactNode }) {
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysisResult | null>(null);
  const [mode, setMode] = useState<InterviewMode | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);

  const value: JobContextValue = {
    jobAnalysis,
    setJobAnalysis,
    mode,
    setMode,
    sessionId,
    setSessionId,
    currentQuestion,
    setCurrentQuestion,
  };

  return <JobContext.Provider value={value}>{children}</JobContext.Provider>;
}

export function useJobContext(): JobContextValue {
  const context = useContext(JobContext);
  if (!context) {
    throw new Error('useJobContext must be used inside a JobProvider');
  }
  return context;
}

import { useState } from 'react';
import UploadPage from './pages/UploadPage';
import ModeSelectPage from './pages/ModeSelectPage';
import InterviewPage from './pages/InterviewPage';
import { useJobContext } from './context/JobContext';
import type { JobAnalysisResult } from './types';

type Page = 'upload' | 'mode' | 'interview';

export default function App() {
  const [page, setPage] = useState<Page>('upload');
  const { jobAnalysis, setJobAnalysis, setMode, setSessionId, setCurrentQuestion } = useJobContext();

  const handleAnalyzed = (analysis: JobAnalysisResult) => {
    setJobAnalysis(analysis);
    setPage('mode');
  };

  const handleInterviewStarted = () => {
    setPage('interview');
  };

  const handleReset = () => {
    setJobAnalysis(null);
    setMode(null);
    setSessionId(null);
    setCurrentQuestion(null);
    setPage('upload');
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Interview AI Coach</h1>
          <p className="subtitle">Analyze jobs, pick a mode, practice smarter.</p>
        </div>
        {jobAnalysis && (
          <button className="ghost" onClick={handleReset}>
            Start over
          </button>
        )}
      </header>

      <main>
        {page === 'upload' && <UploadPage onAnalyzed={handleAnalyzed} />}
        {page === 'mode' && jobAnalysis && (
          <ModeSelectPage onBack={() => setPage('upload')} onStarted={handleInterviewStarted} />
        )}
        {page === 'interview' && jobAnalysis && <InterviewPage onExit={handleReset} />}
      </main>
    </div>
  );
}

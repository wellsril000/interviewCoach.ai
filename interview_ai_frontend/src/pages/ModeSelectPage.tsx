import { useState } from 'react';
import { startInterview } from '../api';
import { useJobContext } from '../context/JobContext';
import type { InterviewMode } from '../types';

type Props = {
  onBack: () => void;
  onStarted: () => void;
};

const MODES: { key: InterviewMode; label: string; description: string }[] = [
  {
    key: 'behavioral',
    label: 'Behavioral',
    description: 'Classic behavioral prompts from a curated question bank.',
  },
  {
    key: 'general',
    label: 'General',
    description: 'Warm-up prompts covering motivation and fit questions.',
  },
  {
    key: 'role',
    label: 'Role-specific',
    description: 'LLM generates questions tied to the analyzed themes.',
  },
];

export default function ModeSelectPage({ onBack, onStarted }: Props) {
  const { jobAnalysis, setMode, setSessionId, setCurrentQuestion } = useJobContext();
  const [loadingMode, setLoadingMode] = useState<InterviewMode | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!jobAnalysis) return null;

  const handleSelect = async (mode: InterviewMode) => {
    setLoadingMode(mode);
    setError(null);
    try {
      const response = await startInterview(mode, jobAnalysis);
      setMode(response.mode);
      setSessionId(response.session_id);
      setCurrentQuestion(response.question);
      onStarted();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start interview');
    } finally {
      setLoadingMode(null);
    }
  };

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Select Interview Mode</h2>
          <p className="muted">Summary: {jobAnalysis.summary}</p>
        </div>
        <button className="ghost" onClick={onBack}>
          Edit job
        </button>
      </div>

      <div className="chip-row">
        {jobAnalysis.themes.slice(0, 4).map((theme) => (
          <span className="chip" key={theme}>
            {theme}
          </span>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <div className="mode-grid">
        {MODES.map((mode) => (
          <button
            key={mode.key}
            className="mode-card"
            onClick={() => handleSelect(mode.key)}
            disabled={!!loadingMode}
          >
            <div>
              <h3>{mode.label}</h3>
              <p>{mode.description}</p>
            </div>
            <span className="mode-action">{loadingMode === mode.key ? 'Starting…' : 'Start'}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

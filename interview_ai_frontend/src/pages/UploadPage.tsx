import { FormEvent, useState } from 'react';
import { analyzeJob } from '../api';
import type { JobAnalysisResult } from '../types';

type Props = {
  onAnalyzed: (analysis: JobAnalysisResult) => void;
};

export default function UploadPage({ onAnalyzed }: Props) {
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!jobDescription.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeJob(jobDescription.trim());
      onAnalyzed(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to analyze job description');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>Upload Job Description</h2>
      <p className="muted">Paste the job description below and let the AI extract what matters.</p>
      <form className="vertical" onSubmit={handleSubmit}>
        <textarea
          rows={12}
          value={jobDescription}
          onChange={(event) => setJobDescription(event.target.value)}
          placeholder="Paste the job description here..."
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading || jobDescription.trim().length < 30}>
          {loading ? 'Analyzing…' : 'Analyze Job'}
        </button>
      </form>
    </section>
  );
}

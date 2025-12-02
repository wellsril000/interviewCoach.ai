import { FormEvent, useState } from 'react';
import { evaluateAnswer } from '../api';
import { useJobContext } from '../context/JobContext';
import AnswerFeedback from '../components/AnswerFeedback';
import type { EvaluateAnswerResponse } from '../types';

type Props = {
  onExit: () => void;
};

export default function InterviewPage({ onExit }: Props) {
  const { jobAnalysis, currentQuestion, sessionId, setCurrentQuestion } = useJobContext();
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<EvaluateAnswerResponse | null>(null);

  if (!jobAnalysis || !sessionId || !currentQuestion) return null;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!answer.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await evaluateAnswer(sessionId, currentQuestion, answer.trim());
      setFeedback(result);
      setCurrentQuestion(result.next_question);
      setAnswer('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to evaluate answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Interview Practice</h2>
          <p className="muted">{jobAnalysis.summary}</p>
        </div>
        <button className="ghost" onClick={onExit}>
          Finish session
        </button>
      </div>

      <div className="question-box">
        <p className="label">Current question</p>
        <h3>{currentQuestion}</h3>
      </div>

      <form className="vertical" onSubmit={handleSubmit}>
        <textarea
          rows={8}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          placeholder="Type your answer here using the STAR method..."
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading || answer.trim().length < 20}>
          {loading ? 'Evaluating…' : 'Submit Answer'}
        </button>
      </form>

      {feedback && (
        <div className="feedback-wrapper">
          <AnswerFeedback data={feedback} />
          <div className="next-question">
            <p className="label">Next question</p>
            <p>{feedback.next_question}</p>
          </div>
        </div>
      )}
    </section>
  );
}

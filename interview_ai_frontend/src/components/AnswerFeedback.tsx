import type { EvaluateAnswerResponse } from '../types';

type Props = {
  data: EvaluateAnswerResponse;
};

export default function AnswerFeedback({ data }: Props) {
  return (
    <div className="feedback-card">
      <div className="star-grid">
        <div>
          <p className="label">Situation</p>
          <p>{data.star.situation || 'Add a brief context to ground the story.'}</p>
        </div>
        <div>
          <p className="label">Task</p>
          <p>{data.star.task || 'Clarify the outcome you had to deliver.'}</p>
        </div>
        <div>
          <p className="label">Action</p>
          <p>{data.star.action || 'Highlight the actions you personally owned.'}</p>
        </div>
        <div>
          <p className="label">Result</p>
          <p>{data.star.result || 'Quantify the business impact or learning.'}</p>
        </div>
      </div>

      <div className="feedback-columns">
        <div>
          <h4>Strengths</h4>
          <ul>
            {data.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Weaknesses</h4>
          <ul>
            {data.weaknesses.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="score-row">
        <div>
          <p className="label">Score</p>
          <p className="score">{data.score} / 5</p>
        </div>
        <div>
          <p className="label">Fit summary</p>
          <p>{data.fit_summary}</p>
        </div>
      </div>

      <div>
        <h4>Improvement ideas</h4>
        <ul>
          {data.improvements.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { JobProvider } from './context/JobContext';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <JobProvider>
      <App />
    </JobProvider>
  </React.StrictMode>,
);

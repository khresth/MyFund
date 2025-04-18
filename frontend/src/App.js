import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [decisions, setDecisions] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:3000/decisions')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch decisions');
        }
        return response.json();
      })
      .then(data => setDecisions(data))
      .catch(err => setError(err.message));
  }, []);

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="App">
      <h1>AI Hedge Fund Decisions</h1>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Buffett Decision</th>
            <th>Sentiment Decision</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(decisions).map(([ticker, { buffett, sentiment }]) => (
            <tr key={ticker}>
              <td>{ticker}</td>
              <td>{buffett}</td>
              <td>{sentiment}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
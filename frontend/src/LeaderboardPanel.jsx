import React from 'react';

function LeaderboardPanel({ entries }) {
  return (
    <section className="panel">
      <h2>Rankings</h2>
      <ul className="list-card">
        {entries.map((entry, index) => (
          <li key={entry.user_id} className="list-item">
            <div>
              <strong>#{index + 1} {entry.username}</strong>
              <div className="muted">{entry.score} pts</div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default LeaderboardPanel;

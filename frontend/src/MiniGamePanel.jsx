import React from 'react';

function MiniGamePanel({ score }) {
  return (
    <section className="panel">
      <h2>Mini games</h2>
      <div className="profile-card">
        <strong>Quiz challenge</strong>
        <div className="muted">Latest score: {score || 0}</div>
      </div>
    </section>
  );
}

export default MiniGamePanel;

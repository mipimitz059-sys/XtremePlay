import React from 'react';

function AdminPanel({ reports }) {
  return (
    <section className="panel">
      <h2>Admin moderation</h2>
      <ul className="list-card">
        {reports.map((report) => (
          <li key={report.id} className="list-item">
            <div>
              <strong>{report.reason}</strong>
              <div className="muted">Report id: {report.id}</div>
            </div>
            <button>Review</button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default AdminPanel;

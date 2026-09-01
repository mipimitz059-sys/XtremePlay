import React from 'react';

function ActivityPanel({ notifications, rewards }) {
  return (
    <section className="panel">
      <h2>Activity</h2>
      <ul className="list-card">
        {notifications.map((item, index) => (
          <li key={`${item.message}-${index}`} className="list-item">
            <div>{item.message}</div>
          </li>
        ))}
        {rewards.map((reward, index) => (
          <li key={`${reward.label}-${index}`} className="list-item">
            <div>{reward.label} +{reward.coins} coins</div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default ActivityPanel;

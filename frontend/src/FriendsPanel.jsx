import React from 'react';

function FriendsPanel({ friends }) {
  return (
    <section className="panel">
      <h2>Friends</h2>
      <ul className="list-card">
        {friends.map((friend) => (
          <li key={friend.id} className="list-item">
            <div>
              <strong>{friend.display_name}</strong>
              <div className="muted">@{friend.username}</div>
            </div>
            <span className="muted">{friend.status}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default FriendsPanel;

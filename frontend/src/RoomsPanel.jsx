import React from 'react';

function RoomsPanel({ rooms }) {
  return (
    <section className="panel">
      <h2>Rooms</h2>
      <ul className="list-card">
        {rooms.map((room) => (
          <li key={room.id} className="list-item">
            <div>
              <strong>{room.name}</strong>
              <div className="muted">{room.theme}</div>
            </div>
            <span className="muted">{room.participants?.length || 0} joined</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default RoomsPanel;

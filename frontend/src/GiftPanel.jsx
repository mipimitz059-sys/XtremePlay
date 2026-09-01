import React from 'react';

function GiftPanel({ catalog }) {
  return (
    <section className="panel">
      <h2>Gift catalog</h2>
      <ul className="list-card">
        {catalog.map((item) => (
          <li key={item.id} className="list-item">
            <div>
              <strong>{item.name}</strong>
              <div className="muted">{item.description}</div>
            </div>
            <span className="muted">{item.price} XPL</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default GiftPanel;

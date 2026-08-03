import React from 'react';

function WalletPanel({ wallet }) {
  return (
    <section className="panel">
      <h2>Wallet</h2>
      <div className="profile-card">
        <strong>{wallet?.balance || 0} XPL</strong>
        <div className="muted">Virtual currency ready for gifts and rewards</div>
      </div>
    </section>
  );
}

export default WalletPanel;

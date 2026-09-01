import React from 'react';

function ProfilePanel({ user, profile }) {
  return (
    <section className="panel">
      <h2>Profile</h2>
      <div className="profile-card">
        <strong>{user?.display_name || 'Player'}</strong>
        <div className="muted">@{user?.username}</div>
        <p>{profile?.bio || 'A rising XtremePlay star.'}</p>
        <div className="muted">Location: {profile?.location || 'Unknown'}</div>
      </div>
    </section>
  );
}

export default ProfilePanel;

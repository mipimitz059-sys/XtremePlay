import { useEffect, useMemo, useState } from 'react';
import AdminPanel from './AdminPanel';
import ActivityPanel from './ActivityPanel';
import FriendsPanel from './FriendsPanel';
import LeaderboardPanel from './LeaderboardPanel';
import ProfilePanel from './ProfilePanel';

const initialState = {
  user: null,
  token: localStorage.getItem('xtremeplay_token') || '',
  users: [],
  friends: [],
  notifications: [],
};

function App() {
  const [state, setState] = useState({ ...initialState, reports: [], profile: {}, rewards: [], notifications: [] });
  const [query, setQuery] = useState('');
  const [form, setForm] = useState({ username: '', display_name: '', email: '', password: '' });

  useEffect(() => {
    if (!state.token) return;
    fetch('/api/v1/me', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, user: payload.user })))
      .catch(() => {});

    fetch('/api/v1/admin/reports', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, reports: payload.reports || [] })))
      .catch(() => {});

    fetch('/api/v1/notifications', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, notifications: payload.notifications || [] })))
      .catch(() => {});

    fetch('/api/v1/friends', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, friends: payload.friends || [] })))
      .catch(() => {});

    fetch('/api/v1/leaderboard', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, entries: payload.entries || [] })))
      .catch(() => {});
  }, [state.token]);

  const heroTitle = useMemo(() => {
    if (state.user?.display_name) return `Welcome back, ${state.user.display_name}`;
    return 'XtremePlay';
  }, [state.user]);

  const handleRegister = async (event) => {
    event.preventDefault();
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    const payload = await response.json();
    if (payload.token) {
      localStorage.setItem('xtremeplay_token', payload.token);
      setState((current) => ({ ...current, token: payload.token, user: payload.user }));
    }
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    const response = await fetch(`/api/v1/users/search?query=${encodeURIComponent(query)}`, {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const payload = await response.json();
    setState((current) => ({ ...current, users: payload.users || [] }));
  };

  const handleFriendRequest = async (targetUsername) => {
    const response = await fetch('/api/v1/friends/requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify({ target_username: targetUsername }),
    });
    if (response.ok) {
      const payload = await response.json();
      setState((current) => ({ ...current, notifications: [...current.notifications, payload] }));
    }
  };

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Social gaming • Phase 2</p>
          <h1>{heroTitle}</h1>
          <p>Meet friends, discover rooms, and build your circle in a responsive XtremePlay experience.</p>
        </div>
        <div className="hero-pill">Realtime + Social</div>
      </header>

      <main className="content-grid">
        <section className="panel">
          <h2>Create account</h2>
          <form onSubmit={handleRegister} className="stack">
            <input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="Username" />
            <input value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} placeholder="Display name" />
            <input value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} placeholder="Email" />
            <input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Password" />
            <button type="submit">Join XtremePlay</button>
          </form>
        </section>

        <section className="panel">
          <h2>Find players</h2>
          <form onSubmit={handleSearch} className="search-row">
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by username" />
            <button type="submit">Search</button>
          </form>
          <ul className="list-card">
            {state.users.map((user) => (
              <li key={user.id} className="list-item">
                <div>
                  <strong>{user.display_name}</strong>
                  <div className="muted">@{user.username}</div>
                </div>
                <button onClick={() => handleFriendRequest(user.username)}>Add</button>
              </li>
            ))}
          </ul>
        </section>

        {state.user ? <ProfilePanel user={state.user} profile={state.profile} /> : null}
        <FriendsPanel friends={state.friends} />
        <ActivityPanel notifications={state.notifications} rewards={state.rewards} />
        <LeaderboardPanel entries={state.entries || []} />
        {state.reports?.length ? <AdminPanel reports={state.reports} /> : null}
      </main>
    </div>
  );
}

export default App;

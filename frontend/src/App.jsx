import { useEffect, useMemo, useState } from 'react';
import AdminPanel from './AdminPanel';
import ActivityPanel from './ActivityPanel';
import FriendsPanel from './FriendsPanel';
import LeaderboardPanel from './LeaderboardPanel';
import ProfilePanel from './ProfilePanel';
import RoomsPanel from './RoomsPanel';
import WalletPanel from './WalletPanel';
import GiftPanel from './GiftPanel';
import MiniGamePanel from './MiniGamePanel';

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
  const [profileForm, setProfileForm] = useState({ bio: '', location: '', theme: 'midnight' });
  const [roomForm, setRoomForm] = useState({ name: '', theme: 'casual' });
  const [familyForm, setFamilyForm] = useState({ name: '', tag: 'PHX' });
  const [notificationText, setNotificationText] = useState('');
  const [voiceForm, setVoiceForm] = useState({ name: '', topic: 'general' });
  const [messageText, setMessageText] = useState('');
  const [selectedRoomId, setSelectedRoomId] = useState('');
  const [messages, setMessages] = useState([]);

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

    fetch('/api/v1/rooms', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, rooms: payload.rooms || [] })))
      .catch(() => {});

    fetch('/api/v1/wallet', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, wallet: payload.wallet || { balance: 0, ledger: [] } })))
      .catch(() => {});

    fetch('/api/v1/gifts/catalog', { headers: { Authorization: `Bearer ${state.token}` } })
      .then((response) => response.json())
      .then((payload) => setState((current) => ({ ...current, catalog: payload.catalog || [] })))
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

  const handleProfileSave = async (event) => {
    event.preventDefault();
    const response = await fetch('/api/v1/profile/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify(profileForm),
    });
    const payload = await response.json();
    if (payload.profile) {
      setState((current) => ({ ...current, profile: payload.profile }));
    }
  };

  const handleClaimDailyReward = async () => {
    const response = await fetch('/api/v1/rewards/daily', {
      method: 'POST',
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const payload = await response.json();
    if (payload.balance) {
      setState((current) => ({ ...current, wallet: { ...(current.wallet || {}), balance: payload.balance } }));
    }
  };

  const handleCreateRoom = async (event) => {
    event.preventDefault();
    const response = await fetch('/api/v1/rooms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify(roomForm),
    });
    const payload = await response.json();
    if (payload.room) {
      setSelectedRoomId(payload.room.id);
      setState((current) => ({ ...current, rooms: [...(current.rooms || []), payload.room] }));
    }
  };

  const handleSendMessage = async (event) => {
    event.preventDefault();
    if (!selectedRoomId || !messageText.trim()) return;
    const response = await fetch(`/api/v1/rooms/${selectedRoomId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify({ text: messageText }),
    });
    const payload = await response.json();
    if (payload.message) {
      setMessages((current) => [...current, payload.message]);
      setMessageText('');
    }
  };

  const handleCreateVoiceRoom = async (event) => {
    event.preventDefault();
    const response = await fetch('/api/v1/voice-rooms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify(voiceForm),
    });
    const payload = await response.json();
    if (payload.voice_room) {
      setState((current) => ({ ...current, voiceRooms: [...(current.voiceRooms || []), payload.voice_room] }));
    }
  };

  const handleCreateFamily = async (event) => {
    event.preventDefault();
    const response = await fetch('/api/v1/families', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify(familyForm),
    });
    const payload = await response.json();
    if (payload.family) {
      setState((current) => ({ ...current, families: [...(current.families || []), payload.family] }));
    }
  };

  const handleSendNotification = async (event) => {
    event.preventDefault();
    const response = await fetch('/api/v1/notifications/general', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: JSON.stringify({ message: notificationText }),
    });
    const payload = await response.json();
    if (payload.notification) {
      setState((current) => ({ ...current, notifications: [...(current.notifications || []), payload.notification] }));
      setNotificationText('');
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
        <section className="panel">
          <h2>Profile settings</h2>
          <form onSubmit={handleProfileSave} className="stack">
            <input value={profileForm.bio} onChange={(event) => setProfileForm({ ...profileForm, bio: event.target.value })} placeholder="Bio" />
            <input value={profileForm.location} onChange={(event) => setProfileForm({ ...profileForm, location: event.target.value })} placeholder="Location" />
            <input value={profileForm.theme} onChange={(event) => setProfileForm({ ...profileForm, theme: event.target.value })} placeholder="Theme" />
            <button type="submit">Save profile</button>
          </form>
        </section>
        <FriendsPanel friends={state.friends} />
        <ActivityPanel notifications={state.notifications} rewards={state.rewards} />
        <LeaderboardPanel entries={state.entries || []} />
        <section className="panel">
          <h2>Create room</h2>
          <form onSubmit={handleCreateRoom} className="stack">
            <input value={roomForm.name} onChange={(event) => setRoomForm({ ...roomForm, name: event.target.value })} placeholder="Room name" />
            <input value={roomForm.theme} onChange={(event) => setRoomForm({ ...roomForm, theme: event.target.value })} placeholder="Theme" />
            <button type="submit">Create room</button>
          </form>
        </section>
        <section className="panel">
          <h2>Realtime chat</h2>
          <form onSubmit={handleSendMessage} className="stack">
            <input value={messageText} onChange={(event) => setMessageText(event.target.value)} placeholder="Type a message" />
            <button type="submit">Send</button>
          </form>
          <ul className="list-card">
            {messages.map((message, index) => (
              <li key={`${message}-${index}`} className="list-item"><div>{message}</div></li>
            ))}
          </ul>
        </section>
        <section className="panel">
          <h2>Voice rooms</h2>
          <form onSubmit={handleCreateVoiceRoom} className="stack">
            <input value={voiceForm.name} onChange={(event) => setVoiceForm({ ...voiceForm, name: event.target.value })} placeholder="Voice room name" />
            <input value={voiceForm.topic} onChange={(event) => setVoiceForm({ ...voiceForm, topic: event.target.value })} placeholder="Topic" />
            <button type="submit">Open room</button>
          </form>
        </section>
        <section className="panel">
          <h2>Families</h2>
          <form onSubmit={handleCreateFamily} className="stack">
            <input value={familyForm.name} onChange={(event) => setFamilyForm({ ...familyForm, name: event.target.value })} placeholder="Clan name" />
            <input value={familyForm.tag} onChange={(event) => setFamilyForm({ ...familyForm, tag: event.target.value })} placeholder="Tag" />
            <button type="submit">Create clan</button>
          </form>
        </section>
        <section className="panel">
          <h2>Notifications</h2>
          <form onSubmit={handleSendNotification} className="stack">
            <input value={notificationText} onChange={(event) => setNotificationText(event.target.value)} placeholder="Notification message" />
            <button type="submit">Send</button>
          </form>
        </section>
        <section className="panel">
          <h2>Analytics snapshot</h2>
          <div className="muted">Rooms: {state.analytics?.room_count || 0}</div>
          <div className="muted">Members: {state.analytics?.user_count || 0}</div>
          <div className="muted">Daily rewards: {state.analytics?.daily_reward_claims || 0}</div>
        </section>
        <RoomsPanel rooms={state.rooms || []} />
        <WalletPanel wallet={state.wallet} />
        <section className="panel">
          <h2>Daily rewards</h2>
          <button onClick={handleClaimDailyReward}>Claim reward</button>
        </section>
        <GiftPanel catalog={state.catalog || []} />
        <MiniGamePanel score={state.minigameScore} />
        {state.reports?.length ? <AdminPanel reports={state.reports} /> : null}
      </main>
    </div>
  );
}

export default App;

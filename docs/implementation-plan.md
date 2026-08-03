# XtremePlay implementation plan

## Repository audit

### Project structure
- The repository currently contains a minimal Quart application in [main.py](main.py) and a placeholder plugin contract in [openapi.yaml](openapi.yaml).
- There is no backend persistence layer, no frontend application, and no deployment configuration yet.
- The current code is a good foundation for an API server but not for a full social gaming platform.

### Dependencies
- Current runtime dependencies are Quart and Quart-CORS.
- Testing support was added via pytest for Phase 1 verification.
- Future phases should introduce a database ORM, authentication libraries, and possibly WebSocket support.

### Security issues
- The current server uses in-memory state only and has no authentication strategy beyond a temporary token flow.
- There is no rate limiting, input validation layer, or secret management.
- Production readiness requires environment-based secrets, CORS configuration, and structured error handling.

### Missing backend capabilities
- No persistent database.
- No real user profile management beyond a basic registration flow.
- No room persistence, messaging, voice, gifts, wallet, or moderation systems.
- No admin tooling.

### Missing frontend capabilities
- No client application, UI shell, or state management layer.
- A web-based experience will be required for social features, rooms, leaderboards, and wallet views.

### Database schema
Phase 1 should establish a schema for:
- users
- sessions
- rooms
- room_members
- leaderboard_entries
- notifications
- wallet_transactions

### Authentication
- Phase 1 introduced a simple bearer-token flow to support authenticated profile and room access.
- Phase 2 should replace this with hashed passwords, refresh tokens, and role-based access controls.

### Realtime messaging
- Not implemented yet.
- Recommended approach: WebSocket gateway for chat and presence updates.

### Voice rooms
- Not implemented yet.
- Recommended stack: WebRTC or a managed voice provider such as LiveKit.

### Coins and wallet
- Phase 1 includes a basic wallet balance field.
- Phase 2 should introduce transaction history, credits, and redemption flows.

### Gifts
- Not yet implemented.
- Planned as a social economy feature tied to wallet transactions and room interactions.

### Leaderboards
- Phase 1 includes an in-memory leaderboard entry model.
- Future iterations should persist rankings and support per-game or per-room leaderboards.

### Family system
- Not implemented.
- Planned as a social graph feature with invite-based family rooms and shared moderation controls.

### Relationships
- Not implemented.
- Planned as follow/friend/block relationships with status-based user discovery.

### Notifications
- Not implemented.
- Planned as in-app, push, and email delivery channels with preference controls.

### Mini games
- Not implemented.
- Planned as lightweight games with score submission and shared room events.

### Admin dashboard
- Not implemented.
- Planned as a protected admin console for moderation, metrics, and user management.

### Deployment readiness
- Current project is not containerized or deployment-ready.
- Phase 1 should be followed by Dockerfiles, environment configuration, health checks, and CI workflows.

## Prioritized roadmap

### Phase 1 — foundation and API skeleton
Status: complete in this repository snapshot.
- Add health endpoint.
- Add basic registration and authenticated profile flow.
- Add room creation/listing.
- Add leaderboard score updates and listings.
- Add regression tests.

### Phase 2 — persistence and security
- Replace in-memory storage with a PostgreSQL-backed data layer.
- Add password-based auth and refresh token handling.
- Add input validation and structured error handling.
- Add role-based admin access.

### Phase 3 — realtime social layer
- Add WebSocket support for chat, presence, and room events.
- Add notification delivery and room participation updates.

### Phase 4 — economy and social systems
- Add wallet transactions, gifting, and coin-based interactions.
- Add relationship and family management flows.

### Phase 5 — voice, mini games, and admin UX
- Integrate voice room support.
- Add mini games and leaderboard variants.
- Ship an admin dashboard.

### Phase 6 — deployment and scale
- Add Docker, CI/CD, and environment-based configuration.
- Add observability, backups, and deployment playbooks.

## Recommended implementation order
1. Harden the API contract and add validation.
2. Introduce a database layer and persistent models.
3. Add realtime chat and presence.
4. Add wallet, gifts, and family systems.
5. Add voice rooms and admin tooling.
6. Prepare production deployment assets.

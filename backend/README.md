# XtremePlay backend notes

This backend is an initial production-oriented API skeleton for Phase 2. It preserves the existing Quart service while introducing a structured domain model and contract surface for authentication, presence, social graph search, and notifications.

## Planned production evolution
- Replace in-memory storage with Convex-backed persistence and normalized schema.
- Integrate Hercules Auth for secure sign-in and access control.
- Add WebSocket presence and realtime updates.
- Introduce a reusable React UI with a mobile-first XtremePlay-inspired design language.

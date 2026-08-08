from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class ConnectionManager:
    """
    In-memory room connection manager.

    One instance per Quart process.

    Later this can be replaced by Redis Pub/Sub
    without changing websocket routes.
    """

    def __init__(self):

        self._rooms: dict[
            int,
            set[Any],
        ] = defaultdict(set)

        self._lock = asyncio.Lock()

    async def connect(
        self,
        room_id: int,
        websocket,
    ):

        async with self._lock:
            self._rooms[room_id].add(websocket)

    async def disconnect(
        self,
        room_id: int,
        websocket,
    ):

        async with self._lock:

            sockets = self._rooms.get(room_id)

            if sockets is None:
                return

            sockets.discard(websocket)

            if not sockets:
                self._rooms.pop(room_id, None)

    async def broadcast(
        self,
        room_id: int,
        payload: dict,
    ):

        sockets = list(
            self._rooms.get(room_id, ())
        )

        dead = []

        for ws in sockets:

            try:
                await ws.send_json(payload)

            except Exception:
                dead.append(ws)

        if dead:

            async with self._lock:

                current = self._rooms.get(room_id)

                if current is None:
                    return

                for ws in dead:
                    current.discard(ws)

                if not current:
                    self._rooms.pop(room_id, None)

    def room_count(
        self,
        room_id: int,
    ) -> int:

        return len(
            self._rooms.get(room_id, ())
        )

    def total_connections(
        self,
    ) -> int:

        return sum(
            len(sockets)
            for sockets in self._rooms.values()
        )


manager = ConnectionManager()
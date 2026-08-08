from __future__ import annotations

from backend.websocket.handlers import PingHandler


class PacketDispatcher:
    """
    Dispatch websocket packets to the
    correct handler.

    Every realtime feature simply registers
    a new handler here.
    """

    def __init__(self):

        self.handlers = {
            "ping": PingHandler(),
        }

    async def dispatch(
        self,
        packet: dict,
    ) -> bool:

        packet_type = packet.get("type")

        handler = self.handlers.get(packet_type)

        if handler is None:
            return False

        await handler.handle(packet)

        return True


dispatcher = PacketDispatcher()
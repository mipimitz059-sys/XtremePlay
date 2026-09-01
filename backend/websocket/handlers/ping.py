from quart import websocket


class PingHandler:
    """
    Heartbeat handler.

    Client:
        {"type": "ping"}

    Server:
        {"type": "pong"}
    """

    async def handle(
        self,
        packet: dict,
    ):

        await websocket.send_json(
            {
                "type": "pong",
            }
        )
from __future__ import annotations

from typing import Any

from backend.chat.service import send_message


class MessageEngine:
    """
    Central message processing pipeline.

    All message transports (REST, WebSocket, future voice
    signaling, bots, etc.) should use this engine instead of
    writing directly to the database.
    """

    def process_message(
        self,
        *,
        room_id: int,
        user_id: int,
        message: str,
    ) -> dict[str, Any]:
        """
        Validate, persist and return a message.

        Future pipeline stages:
            - Rate limiting
            - Spam detection
            - Profanity filtering
            - AI moderation
            - XP rewards
            - Coin rewards
            - Notifications
            - Analytics
        """

        # Current persistence implementation.
        result = send_message(
            room_id=room_id,
            user_id=user_id,
            message_text=message,
        )

        if not result.get("success"):
            return result

        # Hook point for future processors.

        return result


engine = MessageEngine()
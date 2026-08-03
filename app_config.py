import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    allowed_origin: str
    convex_url: Optional[str] = None
    hercules_auth_url: Optional[str] = None
    hercules_client_id: Optional[str] = None
    hercules_client_secret: Optional[str] = None
    enable_mock_auth: bool = True
    enable_mock_realtime: bool = True
    enable_mock_wallet: bool = True


def load_config() -> AppConfig:
    return AppConfig(
        allowed_origin=os.getenv("XTREMEPLAY_ALLOWED_ORIGIN", "https://chat.openai.com"),
        convex_url=os.getenv("CONVEX_URL"),
        hercules_auth_url=os.getenv("HERCULES_AUTH_URL"),
        hercules_client_id=os.getenv("HERCULES_AUTH_CLIENT_ID"),
        hercules_client_secret=os.getenv("HERCULES_AUTH_CLIENT_SECRET"),
        enable_mock_auth=not bool(os.getenv("HERCULES_AUTH_URL")),
        enable_mock_realtime=not bool(os.getenv("CONVEX_URL")),
        enable_mock_wallet=not bool(os.getenv("CONVEX_URL")),
    )

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ConvexAdapter:
    url: Optional[str]
    enabled: bool = False

    def __post_init__(self):
        self.enabled = bool(self.url)

    def save(self, collection: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"collection": collection, "payload": payload, "mode": "mock"}
        raise NotImplementedError("Production Convex integration requires a configured URL")


@dataclass
class HerculesAuthAdapter:
    auth_url: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    enabled: bool = False

    def __post_init__(self):
        self.enabled = bool(self.auth_url and self.client_id and self.client_secret)

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return {"mode": "mock", "username": username}
        raise NotImplementedError("Production Hercules Auth integration requires credentials")


@dataclass
class RealtimeTransportAdapter:
    enabled: bool

    def publish(self, room_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"room_id": room_id, "payload": payload, "mode": "mock"}


@dataclass
class WalletProviderAdapter:
    enabled: bool

    def credit(self, user_id: str, amount: int, reason: str) -> Dict[str, Any]:
        return {"user_id": user_id, "amount": amount, "reason": reason, "mode": "mock"}

    def debit(self, user_id: str, amount: int, reason: str) -> Dict[str, Any]:
        return {"user_id": user_id, "amount": -amount, "reason": reason, "mode": "mock"}

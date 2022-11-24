from __future__ import annotations
from typing import Dict, Any


class SlackEvent:
    def __init__(self, user_id: str, channel: str, text: str) -> None:
        self.user_id = user_id
        self.channel = channel
        self.text = text

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> SlackEvent:
        event = payload.get("event", {})
        return SlackEvent(user_id=event["user"], channel=event["channel"], text=event.get("text", "").lower())

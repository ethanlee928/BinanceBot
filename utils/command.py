from __future__ import annotations
from enum import IntEnum
from typing import Dict, Any, TypeAlias
import pickle

CommandBody: TypeAlias = Dict[str, Any]


class Command:
    """
    Available commands:
        1. ping
        2. chart (coinpair) (interval) (start time)
        3. price (coinpair)
        4. info (coinpair) (interval)
    """

    class ID(IntEnum):
        _BASE = 100
        PING = _BASE + 1
        CHART = _BASE + 2
        PRICE = _BASE + 3
        INFO = _BASE + 4

    def __init__(self, _id: ID, body: CommandBody) -> None:
        self._id = _id
        self.body = body

    def to_payload(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def from_payload(payload: bytes) -> Command:
        return pickle.loads(payload)

from __future__ import annotations
from enum import IntEnum
from typing import Dict, Any, TypeAlias
import pickle
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from overrides import override

from .mqtt import MQTTMessageHandler, MQTTMessage
from .logger import logger

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

    def __init__(self, _id: ID, channel_id: str, body: CommandBody) -> None:
        self._id = _id
        self.channel_id = channel_id
        self.body = body

    def to_payload(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def from_payload(payload: bytes) -> Command:
        return pickle.loads(payload)


class CommandHandler(MQTTMessageHandler, ABC):
    def __init__(self, max_workers: int = 5) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    @override
    def on_MQTTMessage(self, mqtt_message: MQTTMessage):
        logger.debug(f"Received MQTTMessage: {mqtt_message}")
        command = Command.from_payload(mqtt_message.payload)
        future = self.executor.submit(self.on_command, command)
        future.add_done_callback(self._callback)

    @abstractmethod
    def on_command(self, command: Command):
        pass

    def _callback(self, *_):
        logger.info("Finished on command")

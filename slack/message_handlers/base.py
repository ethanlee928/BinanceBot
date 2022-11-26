from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum


class HandlerType(Enum):
    BINANCE = "BinanceCommandHandler"


class MessageHandler(ABC):
    @abstractmethod
    def on_message(self, payload: Dict[str, Any]) -> None:
        pass

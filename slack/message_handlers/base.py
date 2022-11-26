from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from enum import Enum


from .binance_command_handler import BinanceCommandHandler


class HandlerType(Enum):
    BINANCE = "BinanceCommandHandler"


class MessageHandler(ABC):
    @abstractmethod
    def on_message(self, payload: Dict[str, Any]) -> None:
        pass


class MessageHandlerFactory:
    @staticmethod
    def from_dict(_type: HandlerType, body: Dict[str, Any]) -> Type[MessageHandler]:
        if _type == MessageHandlerFactory.HandlerType.BINANCE:
            return BinanceCommandHandler(client_id=body["client_id"], broker=body["broker"], topic=body["topic"])
        else:
            raise NotImplementedError("The input type of handler is not supported")

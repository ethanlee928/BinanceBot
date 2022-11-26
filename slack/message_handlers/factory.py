from typing import Dict, Any, Type

from .base import MessageHandler, HandlerType
from .binance_command_handler import BinanceCommandHandler


class MessageHandlerFactory:
    @staticmethod
    def from_dict(_type: HandlerType, body: Dict[str, Any]) -> Type[MessageHandler]:
        if _type == HandlerType.BINANCE:
            return BinanceCommandHandler(client_id=body["client_id"], broker=body["broker"], topic=body["topic"])
        else:
            raise NotImplementedError("The input type of handler is not supported")

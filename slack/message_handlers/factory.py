from typing import Dict, Any, Type

from .base import MessageHandler, HandlerType
from .binance_command_handler import BinanceCommandHandler


class MessageHandlerFactory:
    @staticmethod
    def create_handler(_type: HandlerType, **kwargs: Dict[str, Any]) -> Type[MessageHandler]:
        if _type == HandlerType.BINANCE:
            return BinanceCommandHandler(client_id=kwargs["client_id"], broker=kwargs["broker"], topic=kwargs["topic"])
        else:
            raise NotImplementedError("The input type of handler is not supported")

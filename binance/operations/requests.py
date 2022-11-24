from __future__ import annotations
from abc import ABC
from typing import Type
from dataclasses import dataclass

from utils import Command


@dataclass
class BinanceRequest(ABC):
    coin_pair: str


@dataclass
class KlineRequest(BinanceRequest):
    interval: str
    start_time: str


@dataclass
class InfoRequest(BinanceRequest):
    interval: str


@dataclass
class CoinPriceRequest(BinanceRequest):
    ...


class BinanceRequestFactory:
    @staticmethod
    def from_command(command: Command) -> Type[BinanceRequest]:
        match command._id:
            case Command.ID.PING:
                return
            case Command.ID.CHART:
                return KlineRequest(
                    coin_pair=command.body["coin_pair"],
                    interval=command.body["interval"],
                    start_time=command.body["start_time"],
                )
            case Command.ID.INFO:
                return InfoRequest(
                    coin_pair=command.body["coin_pair"],
                    interval=command.body["interval"],
                )
            case Command.ID.PRICE:
                return CoinPriceRequest(coin_pair=command.body["coin_pair"])
            case _:
                raise NotImplementedError("No such command ID")

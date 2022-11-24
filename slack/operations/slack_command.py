from __future__ import annotations
from typing import List
from enum import Enum

from utils import Command, logger
from .slack_event import SlackEvent


class SlackCommand:
    class ID(Enum):
        HELP = "help"
        CHART = "chart"
        INFO = "info"
        PRICE = "price"
        PING = "ping"

    def __init__(self, _id: ID, channel: str, command_slides: List[str]) -> None:
        self._id = _id
        self.channel = channel
        self.command_slides = command_slides

    @staticmethod
    def from_slackevent(event: SlackEvent) -> SlackCommand:
        command_slides = event.text.strip().split()
        channel = event.channel
        match command_slides[0]:
            case "help":
                _id = SlackCommand.ID.HELP
            case "chart":
                _id = SlackCommand.ID.CHART
            case "info":
                _id = SlackCommand.ID.INFO
            case "price":
                _id = SlackCommand.ID.PRICE
            case "ping":
                _id = SlackCommand.ID.PING
            case _:
                logger.warning("Command not recognised")
                return
        return SlackCommand(_id=_id, channel=channel, command_slides=command_slides)

    def to_command(self) -> Command:
        if self._id == self.ID.HELP:
            raise NotImplementedError("Help function is local to slack command")
        elif self._id == self.ID.CHART:
            coin_pair = self.command_slides[1].upper()
            interval = self.command_slides[2]
            start_time = self.command_slides[3]
            return Command(
                _id=Command.ID.CHART,
                channel_id=self.channel,
                body=dict(
                    coin_pair=coin_pair,
                    interval=interval,
                    start_time=start_time,
                ),
            )
        elif self._id == self.ID.PRICE:
            coin_pair = self.command_slides[1].upper()
            return Command(_id=Command.ID.PRICE, channel_id=self.channel, body=dict(coin_pair=coin_pair))
        elif self._id == self.ID.INFO:
            coin_pair = self.command_slides[1].upper()
            interval = self.command_slides[2]
            return Command(
                _id=Command.ID.INFO, channel_id=self.channel, body=dict(coin_pair=coin_pair, interval=interval)
            )
        elif self._id == self.ID.PING:
            return Command(_id=Command.ID.PING, channel_id=self.channel, body={})
        else:
            raise NotImplementedError(f"Slack command ID: {self._id} conversion to Command is not implemented")

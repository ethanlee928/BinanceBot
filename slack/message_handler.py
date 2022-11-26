from typing import Dict, Any
import os

from slack import WebClient

from utils import MQTTMessage, Command, Broker, Publisher, logger
from operations import SlackCommand, SlackEvent


class SlackMessageHandler:
    def __init__(self, client_id: str, broker: Broker, topic: str) -> None:
        self.publisher = Publisher(client_id=client_id, broker=broker)
        self.slack_web_client = WebClient(os.getenv("SLACK_TOKEN"))
        self.topic = topic

    def on_message(self, payload: Dict[str, Any]) -> None:
        if self._is_bot_user(payload=payload):
            return
        slack_event = SlackEvent.from_payload(payload=payload)
        slack_command = SlackCommand.from_slackevent(event=slack_event)
        if slack_command._id == SlackCommand.ID.HELP:
            self._on_help_command(channel_id=slack_command.channel)
            return
        command: Command = slack_command.to_command()
        msg = MQTTMessage(topic=self.topic, payload=command.to_payload())
        self.publisher.publish(message=msg)

    def send_slack_msg(self, channel_id: str, msg: str):
        logger.info(f"Msg sent to {channel_id}: {msg}")
        return self.slack_web_client.chat_postMessage(channel=channel_id, text=msg)

    def _is_bot_user(self, payload: Dict[str, Any]) -> bool:
        event = payload.get("event", {})
        if event.get("bot_id"):
            return True
        return False

    def _on_help_command(self, channel_id: str) -> None:
        message = (
            "Available commands:\n"
            + "1. ping\n"
            + "2. chart (coinpair) (interval) (start time)\n"
            + "3. price (coinpair)\n"
            + "4. info (coinpair) (interval)"
        )
        res = self.send_slack_msg(channel_id=channel_id, msg=message)
        logger.info(f"Help message response: {res}")

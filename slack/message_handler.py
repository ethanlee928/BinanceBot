from typing import Dict, Any


from utils import MQTTMessage, Command, Broker, Publisher, logger
from operations import SlackCommand, SlackEvent, send_slack_message


class SlackMessageHandler:
    def __init__(self, client_id: str, broker: Broker, topic: str) -> None:
        self.publisher = Publisher(client_id=client_id, broker=broker)
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
        res = send_slack_message(channel_id=channel_id, message=message)
        logger.info(f"Help message response: {res}")

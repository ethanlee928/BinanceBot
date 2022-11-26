from typing import TypeAlias, Dict, Any
import os


from slack import WebClient
from utils import get_logger

WebClientResponse: TypeAlias = Dict[str, Any]
slack_web_client = WebClient(os.getenv("SLACK_TOKEN"))
logger = get_logger("SlackWebClient")


def send_slack_message(channel_id: str, message: str) -> WebClientResponse:
    logger.info(f"Message sending to {channel_id}: {message}")
    return slack_web_client.chat_postMessage(channel=channel_id, text=message)

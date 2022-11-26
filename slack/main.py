import os
import argparse
from flask import Flask

from slackeventsapi import SlackEventAdapter

from utils import Broker, logger, broker_config
from message_handlers import MessageHandlerFactory, HandlerType

parser = argparse.ArgumentParser(description="Slack bot configuration.")
parser.add_argument("--topic", default="pair")
parser.add_argument("--client_id", default="slackbot-pub")
args = parser.parse_args()

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv("SLACK_EVENT_TOKEN"), "/slack/events", app)
message_handlers = [
    MessageHandlerFactory.from_dict(
        _type=HandlerType.BINANCE,
        body=dict(client_id=args.client_id, broker=Broker.from_dict(broker_config), topic=args.topic),
    )
]


@slack_events_adapter.on("message")
def message(payload):
    try:
        for handler in message_handlers:
            handler.on_message(payload=payload)
    except Exception as err:
        logger.error("Slack OnMessage error: %s" % err)


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5001)

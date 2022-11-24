import os
import argparse
from flask import Flask

from slack import WebClient
from slackeventsapi import SlackEventAdapter

from utils import Publisher, Command, Broker, MQTTMessage, logger, broker_config
from .operations import SlackEvent, SlackCommand

parser = argparse.ArgumentParser(description="Slack bot configuration.")
parser.add_argument("--topic", default="pair")
parser.add_argument("--client_id", default="slackbot-pub")
args = parser.parse_args()

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv("SLACK_EVENT_TOKEN"), "/slack/events", app)
slack_web_client = WebClient(os.getenv("SLACK_TOKEN"))

topic = args.topic
pub = Publisher(client_id=args.client_id, broker=Broker.from_dict(broker_config))


@slack_events_adapter.on("message")
def message(payload):
    try:
        event = payload.get("event", {})
        if event.get("bot_id"):
            return
        slack_event = SlackEvent.from_payload(payload=payload)
        slack_command = SlackCommand.from_slackevent(event=slack_event)
        if slack_command._id == SlackCommand.ID.HELP:
            message = (
                "Available commands:\n"
                + "1. ping\n"
                + "2. chart (coinpair) (interval) (start time)\n"
                + "3. price (coinpair)\n"
                + "4. info (coinpair) (interval)"
            )
            slackMsg(channelID=slack_command.channel, msg=message)
            return
        command: Command = slack_command.to_command()
        msg = MQTTMessage(topic=topic, payload=command.to_payload())
        pub.publish(message=msg)

    except Exception as err:
        logger.error("Slack OnMessage error: %s" % err)


def slackMsg(channelID, msg):
    try:
        res = slack_web_client.chat_postMessage(channel=channelID, text=msg)
        logger.info("Msg sent to %s:\n%s" % (channelID, msg))
    except Exception as err:
        logger.error("Slack send message error %s" % err)


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5001)

import os
import argparse
from flask import Flask

from slack import WebClient
from slackeventsapi import SlackEventAdapter

from utils import Publisher, Command, Broker, MQTTMessage, logger, broker_config


parser = argparse.ArgumentParser(description="Slack bot configuration.")
parser.add_argument("--topic", default="pair")
parser.add_argument("--client_id", default="slackbot-pub")
args = parser.parse_args()

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv("SLACK_EVENT_TOKEN"), "/slack/events", app)
slack_web_client = WebClient(os.getenv("SLACK_TOKEN"))

topic = args.topic
pub = Publisher(client_id=args.client_id, broker=Broker.from_dict(broker_config))

available_commands = ["chart", "price", "ping", "info", "help", "start", "stop"]


@slack_events_adapter.on("message")
def message(payload):
    try:
        event = payload.get("event", {})
        text = event.get("text").lower()
        textSlice = text.strip().split()
        channel = event.get("channel")
        userID = event.get("user")

        if event.get("bot_id"):
            return

        if textSlice[0] not in available_commands:
            logger.info("Command not recognised")
            return

        if textSlice[0] == "help":
            message = (
                "Available commands:\n"
                + "1. ping\n"
                + "2. chart (coinpair) (interval) (start time)\n"
                + "3. price (coinpair)\n"
                + "4. info (coinpair) (interval)"
            )
            slackMsg(channelID=channel, msg=message)

        if textSlice[0] == "chart":
            handleChartPrice(command=textSlice, channel=channel)

        if textSlice[0] == "info":
            handleInfo(command=textSlice, channel=channel)

        if textSlice[0] == "price":
            handleCheckPrice(command=textSlice, channel=channel)

        if textSlice[0] == "ping":
            handlePing(channel=channel)

    except Exception as err:
        logger.error("Slack OnMessage error: %s" % err)


def handleChartPrice(command, channel):
    if len(command) != 4:
        logger.info("Wrong syntax for get price chart")
        message = "Wrong syntax, try:\nchart (coinpair) (interval) (start time)"
        slackMsg(channelID=channel, msg=message)
        return

    coinPair = command[1].upper()
    interval = command[2]
    startTime = command[3]
    _command = Command(
        _id=Command.ID.CHART,
        channel_id=channel,
        body={
            "coin_pair": coinPair,
            "interval": interval,
            "start_time": startTime,
        },
    )
    msg = MQTTMessage(topic=topic, payload=_command.to_payload())
    pub.publish(message=msg)


def handleCheckPrice(command, channel):
    if len(command) != 2:
        logger.info("Wrong syntax to check average price")
        message = "Wrong syntax, try:\nprice (coinpair)"
        slackMsg(channelID=channel, msg=message)
        return

    coinPair = command[1].upper()
    _command = Command(
        _id=Command.ID.PRICE,
        channel_id=channel,
        body={
            "coin_pair": coinPair,
        },
    )
    msg = MQTTMessage(topic=topic, payload=_command.to_payload())
    pub.publish(message=msg)


def handleInfo(command, channel):
    if len(command) != 3:
        logger.info("Wrong syntax to check coinpair info")
        message = "Wrong syntax, try:\ninfo (coinpair) (interval)"
        slackMsg(channelID=channel, msg=message)
        return

    coinPair = command[1].upper()
    interval = command[2]
    _command = Command(
        _id=Command.ID.INFO,
        channel_id=channel,
        body={
            "coin_pair": coinPair,
            "interval": interval,
        },
    )
    msg = MQTTMessage(topic=topic, payload=_command.to_payload())
    pub.publish(message=msg)


def handlePing(channel):
    command = Command(_id=Command.ID.PING, channel_id=channel, body={})
    msg = MQTTMessage(topic=topic, payload=command.to_payload())
    pub.publish(message=msg)


def slackMsg(channelID, msg):
    try:
        res = slack_web_client.chat_postMessage(channel=channelID, text=msg)
        logger.info("Msg sent to %s:\n%s" % (channelID, msg))
    except Exception as err:
        logger.error("Slack send message error %s" % err)


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5001)

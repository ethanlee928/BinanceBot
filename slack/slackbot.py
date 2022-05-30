import os
import time
import json
import argparse
from flask import Flask

from slack import WebClient
from slackeventsapi import SlackEventAdapter
from utils.mqtt import Subscriber, Publisher
from utils.logger import get_logger


parser = argparse.ArgumentParser(description='Slack bot configuration.')
parser.add_argument('--broker', default='mosquitto')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--topic', default='pair')
parser.add_argument('--client_id', default='slackbot-pub')
args = parser.parse_args()

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv("SLACK_EVENT_TOKEN"), "/slack/events", app)
slack_web_client = WebClient(os.getenv("SLACK_TOKEN"))

broker = args.broker
port = args.port
topic = args.topic
client_id = args.client_id
pub = Publisher(broker, port, client_id)

logger = get_logger(name='SBOT')


@slack_events_adapter.on("message")
def message(payload):
    try:
        event = payload.get("event", {})
        text = event.get("text").lower()
        textSlice = text.strip().split()
        channel = event.get("channel")
        
        if event.get('bot_id'):
            return

        if textSlice[0] != 'check':
            message = 'Your commands are not recognised, try:\n' + 'check (coinpair) (interval) (start time)' 
            slackMsg(channelID=channel, msg=message)
            return

        if len(textSlice) != 4:
            message = 'Wrong syntax, try:\ncheck (coinpair) (interval) (start time)'
            slackMsg(channelID=channel, msg=message)
            return

        coinPair = textSlice[1].upper()
        interval = textSlice[2]
        startTime = textSlice[3]
        payload = {
            "type": "kline",
            "coinPair": coinPair,
            "interval": interval,
            "startDate": startTime,
            "channelID": channel
        }
        payload = json.dumps(payload)
        pub.publish(topic=topic, message=payload) 
        logger.info("Published %s to %s" % (payload, topic))       

    except Exception as err:
        logger.error("Slack OnMessage error: %s" % err)


def slackMsg(channelID, msg):
    try:
        res = slack_web_client.chat_postMessage(
            channel=channelID,
            text=msg
        )
        logger.info("Msg sent to %s:\n%s" % (channelID, msg))
    except Exception as err:
        logger.error("Slack send message error %s" % err)


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5001)
    slackMsg(channelID="C03G2NCPY8P", msg="Slackbot disconnected...")


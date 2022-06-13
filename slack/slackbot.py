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
available_commands = ['chart', 'price', 'ping', 'info', 'help', 'start', 'stop']


@slack_events_adapter.on("message")
def message(payload):
    try:
        event = payload.get("event", {})
        text = event.get("text").lower()
        textSlice = text.strip().split()
        channel = event.get("channel")
        userID = event.get("user")
        
        if event.get('bot_id'):
            return

        if textSlice[0] not in available_commands:
            logger.info('Command not recognised')
            return
        
        if textSlice[0] == 'help':
            message = 'Available commands:\n' + '1. ping\n' +'2. chart (coinpair) (interval) (start time)\n' + '3. price (coinpair)\n' + '4. info (coinpair) (interval)'
            slackMsg(channelID=channel, msg=message)            

        if textSlice[0] == 'chart':
            handleChartPrice(command=textSlice, channel=channel)

        if textSlice[0] == 'info':
            handleInfo(command=textSlice, channel=channel)

        if textSlice[0] == 'price':
            handleCheckPrice(command=textSlice, channel=channel)
        
        if textSlice[0] == 'ping':
            handlePing(channel=channel)

        if textSlice[0] == 'start':
            handleStart(command=textSlice, channel=channel, userID=userID)
        
        if textSlice[0] == 'stop':
            handleStop(command=textSlice, channel=channel, userID=userID)
    
    except Exception as err:
        logger.error("Slack OnMessage error: %s" % err)

def handleStart(command, channel, userID):
    if len(command) != 3:
        logger.info('Wrong syntax for starting price report')
        message = 'Wrong syntax for starting price report, try:\nstart (coinpair) (report interval)'
        slackMsg(channelID=channel, msg=message)
        return 
    coinPair = command[1].upper()
    interval = command[2]
    payload = {
        "type": "start",
        "coinPair": coinPair,
        "interval": interval, 
        "userID": userID,
        "channelID": channel
    }
    payload = json.dumps(payload)
    pub.publish(topic=topic, message=payload)

def handleStop(command, channel, userID):
    if len(command) != 2:
        logger.info('Wrong syntax for stopping price report')
        message = 'Wrong syntax for stopping price report, try:\nstop (coinpair)'
        return

    coinPair = command[1].upper()
    payload = {
        "type": "stop",
        "coinPair": coinPair,
        "userID": userID,
        "channelID": channel
    }
    payload = json.dumps(payload)
    pub.publish(topic=topic, message=payload)

def handleChartPrice(command, channel):
    if len(command) != 4:
        logger.info('Wrong syntax for get price chart')
        message = 'Wrong syntax, try:\nchart (coinpair) (interval) (start time)'
        slackMsg(channelID=channel, msg=message)
        return

    coinPair = command[1].upper()
    interval = command[2]
    startTime = command[3]
    payload = {
        "type": "chart",
        "coinPair": coinPair,
        "interval": interval,
        "startDate": startTime,
        "channelID": channel
    }    
    payload = json.dumps(payload)
    pub.publish(topic=topic, message=payload)     

def handleCheckPrice(command, channel):
    if len(command) != 2:
        logger.info('Wrong syntax to check average price')
        message = 'Wrong syntax, try:\nprice (coinpair)'
        slackMsg(channelID=channel, msg=message)
        return
    
    coinPair = command[1].upper()
    payload = {
        "type": "price",
        "coinPair": coinPair,
        "channelID": channel
    }
    payload = json.dumps(payload)
    pub.publish(topic=topic, message=payload)     

def handleInfo(command, channel):
    if len(command) != 3:
        logger.info('Wrong syntax to check coinpair info')
        message = 'Wrong syntax, try:\ninfo (coinpair) (interval)'
        slackMsg(channelID=channel, msg=message)
        return
    
    coinPair = command[1].upper()
    interval = command[2]
    payload = {
        "type": "info",
        "coinPair": coinPair,
        "interval": interval,
        "channelID": channel
    }
    payload = json.dumps(payload)
    pub.publish(topic=topic, message=payload)

def handlePing(channel):
    payload = {
        "type": "ping",
        "channelID": channel
    }
    payload = json.dumps(payload)
    pub.publish(topic=topic, message=payload)

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

import os
import time
import json
from flask import Flask

from slack import WebClient
from slackeventsapi import SlackEventAdapter
from utils.mqtt import Subscriber, Publisher


app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.getenv("SLACK_EVENT_TOKEN"), "/slack/events", app)
slack_web_client = WebClient(os.getenv("SLACK_TOKEN"))

broker = 'mosquitto'
port = 1883
topic = 'pair'
client_id = 'slackbot-pub'
pub = Publisher(broker, port, client_id)


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

    except Exception as err:
        print(f'Error occured: {err}')


def slackMsg(channelID, msg):
    try:
        res = slack_web_client.chat_postMessage(
            channel=channelID,
            text=msg
        )
    except Exception as err:
        print(f'Error occured: {err}')



if __name__ == "__main__":

    broker = 'mosquitto'
    port = 1883
    topic = 'pair'
    client_id = 'machine1-pub'

    app.run(host='0.0.0.0', port=5001)
    slackMsg(channelID="C03G2NCPY8P", msg="Slackbot disconnected...")

    # start = time.time()
    # pub = Publisher(broker, port, client_id)
    # while 1:
    #     try:
    #         now = time.time()
    #         payload = {
    #             "type": "kline",
    #             "pair": "BNBUSDT",
    #             "interval": "15m",
    #             "startDate": "15/5/2022"
    #         }
    #         payload = json.dumps(payload)
    #         pub.publish(topic=topic, message=payload)
    #         time.sleep(1)
    #     except Exception as err:
    #         print(f'error occured: {err}')
    #     except KeyboardInterrupt:
    #         break
    
    # payload = {
    #     "type": "message",
    #     "message": "Finished publishing"
    # }
    # payload = json.dumps(payload)
    # pub.publish(topic=topic, message=payload)

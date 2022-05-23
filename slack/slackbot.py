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

@slack_events_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    text = event.get("text")
    channel = event.get("channel")

    print(f'from {channel}: {text}')


if __name__ == "__main__":

    broker = 'mosquitto'
    port = 1883
    topic = 'pair'
    client_id = 'machine1-pub'

    app.run(host='0.0.0.0', port=3000)

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

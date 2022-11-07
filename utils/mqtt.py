import json
import paho.mqtt.client as mqtt
from utils.logger import get_logger


class Subscriber:
    def __init__(self, broker, port, topic, client_id):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id

        self.logger = get_logger(name="SUB")

        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, self.port)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to MQTT Broker!")
        else:
            self.logger.error("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        message = json.loads(message)

    def start_subscribe(self):
        self.client.subscribe(self.topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()


class Publisher:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id

        self.logger = get_logger(name="PUB")

        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to MQTT Broker!")
        else:
            self.logger.error("Failed to connect, return code %d\n", rc)

    def publish(self, topic, message):

        msg = f"{message}"
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            self.logger.info("Send %s to topic %s" % (msg, topic))

        else:
            self.logger.error("Failed to send message to topic %s" % topic)

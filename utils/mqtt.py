from __future__ import annotations
from abc import ABC, abstractmethod

import paho.mqtt.client as mqtt
from overrides import overrides

from .broker import Broker
from .logger import logger, get_logger


class MQTTClient(ABC):
    def __init__(self, client_id: str, broker: Broker) -> None:
        self.logger = get_logger(name="MQTT")
        self.client_id = client_id
        self.broker = broker

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(broker.username, broker.password)
        self.client.connect(broker.host, broker.port)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to MQTT Broker!")
        else:
            self.logger.error("Failed to connect, return code %d\n", rc)

    @abstractmethod
    def start(self):
        pass


class Subscriber(MQTTClient):
    def __init__(self, client_id: str, broker: Broker, topic) -> None:
        super().__init__(client_id, broker)
        self.topic = topic

    @overrides
    def start(self):
        self.client.subscribe(self.topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, udata, msg):
        message = msg.payload.decode()
        self.logger.info(f"message received: {message}")


class Publisher(MQTTClient):
    def __init__(self, client_id: str, broker: Broker) -> None:
        super().__init__(client_id, broker)
        self.client.loop_start()

    @overrides
    def start(self):
        self.client.loop_start()

    def publish(self, topic, message):
        msg = f"{message}"
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            self.logger.info("Send %s to topic %s" % (msg, topic))

        else:
            self.logger.error("Failed to send message to topic %s" % topic)

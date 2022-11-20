from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TypeAlias, Type

import paho.mqtt.client as mqtt
from overrides import overrides

from .broker import Broker
from .logger import get_logger


class MQTTMessage(ABC):
    def __init__(self, topic: str, payload: bytes) -> None:
        self.topic = topic
        self.payload = payload

    @staticmethod
    def from_str(topic: str, message: str) -> MQTTMessage:
        return MQTTMessage(topic=topic, payload=bytes(message, "utf8"))


class MQTTMessageHandler(ABC):
    @abstractmethod
    def on_MQTTMessage(self, mqtt_message: MQTTMessage):
        pass


Handlers: TypeAlias = List[Type[MQTTMessageHandler]]


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
        self.handlers = []

    @overrides
    def start(self):
        self.client.subscribe(self.topic)
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, udata, msg):
        mqtt_msg = MQTTMessage(topic=self.topic, payload=msg.payload)
        self.logger.debug(f"received payload: {mqtt_msg.payload} from topic: {mqtt_msg.topic}")
        handler: Type[MQTTMessageHandler]
        for handler in self.handlers:
            handler.on_MQTTMessage(mqtt_message=mqtt_msg)

    def register_handlers(self, handlers: Handlers) -> None:
        self.logger.info("Adding handlers")
        self.handlers = handlers


class Publisher(MQTTClient):
    def __init__(self, client_id: str, broker: Broker) -> None:
        super().__init__(client_id, broker)
        self.client.loop_start()

    @overrides
    def start(self):
        self.client.loop_start()

    def publish(self, message: MQTTMessage) -> None:
        result = self.client.publish(message.topic, message.payload)
        if result[0] == 0:
            self.logger.debug(f"Send {message.payload} to topic {message.topic}")
        else:
            self.logger.error(f"Failed to send message to topic {message.topic}")

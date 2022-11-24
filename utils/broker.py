from __future__ import annotations
from typing import Dict, Any
import os


class Broker:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @staticmethod
    def from_dict(config: Dict[str, Any]) -> Broker:
        return Broker(
            host=config["host"], port=config["port"], username=config["username"], password=config["password"]
        )

    @staticmethod
    def from_env() -> Broker:
        host = os.getenv("BROKER_HOST")
        port = os.getenv("BROKER_PORT")
        username = os.getenv("BROKER_USERNAME")
        password = os.getenv("BROKER_PASSWORD")
        return Broker(host, port, username, password)

import argparse

from utils import Subscriber, Broker, broker_config, logger
from command_handler import BinanceCommandHandler


class BinanceBot:
    def __init__(self, client_id: str, broker: Broker, topic: str, data_dir: str) -> None:
        self.subscriber = Subscriber(client_id=client_id, broker=broker, topic=topic)
        self.data_dir = data_dir

    def start(self):
        handlers = [BinanceCommandHandler(data_dir=self.data_dir)]
        self.subscriber.register_handlers(handlers=handlers)
        self.subscriber.start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Binance bot configuration")
    parser.add_argument("--topic", default="pair")
    parser.add_argument("--client_id", default="binancebot")
    parser.add_argument("--data_dir", default="./data")
    args = parser.parse_args()

    try:
        app = BinanceBot(
            client_id=args.client_id, broker=Broker.from_dict(broker_config), topic=args.topic, data_dir=args.data_dir
        )
        app.start()
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt stopping main function")
    finally:
        logger.warning("Exiting main function")

from overrides import override

from utils import Command, CommandHandler, logger
from operations import BinanceClient, SlackRequest, BinanceRequestFactory, plot_klines


class BinanceCommandHandler(CommandHandler):
    def __init__(self, data_dir: str, max_workers: int = 5) -> None:
        super().__init__(max_workers)
        self.binance_client = BinanceClient()
        self.save_dir = data_dir

    @override
    def on_command(self, command: Command):
        logger.debug(f"Command received with ID: {command._id}")
        try:
            match command._id:
                case Command.ID.PING:
                    self._on_ping(command=command)
                case Command.ID.CHART:
                    self._on_chart(command=command)
                case Command.ID.INFO:
                    self._on_info(command=command)
                case Command.ID.PRICE:
                    self._on_price(command=command)
                case _:
                    raise NotImplementedError("The received command ID is not implemented")
        except Exception as err:
            logger.error(f"Binance command error: {err}")

    def _on_ping(self, command: Command) -> None:
        if self.binance_client.server_is_healthy():
            msg = "Binance server normal"
        else:
            msg = "Binance server under maintenance"
        req = SlackRequest.create_msg_request(channel=command.channel_id, msg=msg)
        res = req.post_request()
        logger.info(f"Posted request with response {res}")

    def _on_chart(self, command: Command) -> None:
        req = BinanceRequestFactory.from_command(command=command)
        kline = self.binance_client.get_klines(request=req)
        _path = plot_klines(kline=kline, request=req, data_dir=self.save_dir)
        logger.info(f"Saved kline graph @ {_path}")
        req = SlackRequest.create_upload_file_request(channel=command.channel_id, file_path=_path)
        res = req.post_request()
        logger.info(f"Posted request with response {res}")

    def _on_price(self, command: Command) -> None:
        req = BinanceRequestFactory.from_command(command=command)
        mins, price = self.binance_client.get_coin_price(request=req)
        msg = f"{req.coin_pair} {mins}m average: {price}"
        req = SlackRequest.create_msg_request(channel=command.channel_id, msg=msg)
        res = req.post_request()
        logger.info(f"Posted request with response {res}")

    def _on_info(self, command: Command) -> None:
        req = BinanceRequestFactory.from_command(command=command)
        info = self.binance_client.get_coin_info(request=req)
        message = f'[{req.coin_pair}] Open Time: {info["openTime"]}\tClose Time: {info["closeTime"]}\nOpen Price: {info["openPrice"]}\nCurrent Price: {info["closePrice"]}\nHigh: {info["high"]}\nVolume: {info["volume"]}\nQuote Volume: {info["quoteVolume"]}'
        req = SlackRequest.create_msg_request(channel=command.channel_id, msg=message)
        res = req.post_request()
        logger.info(f"Posted request with response {res}")

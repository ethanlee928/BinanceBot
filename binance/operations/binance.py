import os
from typing import Dict, Any, Tuple
from datetime import datetime

import pandas as pd
from binance.client import Client


class BinanceRequest:
    def __init__(self, coin_pair: str, body: Dict[str, Any]) -> None:
        self.coin_pair = coin_pair
        self.body = body


class BinanceClient:
    def __init__(self) -> None:
        self.client = Client(os.getenv("BINANCE_KEY"), os.getenv("BINANCE_SECRET"))

    def get_klines(self, request: BinanceRequest) -> pd.DataFrame:
        _klines = self.client.get_historical_klines(
            request.coin_pair, request.body.get("interval"), request.body.get("start_time")
        )
        klines = []
        for item in _klines:
            open_time = datetime.fromtimestamp(item[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            open_price = item[1]
            high = item[2]
            low = item[3]
            close_price = item[4]
            klines.append([open_time, open_price, high, low, close_price])

        df = pd.DataFrame(klines, columns=["date", "open", "high", "low", "close"])
        df.set_index(pd.DatetimeIndex(df["date"]), inplace=True)
        df.drop(["date"], inplace=True, axis=1)
        df = df.astype(float)
        return df

    def get_coin_info(self, request: BinanceRequest) -> Dict[str, Any]:
        candle = self.client.get_klines(symbol=request.coin_pair, interval=request.body.get("interval"))[-1]
        info = {
            "openTime": datetime.fromtimestamp(candle[0] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            "openPrice": candle[1],
            "high": candle[2],
            "low": candle[3],
            "closePrice": candle[4],
            "volume": candle[5],
            "closeTime": datetime.fromtimestamp(candle[6] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            "quoteVolume": candle[7],
        }
        return info

    def get_coin_price(self, request: BinanceRequest) -> Tuple[float, float]:
        avg_price: Dict[str, float] = self.client.get_avg_price(symbol=request.coin_pair)
        return (avg_price.get("mins"), avg_price.get("price"))

    def server_is_healthy(self):
        status = self.client.get_system_status()
        if status.get("status") == 0:
            return True
        return False

import os
import json
import argparse
import requests

import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime
from threading import Thread

from binance.client import Client
from utils.mqtt import Subscriber, Publisher
from utils.logger import get_logger


class BinanceBot(Subscriber):
    def __init__(self, broker, port, topic, client_id, dataDir, timeLimit):
        super().__init__(broker, port, topic, client_id)
        self.key = os.getenv("BINANCE_KEY")
        self.secret = os.getenv("BINANCE_SECRET")
        self.binanceClient = Client(self.key, self.secret)

        self.slackToken = os.getenv("SLACK_TOKEN")

        self.lastShow = None
        self.timeLimit = timeLimit

        self.dataDir = dataDir

        self.logger = get_logger(name="BBOT")

        self.subThread = Thread(target=self.start_subscribe)
        self.subThread.start()

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        message = json.loads(message)
        if message["type"] == "message":
            self.logger.info("message from MQTT: " % (message["message"]))
            return

        if message["type"] == "chart":
            self.handleKline(message=message)
            return

        if message["type"] == "price":
            self.handlePrice(message=message)
            return

        if message["type"] == "info":
            self.handleInfo(message=message)
            return

        if message["type"] == "ping":
            status = self.pingServer()
            channelID = message["channelID"]
            if status:
                self.sendMsg(msg="Binance server normal", channel=channelID)
            else:
                self.sendMsg(msg="Binance server under maintenance", channel=channelID)
            return

    def handleKline(self, message):
        now = datetime.now()
        if (
            self.lastShow is None
            or (now - self.lastShow).total_seconds() > self.timeLimit
        ):
            try:
                coinPair = message["coinPair"]
                interval = message["interval"]
                startDate = message["startDate"]
                channelID = message["channelID"]
                kline = self.getKlines(coinPair, interval, startDate)

                savePath = self.plotKlines(
                    kline=kline, type="candle", coinPair=coinPair, interval=interval
                )
                if savePath is None:
                    self.logger.error("Cannot plot klines")
                    return

                self.sendKlines(imgpath=savePath, channel=channelID)
                self.lastShow = datetime.now()

            except Exception as err:
                self.logger.error("Kline component error: %s" % err)

    def handlePrice(self, message):
        try:
            coinPair = message["coinPair"]
            channelID = message["channelID"]
            mins, price = self.getCoinPrice(coinPair=coinPair)
            message = f"[{coinPair}] {mins}m average: {price}"
            self.sendMsg(msg=message, channel=channelID)
        except Exception as err:
            self.logger.error("Coinpair price component error: %s" % err)

    def handleInfo(self, message):
        try:
            coinPair = message["coinPair"]
            interval = message["interval"]
            channelID = message["channelID"]
            info = self.getInfo(coinPair=coinPair, interval=interval)
            message = f'[{coinPair}] Open Time: {info["openTime"]}\tClose Time: {info["closeTime"]}\nOpen Price: {info["openPrice"]}\nCurrent Price: {info["closePrice"]}\nHigh: {info["high"]}\nVolume: {info["volume"]}\nQuote Volume: {info["quoteVolume"]}'
            self.sendMsg(msg=message, channel=channelID)
        except Exception as err:
            self.logger.error("Coinpair info component error: %s" % err)

    def pingServer(self):
        status = self.binanceClient.get_system_status()
        if status["status"] == 0:
            return True
        return False

    def getPrice(self):
        prices = self.binanceClient.get_all_tickers()
        return prices

    def getInfo(self, coinPair, interval):
        candle = self.binanceClient.get_klines(symbol=coinPair, interval=interval)[-1]
        info = {
            "openTime": datetime.fromtimestamp(candle[0] / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "openPrice": candle[1],
            "high": candle[2],
            "low": candle[3],
            "closePrice": candle[4],
            "volume": candle[5],
            "closeTime": datetime.fromtimestamp(candle[6] / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "quoteVolume": candle[7],
        }
        return info

    def getCoinPrice(self, coinPair):
        avg_price = self.binanceClient.get_avg_price(symbol=coinPair)
        mins = avg_price["mins"]
        price = avg_price["price"]
        return mins, price

    def getKlines(self, coin_pair, interval, start_time):
        klinesBinance = self.binanceClient.get_historical_klines(
            coin_pair, interval, start_time
        )
        klines = []
        for item in klinesBinance:
            openTime = datetime.fromtimestamp(item[0] / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            openPirce = item[1]
            high = item[2]
            low = item[3]
            closePrice = item[4]
            klines.append([openTime, openPirce, high, low, closePrice])

        df = pd.DataFrame(klines, columns=["date", "open", "high", "low", "close"])
        df.set_index(pd.DatetimeIndex(df["date"]), inplace=True)
        df.drop(["date"], inplace=True, axis=1)
        df = df.astype(float)
        return df

    def sendMsg(self, msg, channel):
        api = "https://slack.com/api/chat.postMessage"
        token = "Bearer " + self.slackToken
        headers = {"Authorization": token}
        data = {"channel": channel, "text": msg}
        res = requests.post(api, headers=headers, data=data)
        self.logger.info("Message sent with response code: %s" % res.status_code)
        return res.status_code

    def sendKlines(self, imgpath, channel):
        api = "https://slack.com/api/files.upload"
        token = "Bearer " + self.slackToken
        headers = {"Authorization": token}
        data = {"channels": channel}
        files = {"file": open(imgpath, "rb")}

        res = requests.post(api, headers=headers, data=data, files=files)
        self.logger.info("Klines sent with response code: %s" % res.status_code)
        return res.status_code

    def plotKlines(self, kline, type, coinPair, interval):
        title = f"{coinPair}-{interval}"
        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        saveDir = f"{self.dataDir}/{coinPair}/"
        isExist = os.path.exists(saveDir)
        if not isExist:
            os.makedirs(saveDir)
        savePath = f"{saveDir}/{now}.png"
        try:
            mpf.plot(kline, type=type, title=title, savefig=savePath)
            self.logger.info("Klines plotted")
            return savePath
        except Exception as err:
            self.logger.error("PlotKlines error: %s" % err)
            return None


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Binance bot configuration")
    parser.add_argument("--broker", default="mosquitto")
    parser.add_argument("--port", default=1883)
    parser.add_argument("--topic", default="pair")
    parser.add_argument("--client_id", default="binancebot")
    parser.add_argument("--data_dir", default="./binance/data")
    parser.add_argument("--time_limit", type=int, default=20)
    args = parser.parse_args()

    broker = args.broker
    port = args.port
    topic = args.topic
    client_id = args.client_id
    data_dir = args.data_dir
    time_limit = args.time_limit

    bbot = BinanceBot(
        broker=broker,
        port=port,
        topic=topic,
        client_id=client_id,
        dataDir=data_dir,
        timeLimit=time_limit,
    )

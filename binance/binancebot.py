import os
import json
import requests

import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime
from threading import Thread

from binance.client import Client
from utils.mqtt import Subscriber, Publisher

class BinanceBot(Subscriber):

    def __init__(self, broker, port, topic, client_id):
        super().__init__(broker, port, topic, client_id)
        self.key = os.getenv('BINANCE_KEY')
        self.secret = os.getenv('BINANCE_SECRET')
        self.binanceClient = Client(self.key, self.secret) 

        self.slackToken = os.getenv('SLACK_TOKEN')

        self.lastShow = None
        self.timeLimit = 20

        self.dataDir = './data'

        self.subThread = Thread(target=self.start_subscribe)
        self.subThread.start() 
        
    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        message = json.loads(message)
        if message['type'] == 'message':
            print(f'message: {message["message"]}')
            return

        now = datetime.now()
        if self.lastShow is None or (now - self.lastShow).total_seconds() > self.timeLimit:
            coinPair = message['pair']
            interval = message['interval']
            startDate = message['startDate']
            kline = self.getKlines(coinPair, interval, startDate)
            print(kline)
            self.plotKlines(kline=kline, type='candle', coinPair=coinPair, interval=interval)
            self.lastShow = datetime.now()

    def getPrice(self):
        prices = self.binanceClient.get_all_tickers()
        return prices

    def getKlines(self, coin_pair, interval, start_time):
        klinesBinance = self.binanceClient.get_historical_klines(coin_pair, interval, start_time)
        klines = []
        for item in klinesBinance:
            openTime = datetime.fromtimestamp(item[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            openPirce = item[1]
            high = item[2]
            low = item[3]
            closePrice = item[4]
            klines.append([openTime, openPirce, high, low, closePrice])

        df = pd.DataFrame(klines, columns=['date', 'open', 'high', 'low', 'close'])
        df.set_index(pd.DatetimeIndex(df['date']), inplace=True)
        df.drop(['date'], inplace=True, axis=1)
        df = df.astype(float)
        return df

    def sendKlines(self, imgpath, channel):
        api = 'https://slack.com/api/files.upload'
        token = 'Bearer ' + self.slackToken
        headers = {'Authorization': token}
        data = {'channels': channel}
        files = {'file': open(imgpath, 'rb')}

        res = requests.post(api, headers=headers, data=data, files=files)
        print(res.status_code)
        return res.status_code
        
    
    def plotKlines(self, kline, type, coinPair, interval):
        title = f'{coinPair}-{interval}'
        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        saveDir = f'{self.dataDir}/{coinPair}/'
        isExist = os.path.exists(saveDir)
        if not isExist:
            os.makedirs(saveDir)
        savePath = f'{saveDir}/{now}.png'
        try:
            mpf.plot(kline, type=type, title=title, savefig=savePath)
            self.sendKlines(imgpath=savePath)
        except Exception as err:
            print(f'err occured: {err}')

if __name__ == "__main__":

    broker = 'mosquitto'
    port = 1883
    topic = 'pair'
    client_id = 'binancebot'

    pair = 'LUNABUSD'
    timeInterval = '5m'
    startTime = '15/5/2022 00:00:00'


    bbot = BinanceBot(broker=broker, port=port, topic=topic, client_id=client_id)
    # prices = bbot.getPrice()
    # kline = bbot.getKlines('ETHUSDT', '15m', '13 May 2022 12:00:00')
    # try:
    #     kline = bbot.getKlines(pair, timeInterval, startTime)
    #     mpf.plot(kline, type='candle', title=f'{pair}-{timeInterval}', savefig=f'./data/{pair}_test.png')
    # except Exception as err:
    #     print(f'err occured: {err}')
    
    
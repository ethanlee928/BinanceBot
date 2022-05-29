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

class BinanceBot(Subscriber):

    def __init__(self, broker, port, topic, client_id, dataDir, timeLimit):
        super().__init__(broker, port, topic, client_id)
        self.key = os.getenv('BINANCE_KEY')
        self.secret = os.getenv('BINANCE_SECRET')
        self.binanceClient = Client(self.key, self.secret) 

        self.slackToken = os.getenv('SLACK_TOKEN')

        self.lastShow = None
        self.timeLimit = timeLimit

        self.dataDir = dataDir

        self.subThread = Thread(target=self.start_subscribe)
        self.subThread.start() 
        
    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        message = json.loads(message)
        if message['type'] == 'message':
            print(f'message: {message["message"]}')
            return
        
        if message['type'] != 'kline': 
            return

        now = datetime.now()
        if self.lastShow is None or (now - self.lastShow).total_seconds() > self.timeLimit:
            try:
                coinPair = message['coinPair']
                interval = message['interval']
                startDate = message['startDate']
                channelID = message['channelID']
                kline = self.getKlines(coinPair, interval, startDate)
                print(kline)
                
                savePath = self.plotKlines(kline=kline, type='candle', coinPair=coinPair, interval=interval)
                if savePath is None:
                    print('Cannot plot klines...')
                    return

                self.sendKlines(imgpath=savePath, channel=channelID)
                self.lastShow = datetime.now()
            
            except Exception as err:
                print(f'Error occured: {err}')


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
            return savePath
        except Exception as err:
            print(f'err occured: {err}')
            return None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Binance bot configuration')
    parser.add_argument('--broker', default='mosquitto')
    parser.add_argument('--port', default=1883)
    parser.add_argument('--topic', default='pair')
    parser.add_argument('--client_id', default='binancebot')
    parser.add_argument('--data_dir', default='./binance/data')
    parser.add_argument('--time_limit', type=int, default=20)
    args = parser.parse_args()

    broker = args.broker
    port = args.port
    topic = args.topic
    client_id = args.client_id
    data_dir = args.data_dir
    time_limit = args.time_limit

    bbot = BinanceBot(broker=broker, port=port, topic=topic, client_id=client_id, dataDir=data_dir, timeLimit=time_limit)
    
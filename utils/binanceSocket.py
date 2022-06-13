import time
import asyncio
from multiprocessing import Process

from binance import AsyncClient, BinanceSocketManager
from binance.enums import *


class BinanceSocket():
    def __init__(self, coin_pair):
        self.coin_pair = coin_pair
        self.loop = None
        self.proc = None

    async def main(self):
        client = await AsyncClient.create()
        bm = BinanceSocketManager(client)
        ks = bm.kline_socket(self.coin_pair)
        async with ks as tscm:
            while 1:
                res = await tscm.recv()
                print(self.coin_pair, res)

        await client.close_connection()

    def start_loop(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.main())

    def start_process(self):
        self.proc = Process(target=self.start_loop)
        self.proc.start()

    def setStop(self):
        print('Stop triggered')
        self.proc.terminate()
        self.proc.join()
        self.loop = None

if __name__ == "__main__":

    BS = BinanceSocket('ETHUSDT')
    BS.start_process()
    time.sleep(5)
    BS2 = BinanceSocket('BTCUSDT')
    BS2.start_process()
    time.sleep(10)
    BS.setStop()
    time.sleep(5)
    BS.start_process()
    time.sleep(5)
    BS2.setStop()
    BS.setStop()

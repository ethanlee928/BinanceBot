import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *

from multiprocessing import Process

import time


async def main(coinPair):
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    # ts = bm.trade_socket('BNBBTC')
    ks = bm.kline_socket(coinPair)
    # then start receiving messages
    startTime = time.time()
    now = time.time()
    async with ks as tscm:
        while (now - startTime) < 20:
            res = await tscm.recv()
            now = time.time()
            print(coinPair, res)

    await client.close_connection()


def start(loop, coinPair):
    loop.run_until_complete(main(coinPair))


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    t = Process(
        target=start,
        args=(
            loop,
            "ETHUSDT",
        ),
    )
    t2 = Process(
        target=start,
        args=(
            loop,
            "BTCUSDT",
        ),
    )
    t3 = Process(
        target=start,
        args=(
            loop,
            "ENSUSDT",
        ),
    )
    t.start()
    t2.start()
    t.join()
    t2.join()

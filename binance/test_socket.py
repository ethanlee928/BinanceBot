import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *


async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    # ts = bm.trade_socket('BNBBTC')
    ks = bm.kline_socket('ETHUSDT')
    # then start receiving messages
    async with ks as tscm:
        while True:
            res = await tscm.recv()
            print(res)


    await client.close_connection()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
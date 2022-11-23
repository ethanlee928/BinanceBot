import os
from datetime import datetime

import pandas as pd
import mplfinance as mpf

from utils import logger
from .requests import KlineRequest


def plot_klines(kline: pd.DataFrame, request: KlineRequest, data_dir: str, _type="candle"):
    try:
        title = f"{request.coin_pair}-{request.interval}"
        now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        save_dir = f"{data_dir}/{request.coin_pair}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_path = f"{save_dir}/{now}.png"
        mpf.plot(kline, type=_type, title=title, savefig=save_path)
        logger.info(f"Klines of {request.coin_pair} plotted")
    except Exception as err:
        logger.error(f"Plot klines error: {err}")
        save_path = None
    finally:
        return save_path

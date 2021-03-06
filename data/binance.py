import logging
import time

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def get_now(symbol):
    """
    param symbol: market pair
    return: 24 hour ticket data
    """
    params = {
        'symbol': symbol,
    }

    response = requests.get('https://api.binance.com/api/v3/ticker/24hr', params=params).json()
    return response.json()


def get_past(symbol, interval, limit=600):
    """
    param symbol: market pair
    param interval: period of the candles
    param limit: maximum number of candles to be returned
    return: historical charts data from api.binance.com
    """
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }

    response = requests.get('https://api.binance.com/api/v3/klines', params=params)
    return response.json()

def load_dataframe(symbol, interval, limit=100):
    """
    Return historical charts data from api.binance.com
    param symbol: market pair
    param period: period of the candles
    param limit: maximum number of candles to be returned
    return: list of candles in the form of a pandas Dataframe
    """
    try:
        data = get_past(symbol, interval, limit)
    except Exception as ex:
        logger.error('Error trying to get historical charts data from the binance api: ' + str(ex))
        raise ex

    if 'error' in data:
        raise Exception("Bad response: {}".format(data['error']))

    # rename columns
    df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 
        'volume', 'close_time', 'qa_volume', 'nof_trades', 'tbba_volume', 'tbqa_volume', 'ignore'])

    # convert dates (milliseconds) to date time and make date index
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df = df.set_index(['date'])

    # convert numeric string values to float
    columns = ['open', 'high', 'low', 'close', 'volume', 'qa_volume', 'tbba_volume', 'tbqa_volume']
    for column in columns:
        df[column] = df[column].astype(float)

    return df

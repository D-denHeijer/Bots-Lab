# Imports of external modules come here
import numpy as np
import talib

# Imports of internal modules comes here
# When you want to change the buy_signal_settings from within the get_buy_or_sell_signal function import config_test or config_live  
# See https://docs.python.org/3/faq/programming.html#how-do-i-share-global-variables-across-modules

# Global variables come here. 
# Global variables can be used to store values for later use. 
# See https://www.w3schools.com/python/gloss_python_global_variables.asp

def get_buy_or_sell_signal(data):
    """
    Main algorithm method (the actual bot!), which will be called every tick. 
    This method receives a Pandas DataFrame(data). Each row of this Dataframe is a candle. 
    Rows of a DataFrame are dictionary like objects. To access a row value you can use 
    the follwing syntax: row_name['column_name']. Based upon this DataFrame the bot must 
    make a decision to buy, sell or do nothing. See below for a simple example.

    Param data: 
    List of candles or ticker data in the form of a Pandas Dataframe. The test environment
    uses candles (historical data) and the live environment ticker data. Candles or ticker data 
    have minimal the following properties: date, open, high, low, close and volume.

    Float64:
    The Dataframe number values are of type float64 (numpy dtype float). To convert this values to native
    Python floats use the item() function. See below.

    Example candle / ticker data:
    date(index)                 open       high       low        close       volume      date
    2020-03-03 12:00:00     0.02608580 0.02613449 0.02581001 0.02581078  59.40688146 2020-03-03 12:00:00

    Return: 'buy', 'sell' or None
    """

    # skip when the number of rows (candles) is too short
    if len(data) < 50:
        return None

    # get the last and second to last row
    current_candle = data.iloc[-1]
    previous_candle = data.iloc[-2]

    ema_50_previous = talib.EMA(data['close'], timeperiod = 50)
    print('ema50: ', ema_50_previous)

    
    if current_candle['high'] > previous_candle['close']:
        atr = current_candle['high'] - previous_candle['close']
    elif current_candle['low'] < previous_candle['close']:
        atr = previous_candle['close'] - current_candle['low']
    elif current_candle['high'] > previous_candle['high'] and current_candle['low'] < previous_candle['low']:
        atr = current_candle['high'] - current_candle['low']

    print('ATR: ', atr)
    TP = 3*atr
    SL = atr

    if (previous_candle['low'] <= ema_50_previous) and (current_candle['open'] < previous_candle['close']) and (current_candle['close'] > previous_candle['open']):
        return 'buy'
    
    
    

    # # return sell signal
    # if current_candle['close'].item() < previous_candle['close'].item():
    #     return 'sell'

    # # return buy signal
    # elif current_candle['close'].item() > previous_candle['close'].item():
    #     return 'buy'

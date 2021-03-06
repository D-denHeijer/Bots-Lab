import websocket
import json
import pandas as pd
from datetime import datetime
import logging

from config_live import data_settings_poloniex
from api_service import send_request

logger = logging.getLogger(__name__)

class PoloniexWebsocketClient:

    def __init__(self, get_buy_or_sell_signal):
        self.get_buy_or_sell_signal = get_buy_or_sell_signal
        self.max_length_ticker_data_list = data_settings_poloniex.get('max_length_ticker_data_list')
        self.id_pair_dictionary = data_settings_poloniex.get('id_pair_dictionary')
        self.pair_ticker_data_list_dictionary = {}

        self.initialize_pair_ticker_data_list_dictionary()

    def initialize_pair_ticker_data_list_dictionary(self):
        for id, pair in self.id_pair_dictionary.items():
            self.pair_ticker_data_list_dictionary[pair] = []

    def on_message(self, ws, message):
        ticker = json.loads(message)

        if not self.contains_ticker_data(ticker= ticker):
            return

        id = self.get_id(ticker=ticker)
        if id in self.id_pair_dictionary:
            pair = self.id_pair_dictionary[id]
            self.store_ticker_data(pair=pair, ticker=ticker)
            self.run_bot(pair=pair)

    def contains_ticker_data(self, ticker):
        return len(ticker) > 2

    def get_id(self, ticker):
        return str(ticker[2][0])

    def store_ticker_data(self, pair, ticker):
        ticker_data = self.get_ticker_data(ticker=ticker)
        self.append_to_pair_ticker_data_list_dictionary(pair=pair, ticker_data=ticker_data)

    def get_ticker_data(self, ticker):
        return ticker[2]

    def append_to_pair_ticker_data_list_dictionary(self, pair, ticker_data):
        ticker_data.append(datetime.now())
        self.pair_ticker_data_list_dictionary[pair].append(ticker_data)
        
        if len(self.pair_ticker_data_list_dictionary[pair]) > self.max_length_ticker_data_list:
            self.pair_ticker_data_list_dictionary[pair].pop(0)

    def run_bot(self, pair):
        ticker_data_list= self.pair_ticker_data_list_dictionary[pair]
        df = self.create_dataframe(ticker_data_list=ticker_data_list)
        buy_or_sell_signal = self.get_buy_or_sell_signal(data=df)
        logger.debug('buy signal for pair {}: {}'.format(pair, buy_or_sell_signal))

        # for now the revenyou api accepts only buy signals!
        if buy_or_sell_signal == 'buy':
            send_request(pair=pair)

    def create_dataframe(self, ticker_data_list):
        df = pd.DataFrame(ticker_data_list, columns=['pair_id', 'close', 'low_ask', 'high_ask', 'percentage_change', 'volume', 
            'quote_volume', 'is_frozen', 'high', 'low', 'date'])
        df = df.set_index(['date'])

        columns = ['close', 'low_ask', 'high_ask', 'percentage_change', 'volume', 
            'quote_volume', 'is_frozen', 'high', 'low']
        for column in columns:
            df[column] = df[column].astype(float)

        return df


    def on_error(self, ws, error):
        print("Websocker error: {}", error)

    def on_close(self, ws):
        print("Websocket is closed")

    def on_open(self, ws):
        subscribe_request =  { "command": "subscribe", "channel": 1002 }
        ws.send(json.dumps(subscribe_request))

    def listen(self):
        websocket.enableTrace(True)
        uri = 'wss://api2.poloniex.com'
        ws = websocket.WebSocketApp(uri,
                                on_message = lambda ws,msg: self.on_message(ws, msg),
                                on_error   = lambda ws,msg: self.on_error(ws, msg),
                                on_close   = lambda ws: self.on_close(ws),
                                on_open    = lambda ws: self.on_open(ws))
        ws.on_open = lambda ws: self.on_open(ws)
        ws.run_forever() 
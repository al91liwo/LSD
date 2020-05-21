import datetime
import plotly.graph_objects as go
import pandas as pd
from src.helper import preprocess_binance, preprocess_binance_live
import time

class Dataset(object):

    pass


class StockDataset(Dataset):

    def __init__(self, symbol, _preprocess=lambda x: x):
        self.symbol = symbol
        self.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        self.df = pd.DataFrame(columns=self.columns)
        self.df.index = self.df['time']
        self._preprocess = _preprocess

    def _add_entry(self, entry):
        return self._preprocess(entry)


class BinanceDataset(StockDataset):
    """
        1499040000000,      # Open time
        "0.01634790",       # Open
        "0.80000000",       # High
        "0.01575800",       # Low
        "0.01577100",       # Close
        "148976.11427815",  # Volume
        1499644799999,      # Close time
        "2434.19055334",    # Quote asset volume
        308,                # Number of trades
        "1756.87402397",    # Taker buy base asset volume
        "28.46694368",      # Taker buy quote asset volume
        "17928899.62484339" # Can be ignored
    """


    def __init__(self, symbol, _preprocess=preprocess_binance):
        super().__init__(symbol=symbol, _preprocess=_preprocess)
        self.columns = ['openTime', 'open', 'high', 'low', 'close', 'volume',
                        'closeTime', 'quoteAssetVolume', 'numberOfTrades',
                        'takerBuyBaseAssetVolume', 'takerBuyQuoteAssetVolume']
        self.df = pd.DataFrame(columns=self.columns)
        self.df.set_index(keys='openTime', inplace=True)

    def _add_entry(self, entry):
        entry = super()._add_entry(entry)
        entry = pd.DataFrame([entry], columns=self.columns)
        self.df = self.df.append(entry)
        self.df.index = self.df[self.columns[0]]
        self.df.sort_index(inplace=True)

    def _add_entries(self, entries):
        for entry in entries:
            self._add_entry(entry)

    def get_figure(self, column, name=None, type='scatter', **kwargs):

        if not name:
            name = column
        if not (column in self.columns):
            raise ValueError(f'{column} is not in {self.columns}')
        figure = {
            'x': self.df.index,
            'y': self.df[column],
            'type': type,
            'name': name,
            **kwargs
        }
        return figure

    def get_ohlc_figure(self, title=None):
        if not title:
            title = self.symbol

        figure = go.Figure(
            data=[
                go.Candlestick(x=self.df.index,
                               open=self.df['open'],
                               high=self.df['high'],
                               low=self.df['low'],
                               close=self.df['close'])
            ],
        )
        figure.update_layout(xaxis_rangeslider_visible=False)
        return figure


class LiveBinanceDataset(BinanceDataset):
    """
    "e": "trade",     # Event type
    "E": 123456789,   # Event time
    "s": "BNBBTC",    # Symbol
    "t": 12345,       # Trade ID
    "p": "0.001",     # Price
    "q": "100",       # Quantity
    "b": 88,          # Buyer order Id
    "a": 50,          # Seller order Id
    "T": 123456785,   # Trade time
    "m": true,        # Is the buyer the market maker?
    "M": true         # Ignore.
    """

    def __init__(self, symbol, _preprocess=preprocess_binance_live):
        super().__init__(symbol, _preprocess=_preprocess)
        self.columns = ['eventTime', 'tradeTime', "price", "quantity", "qp"]
        self.df = pd.DataFrame(columns=self.columns)
        self.df.set_index(keys='eventTime', inplace=True)
        now = int(round(time.time() * 1000))
        self._add_entry({'E': now, 'T': now, 'p': 0, 'q': 0})

    def get_ohlc_figure(self, title=None):
        if not title:
            title = self.symbol

        figure = go.Figure(
            data=[
                go.Scattergl(x=self.df.index,
                             y=self.df['qp'])
            ],
        )
        figure.update_layout(xaxis_rangeslider_visible=False)
        return figure


class TimeSeriesDataset(Dataset):

    def __init__(self, x, y):

        y.update({'time': x})
        self.values = pd.DataFrame(y)

    def get_figure(self):

        figures = [
            {'x': self.values['time'],
             'y': self.values[x], 'type': 'scatter', 'name': x}
            for x in self.values.columns if x != 'time']
        return figures

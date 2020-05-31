import datetime
import plotly.graph_objects as go
import pandas as pd
from src.helper import preprocess_binance, preprocess_binance_live
import time


class Dataset(object):
    """
    Standard Dataset class
    Includes data, data queue, current figure and preprocessing tool
    """
    def __init__(self, data, *args, **kwargs):
        # TODO: Data should be separated for different views.
        self._data = data
        self.queued_data = []
        # TODO: A dataset may define different figures (views).
        self.figure = kwargs.pop('figure', {})
        self.preprocess = kwargs.pop('preprocess', lambda x: x)

    def get_figure(self):
        """
        Get current figure
        :return: ValueError if the figure is not defined, else the figure
        """
        if self.figure:
            return self.figure
        raise ValueError("No figure defined")

    def add_entry(self, entry):
        """

        :param entry:
        :return:
        """
        if entry:
            self.queued_data.append(self.preprocess(entry))

    def update(self, *args, **kwargs):
        while len(self.queued_data) > 1:
            current = self.queued_data.pop()
            self._to_figure(current, *args, **kwargs)

    def _to_figure(self, current, *args, **kwargs):
        """
        Add current entry to the figure
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError("Need to implement me first")


class TimeSeriesDataset(Dataset):
    """
    TODO: create figure for infinite many columns which maps the values correctly.
    """
    def _to_figure(self, current, *args, **kwargs):
        x = []
        y = []
        if 'x' in self.figure.keys():
            x = self.figure.get('x', [])
        x.append(self._get_x(current))
        self.figure.update({'x': x})
        if 'y' in self.figure.keys():
            y = self.figure.get('y', [])
        y.append(self._get_y(current))
        self.figure.update({'y': y})


class StockDataset(TimeSeriesDataset):

    def __init__(self, data, _preprocess=lambda x: x):
        super().__init__(data)
        self.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        self.df = pd.DataFrame(columns=self.columns)
        self.df.index = self.df['time']
        self._preprocess = _preprocess

    def _to_figure(self, current, *args, **kwargs):
        pass


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




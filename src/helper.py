import numpy as np
import pandas as pd
import datetime

def generate_random_data(num_instances=100):
    base = datetime.datetime.now()
    time = np.array([base+datetime.timedelta(hours=x) for x in range(num_instances)])
    high = np.array([np.random.sample() for _ in range(num_instances)])
    open = np.array([np.random.sample() for _ in range(num_instances)])
    low = np.array([np.random.sample() for _ in range(num_instances)])
    close = np.array([np.random.sample() for _ in range(num_instances)])

    return time, {'high': high, 'open': open,
                  'low': low, 'close': close}


def preprocess_binance_live(entry):
    print(entry)
    eventTime = datetime.datetime.fromtimestamp(entry['E']/1000.)
    tradeTime = datetime.datetime.fromtimestamp(entry['T']/1000.)
    price = float(entry['p'])
    quantity = float(entry['q'])
    qp = price * quantity
    return [eventTime, tradeTime, price, quantity, qp]

def preprocess_binance(entry):
    openTime = datetime.datetime.fromtimestamp(entry[0]/1000.)
    open = float(entry[1])
    high = float(entry[2])
    low = float(entry[3])
    close = float(entry[4])
    volume = float(entry[5])
    closeTime = datetime.datetime.fromtimestamp(entry[6]/1000.)
    quoteAssetVolume = float(entry[7])
    numberOfTrades = int(entry[8])
    takerBuyBaseAssetVolume = float(entry[9])
    takerBuyQuoteAssetVolume = float(entry[10])

    return [openTime, open, high, low, close, volume, closeTime, quoteAssetVolume,
            numberOfTrades, takerBuyBaseAssetVolume, takerBuyQuoteAssetVolume]


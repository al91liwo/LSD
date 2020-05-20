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

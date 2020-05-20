import datetime
import pandas as pd


class Dataset(object):

    pass


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

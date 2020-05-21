import dash
import dash_core_components as dcc
import dash_html_components as html
from example.kanbanflow import get_entries, get_data, all_tasks
from src.structure import TimeSeriesDataset
from src.helper import generate_random_data


#
# data = generate_random_data()
# dataset = TimeSeriesDataset(data[0], data[1])
# df = dataset.values


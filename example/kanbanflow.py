import requests
import json
import dash
import datetime
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

cookie = "ga=GA1.2.367344708.1589955298; _gid=GA1.2.64454875.1589955298; kanbanflow_com=s%3A38Ptd1_S_pQYrA5s2Rd0_mB4OD0XVbJ3.igQdPUKn8Es1cbDqWtDcskSYs6eNOyueRRZAZxRxDDI"
base = 'https://kanbanflow.com/task/{task}/time-log'
thesis = 'T5sdA3KJ'
statml = 'T5teUqnv'
work = 'H1N7xhZS'
statml_homework = 'pjwG7dmt'
trading = 'E4mKgvHc'
time_format = "%Y-%m-%dT%H:%M:%S"

all_tasks = [thesis, statml, statml_homework, trading, work]


class Task:

    def __init__(self, start, end, task):
        self.start = datetime.datetime.strptime(start.split('.')[0].replace("Z", ""), time_format)
        self.end = datetime.datetime.strptime(end.split('.')[0].replace("Z", ""), time_format)
        self.minutes = (self.end - self.start).total_seconds()/60
        self.task = task


class Tasks:

    def __init__(self, entries):
        self.start = list()
        self.end = list()
        self.minutes = list()
        self.task = entries[0].task
        for entry in entries:
            if entry.minutes < 0:
                continue
            self.start.append(entry.start)
            self.end.append(entry.end)
            self.minutes.append(entry.minutes)


    def get_df(self):
        return pd.DataFrame({'start': self.start, 'end': self.end, 'minutes': self.minutes})

def get_data(task):
    headers = {'cookie': cookie}
    response = requests.get(base.format(task=task), headers=headers)

    return json.loads(response.content.decode('utf-8'))


def get_entries(data):
    workEntries = data['workEntries']
    manualEntries = data['manualTimeEntries']

    startTimestamp = 'startTimestamp'
    actions = 'actions'
    end = 'end'
    endTimestamp = 'timestamp'
    taskName = 'taskName'
    res = []
    for work in workEntries:
        start_time = work[startTimestamp]
        end_time = work[actions][0][end][endTimestamp]
        task = work[actions][0][taskName]
        res.append(Task(start_time, end_time, task))
    for manual in manualEntries:
        start_time = manual['createdTimestamp']
        end_time = manual['endTimestamp']
        task = manual['taskName']
        res.append(Task(start_time, end_time, task))
    return Tasks(res)



#
# data = generate_random_data()
# dataset = TimeSeriesDataset(data[0], data[1])
# df = dataset.values

dfs = list()
entries = list()
sec_entry = list()
for entry in all_tasks:
    tasks = get_entries(get_data(entry))
    task = tasks.task
    df = tasks.get_df()
    df.index = df['start']
    df = df.sort_index()
    week = df.resample('W').sum()
    entries.append({
        'x': df['start'], 'y': df['minutes'], 'type': 'bar', 'name': task
    })
    sec_entry.append({
        'x': week.index, 'y': week['minutes'].apply(lambda x: x/60), 'type': 'bar', 'name': task
    })

app.layout = html.Div(children=[
    html.H1(children='Alex Lind GmbH'),

    dcc.Graph(
        id='minutes all',
        figure={
            'data': entries,
            'layout': {
                'title': 'Kanbanflow reverse engineered'
            }
        }
    ),
    dcc.Graph(
        id='minutes weekly',
        figure={
            'data': sec_entry,
            'layout': {
                'title': 'Weekly Hours'
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_core_components as dcc
import dash_html_components as html
from data.config import api_key, api_secret
from binance.client import Client
from src.structure import BinanceDataset, LiveBinanceDataset
from dash.dependencies import Input, Output
from binance.websockets import BinanceSocketManager

INTERVAL = [Client.KLINE_INTERVAL_1HOUR, Client.KLINE_INTERVAL_1DAY,
            Client.KLINE_INTERVAL_1MINUTE, Client.KLINE_INTERVAL_1MONTH,
            Client.KLINE_INTERVAL_1WEEK, Client.KLINE_INTERVAL_2HOUR,
            Client.KLINE_INTERVAL_3DAY, Client.KLINE_INTERVAL_3MINUTE,
            Client.KLINE_INTERVAL_4HOUR, Client.KLINE_INTERVAL_5MINUTE,
            Client.KLINE_INTERVAL_6HOUR, Client.KLINE_INTERVAL_8HOUR,
            Client.KLINE_INTERVAL_12HOUR, Client.KLINE_INTERVAL_15MINUTE,
            Client.KLINE_INTERVAL_30MINUTE]


client = Client(api_key, api_secret)


symbol = "BNBBTC"
# fetch 1 minute klines for the last day up until now
klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")


td = BinanceDataset(symbol=symbol)
td._add_entries(klines)

live_figure = LiveBinanceDataset(symbol=symbol)

figure = td.get_ohlc_figure()

app = dash.Dash()


app.layout = html.Div([
    html.Div([
        html.Div([
           html.H4("""Select Symbol""",
                   style={'margin-right': '2em'})
        ]),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=
            [{'label': x['symbol'], 'value': x['symbol']}
             for x in client.get_all_tickers()],
            value='LTCBTC',
            style=dict(
                width='40%',
                verticalAlign="middle"
            ),
        ),
        html.Div([
           html.H4("""Select Interval""",
                   style={'margin-right': '2em'})
        ]),
        dcc.Dropdown(
            id='time-dropdown',
            options=[{'label': x, 'value': x} for x in INTERVAL],
            value=INTERVAL[0],
            style=dict(
                width='40%',
                verticalAlign="middle"
            ),
        ),

    ]),

    dcc.Graph(id='stock_graph', figure=figure),

    dcc.Graph(id='stock_graph_live', figure=live_figure.get_ohlc_figure()),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    ],


)

@app.callback(
    Output(component_id='stock_graph_live', component_property='figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_live(n):
    figure = live_figure.get_ohlc_figure()
    return figure

def update(msg):
    live_figure._add_entry(msg)


bm = BinanceSocketManager(client)
conn_key = bm.start_trade_socket('BNBBTC', update)

bm.start()

@app.callback(
    Output(component_id='stock_graph', component_property='figure'),
    [Input(component_id='symbol-dropdown', component_property='value'),
     Input(component_id='time-dropdown', component_property='value')]
)
def update_stock_graph(symbol, interval):
    klines = client.get_historical_klines(symbol, interval, "1 day ago UTC")
    td = BinanceDataset(symbol=symbol)
    td._add_entries(klines)
    return td.get_ohlc_figure()

# def live_figure()

app.run_server(debug=True)
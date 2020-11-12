import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from app import app
from functions.functions import *
from datetime import datetime
import yfinance as yf
from plotly.subplots import make_subplots

from pyorbital.orbital import Orbital
satellite = Orbital('TERRA')

#Fake data
df = pd.DataFrame(
    {'id':1
    ,'Date':'2020-11-11 21:10:10'
    ,'Open Amount':'5000'
    ,'Close Amount':'5100'
    ,'Position':'BUY'
    ,'Open':'1.782'
    ,'Close':'1.785'
    ,'Profit /Loss':'50%'
    ,'Symbol':'EURUSD',}
    ,[0])

# to do funkcji
controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Strategy"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in df.columns
                    ],
                    value="Date",
                ),
            ]
        ),
    ],
    body=True,
    style={'padding-bottom':0,'padding-top':0, }
)

def create_layout(app):
    return html.Div(
        [
            html.Div(
                [
                    dbc.Row(
                            dbc.Col(children=get_top_bar())
                            ),
                    dbc.Row(
                        [
                            dbc.Col(controls,sm=6,style={'text-align':'center','margin-top':'5px'}),
                            dbc.Col(controls,sm=6,style={'text-align':'center','margin-top':'5px'}),
                        ]
                    ),
                ]
            ),

            html.Div(
                [   dbc.Row(
                            dbc.Col( 
                                    dcc.Graph(
                                        id='live-update-text',
                                        config={"displayModeBar": False,
                                                'scrollZoom': True,}
                                        )
                            )
                    ),
                    dbc.Row(
                            dbc.Col(children=get_bottom_bar(df))
                    ),
                    dcc.Interval(
                        id='interval-component',
                        interval=1*5000, # in milliseconds
                        n_intervals=0
                    ),
                ] 
            )
        ]
    )

@app.callback(Output('live-update-text', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    #generowanie wykresów pod strategie Renko + MACD do funkcji
    now = datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")
    df = yf.download(tickers="EURUSD=X",period='1d',interval='5m')
    max_candle = df.index.max().strftime("%d/%m/%Y %H:%M")

    df["macd"]= MACD(df,12,26,9)[0]
    df["macd_sig"]= MACD(df,12,26,9)[1]
    df['renko'] = renko_DF(df)

    fig = make_subplots(rows=3,cols=1,row_heights=[0.8,0.3,0.3],
                        specs=[[{"secondary_y": False}],
                            [{"secondary_y": True}],
                            [{"secondary_y": False}]
                        ],subplot_titles=("<b>EURUSD Price</b>", "", "")
                        ,vertical_spacing=0.05
                        )
    #Annotations
    #Candles
    fig.add_trace(go.Candlestick(x=df.index,
                open=df.Open,
                high=df.High,
                low=df.Low,
                close=df.Close, name='Candles'),row=1,col=1)
    
    #MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD'),
              row=2, col=1,secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df['macd_sig'], name='MACD_signal'),
              row=2, col=1,secondary_y=False)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'],name='Volume'),
              row=2, col=1,secondary_y=True)
    
    #Renko
    fig.add_trace(
                    go.Scatter(x=df.index
                            , y=df['renko']
                            , mode='markers'
                            ,marker=dict(
                                color=(
                                        (df.renko > 0)
                                    ).astype('int'),
                                    colorscale=[[0, 'red'], [1, 'green']] 
                            ),
                    name='Renko'),
              row=3, col=1,secondary_y=False)



    fig.update_layout(title=f'<sub>Max Candle: {max_candle}</sub><br><sub>Last request (5s delay): {now}</sub>'
    ,height=700,
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig
    
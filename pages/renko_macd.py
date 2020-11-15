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
import dash_daq as daq
import os

from pyorbital.orbital import Orbital
satellite = Orbital('TERRA')

#Fake data
df_fake = pd.DataFrame(
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

def create_layout(app):
    return html.Div(
        [
            html.Div(
                [   
                    dbc.Row(
                        dbc.Col(html.H3("EUR/USD"),style={'text-align':'center'},className='title'),
                    ),
                    dbc.Row(
                        [
                            dbc.Col(card('Type of strategy'),sm=2,style={'text-align':'center','margin-top':'5px'}),
                            dbc.Col(card('Strategy name'),sm=4,style={'text-align':'center','margin-top':'5px'}),
                            dbc.Col(card('Indicators'),sm=4,style={'text-align':'center','margin-top':'5px'}),
                            dbc.Col(  
                                    dbc.Card(
                                                daq.BooleanSwitch(id='start-stop-button',
                                                on=True,
                                                label="Stop/Start live updating",
                                                labelPosition="top",
                                                style={'padding-bottom':'5px'}
                                                )
                                        ),sm=2,style={'text-align':'center','margin-top':'5px'}
                                    ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(dbc.Button("BUY", color="success", className="mr-1",id='buy-eurusd'),width=3,style={'text-align':'right'}),
                            dbc.Col(dbc.Button("SELL", color="danger", className="mr-1",id='sell-eurusd'),width=3),
                        ], justify='center', style={"margin-top":10}
                    )
                ]
            ),
            html.Div(
                [     
                    dbc.Row(
                            dbc.Col( 
                                    dcc.Graph(
                                        id='live-update-text',
                                        config={"displayModeBar": False,
                                                'scrollZoom': True,
                                                }
                                        )
                            ),style={'margin-top':0}
                    ),
                    dbc.Row(
                            dbc.Col(children=get_bottom_bar(df_fake))
                    ),
                    dcc.Interval(
                        id='interval-component',
                        interval=1*5000, # in milliseconds
                        n_intervals=0
                    ),
                ] 
            ),
            html.Div(id='hidden-div', style={'display':'none'}),
            dcc.Store(id='memory-output'),
        ]
    )

# Live update data switch
@app.callback(
    Output('interval-component', 'disabled'),
    [Input('start-stop-button', 'on')])
def callback_func_start_stop_interval(button_clicks):
    if button_clicks:
        return False
    else:
        return True

#Get data and store in Dash
@app.callback(Output('memory-output', 'data'),
              [Input('interval-component', 'n_intervals')])
def get_data_from_api(n):
    df = yf.download(tickers="EURUSD=X",period='1d',interval='5m')
    df.reset_index(inplace=True)
    return df.to_dict('records')




#Save BUY/SELL after click
@app.callback(Output('hidden-div','children'),
    [Input('buy-eurusd','n_clicks')],
    [State('memory-output','data')])
def addAnnotation(click,data):
    df=pd.DataFrame(data)
    if not os.path.isfile('orders.csv'):
        df[df['Datetime']==df['Datetime'].max()].to_csv('orders.csv',sep=";")
    else: # else it exists so append without writing the header
        df[df['Datetime']==df['Datetime'].max()].to_csv('orders.csv', mode='a', header=False,sep=";")




@app.callback(Output('live-update-text', 'figure'),
              [Input('memory-output', 'data')])
def update_metrics(data):
    #generowanie wykresów pod strategie Renko + MACD do funkcji
    now = datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")

    df=pd.DataFrame(data)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    max_candle = df['Datetime'].max().strftime("%d/%m/%Y %H:%M:%S")
    
    df["macd"]= MACD(df,12,26,9)[0]
    
    df["macd_sig"]= MACD(df,12,26,9)[1]
    
    df['renko'] = renko_DF(df)
    
    
    fig = make_subplots(rows=3,cols=1,row_heights=[0.8,0.3,0.3],
                        specs=[[{"secondary_y": False}],
                            [{"secondary_y": True}],
                            [{"secondary_y": False}]
                        ],subplot_titles=("<b>Price</b>", "", "")
                        ,vertical_spacing=0.05
                        )
    #Annotations
    #Candles
    fig.add_trace(go.Candlestick(x=df.Datetime,
                open=df.Open,
                high=df.High,
                low=df.Low,
                close=df.Close, name='Candles'),row=1,col=1)
    
    #MACD
    fig.add_trace(go.Scatter(x=df.Datetime, y=df['macd'], name='MACD'),
              row=2, col=1,secondary_y=False)
    fig.add_trace(go.Scatter(x=df.Datetime, y=df['macd_sig'], name='MACD_signal'),
              row=2, col=1,secondary_y=False)
    fig.add_trace(go.Bar(x=df.Datetime, y=df['Volume'],name='Volume'),
              row=2, col=1,secondary_y=True)
    
    #Renko
    fig.add_trace(
                    go.Scatter(x=df.Datetime
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




    
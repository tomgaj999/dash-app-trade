import pandas as pd
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib
import yfinance as yf
from stocktrends import Renko
import numpy as np
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objs as go
import dash_core_components as dcc
from plotly.tools import mpl_to_plotly
import dash
import dash_html_components as html
import dash_core_components as dcc

def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy()
    df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df["MACD"],df["Signal"])


def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def slope(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

def renko_DF(DF):
    "function to convert ohlc data into renko bricks"
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,4,5]]
    print(df.shape)
    df.columns = ["date","open","close","high","low","volume"]
    df2 = Renko(df)
    print(type(df2))
    print(round(ATR(DF,120)["ATR"][-1],4))
    df2.brick_size = round(ATR(DF,120)["ATR"][-1],4)
    renko_df = df2.get_ohlc_data()
    print(renko_df.shape)
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    for i in range(1,len(renko_df["bar_num"])):
        if renko_df["bar_num"][i]>0 and renko_df["bar_num"][i-1]>0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1]<0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    renko_df.set_index(['date'],inplace=True,drop=True)
    return renko_df

def PlotRenko(DF):
    # Turn interactive mode off
    #plt.ioff()
    df = DF.copy()
 
    # number of bars to display in the plot
    num_bars = df.shape[0]
 
    # get the last num_bars
    df = df.tail(num_bars)
    renkos = zip(df['open'],df['close'])
 
    # compute the price movement in the Renko
    price_move = abs(df.iloc[1]['open'] - df.iloc[1]['close'])
 
    # create the figure
    fig = plt.figure(1)
    fig.clf()
    axes = fig.gca()
 
    # plot the bars, blue for 'up', red for 'down'
    index = 1
    for open_price, close_price in renkos:
        if (open_price < close_price):
            renko = matplotlib.patches.Rectangle((index,open_price), 1, close_price-open_price, edgecolor='darkgreen', facecolor='green', alpha=0.5)
            axes.add_patch(renko)
        else:
            renko = matplotlib.patches.Rectangle((index,open_price), 1, close_price-open_price, edgecolor='darkred', facecolor='red', alpha=0.5)
            axes.add_patch(renko)
        index = index + 1
 
    # adjust the axes
    plt.xlim([0, num_bars])
    plt.ylim([min(min(df['open']),min(df['close'])), max(max(df['open']),max(df['close']))])
    plt.xlabel('Bar Number')
    plt.ylabel('Price')
    plt.grid(True)
    #plt.show()
 



df = yf.download(tickers="EURUSD=X",period='1d',interval='5m')
# key_path = "OUJX2TUIJ0YKBH99"
# ts = TimeSeries(key=key_path, output_format='pandas')
# df = ts.get_intraday(symbol="EURUSD",interval='5min', outputsize='full')[0]
df["macd"]= MACD(df,12,26,9)[0]
df["macd_sig"]= MACD(df,12,26,9)[1]
# print(df.shape)
renko = renko_DF(df)
print(renko)
# print(renko.shape)
#df = df.merge(renko,left_index=True, right_index=True)
# print(df)
#print(df['macd'])
# plot = PlotRenko(renko)
# print(type(plot))

# fig_url=mpl_to_plotly(plot)

# app.layout= html.Div([
#     dcc.Graph(id= 'matplotlib-graph', figure=plotly_fig)

# ])

# app.run_server(debug=True, port=8010, host='localhost')
import numpy as np 
import pandas as pd
import datetime as dt
import yfinance as yf 
from pandas_datareader import data as pdr
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os 

csvfilename = "3B_Total.csv"
stocklist = pd.read_csv(csvfilename, engine="python", encoding="ISO-8859-1")

yf.pdr_override()
start = dt.datetime.now() - dt.timedelta(days=150)  # timedelta: the date 150 days before 
now = dt.datetime.now()

def find_amount(data, i):
    return data['Volume'].iloc[-i] * data['Close'].iloc[-i]

def cross(parameter1, parameter2, i):
    return (parameter1.iloc[-i-1] < parameter2.iloc[-i-1]) and (parameter1.iloc[-i] > parameter2.iloc[-i]) and (parameter1.iloc[-i] > parameter1.iloc[-(i+1)])

def cross_within_period(parameter1, parameter2, begin, period): 
    for i in range(begin, begin + period + 1):
        if cross(parameter1, parameter2, i):
            return i
    return 0

while True:
    try:
        searchPeriod = int(input("Enter the searching period (in days >=0): "))
        if searchPeriod >= 0:
            break
        else:
            print("Please enter a valid search period (>=0)")
    except ValueError:
        print("Please enter a valid integer for search period")

Dual_MA_upward_trend = []
for i in range(len(stocklist)):
    stock = stocklist.iloc[i]["Symbol"]
    print(f"{i+1}/{len(stocklist)} {stock}")
    try:
        df = yf.download(stock, start, now)
    except Exception as e:
        print(f"Error retrieving data for {stock}: {e}")
        continue

    if len(df) < 80:
        print(f"Not enough data points for {stock}")
        continue 

    if find_amount(df, 2) < 2e7:
        print(f"Turnover of {stock} is too low")
        continue

    MA20 = df["Close"].rolling(window=20).mean()
    EMA20 = df["Close"].ewm(span=20).mean()

    MA60=df["Close"].rolling(window=60).mean()
    EMA60=df["Close"].ewm(span=60).mean()
    
    MA120=df["Close"].rolling(window=120).mean()
    EMA120=df["Close"].ewm(span=120).mean()

    # Check for EMA20 crossing above MA20 within the entire data range
    if cross_within_period(parameter1=EMA20, parameter2=MA20, begin=1, period=searchPeriod):
        if cross_within_period(parameter1=EMA60, parameter2=MA60, begin=1, period=searchPeriod):
            if cross_within_period(parameter1=EMA120, parameter2=MA120, begin=1, period=searchPeriod): ## ideal case for being bullish
                closeP_above_MA=True
                for j in range(searchPeriod+1):
                    if df["Close"].iloc[-j]< EMA20.iloc[-j]  or df["Close"].iloc[-j]< MA20.iloc[-j] or 	df["Close"].iloc[-j]< EMA60.iloc[-j] or df["Close"].iloc[-j]< MA60.iloc[-j] or df["Close"].iloc[-j]< EMA120.iloc[-j] or df["Close"].iloc[-j]< MA120.iloc[-j]:
                        closeP_above_MA=False
                        break

                if closeP_above_MA:
                    Dual_MA_upward_trend.append(stock)





		        




print(f"\nMA20_strategy, {searchPeriod}")  # output the MACD result 
for i, stock in enumerate(Dual_MA_upward_trend):
    print(f"{stock}")

## interchange whether includes 120 days time frame
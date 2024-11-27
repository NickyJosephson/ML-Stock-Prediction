import pandas as pd
import numpy as np

def calculate_macd(df, short_span=12, long_span=26, signal_span=9):
    """Calculate MACD and MACD Signal line."""
    df['EMA_12'] = df['Close'].ewm(span=short_span, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=long_span, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=signal_span, adjust=False).mean()
    df.drop(['EMA_12', 'EMA_26'], axis=1, inplace=True)

def calculate_rsi(df, period=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = df['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

def calculate_vwap(df):
    """Calculate Volume Weighted Average Price (VWAP)."""
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()

def calculate_ema(df, span=200):
    """Calculate Exponential Moving Average (EMA)."""
    df['EMA_200'] = df['Close'].ewm(span=span, adjust=False).mean()
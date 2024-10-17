import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(symbols, start_date, end_date, interval='1d', save_path='data/raw/'):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for symbol in symbols:
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        data.to_csv(f'{save_path}{symbol}.csv')
        print(f'Data for {symbol} saved.')
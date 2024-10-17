# src/data_preprocessing.py

import pandas as pd
import os

def load_and_preprocess(symbols, data_path='data/raw/', save_path='data/processed/'):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for symbol in symbols:
        df = pd.read_csv(f'{data_path}{symbol}.csv', parse_dates=['Date'], index_col='Date')
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        # Additional preprocessing steps can be added here
        df.to_csv(f'{save_path}{symbol}_processed.csv')
        print(f'Processed data for {symbol} saved.')
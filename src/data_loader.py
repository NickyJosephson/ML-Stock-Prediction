# import yfinance as yf
# import pandas as pd
# import os

# def fetch_stock_data(symbols, start_date, end_date, interval='1d', save_path='data/raw/'):
#     if not os.path.exists(save_path):
#         os.makedirs(save_path)
#     for symbol in symbols:
#         data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
#         data.to_csv(f'{save_path}{symbol}.csv')
#         print(f'Data for {symbol} saved.')

import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(symbols, start_date, end_date, interval='1d', save_path='data/raw/'):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    for symbol in symbols:
        print(f"Fetching {symbol}...")
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)
        
        # Check if data is not empty
        if not data.empty:
            # Reset index to move Date into a normal column
            data = data.reset_index()

            # Save to CSV
            file_path = os.path.join(save_path, f"{symbol.replace('^','')}.csv")  # Remove '^' from filename
            data.to_csv(file_path, index=False)
            print(f"✅ Data for {symbol} saved to {file_path}.")
        else:
            print(f"⚠️ Warning: No data fetched for {symbol}.")

# Example usage
symbols = ["^GSPC", "QQQ", "SPY", "^GSPX", "ES=F"]  # Correct Yahoo symbols
fetch_stock_data(symbols, start_date="2010-01-01", end_date="2024-12-31")
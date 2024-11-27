# main.py

from src.data_loader import fetch_stock_data
from src.data_preprocessing import load_and_preprocess
from src.train import prepare_data, train_model
from src.evaluate import evaluate_model
import pandas as pd

stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA', 'BRK-A', 'JNJ', 'V', 'WMT']
start_date = '2010-01-01'
end_date = '2023-10-01'

# Step 1: Fetch data
fetch_stock_data(stock_symbols, start_date, end_date)

# Step 2: Preprocess data
load_and_preprocess(stock_symbols)

# Step 3: Load processed data
dfs = []
for symbol in stock_symbols:
    df = pd.read_csv(f'data/processed/{symbol}_processed.csv', parse_dates=['Date'], index_col='Date')
    dfs.append(df)

# # Combine data or process individually
for symbol, df in zip(stock_symbols, dfs):
    # Prepare data
    time_steps = 60
    X, y, scaler = prepare_data(df, time_steps)
    input_shape = (X.shape[1], 1)

    # Train model
    model = train_model(X, y, input_shape, symbol)

    # Evaluate model (using the last 20% of the data as test set)
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    evaluate_model(model, X_test, y_test, scaler)
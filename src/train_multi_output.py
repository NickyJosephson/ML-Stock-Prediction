import numpy as np
import pandas as pd
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.models import Model
from sklearn.preprocessing import MinMaxScaler
import os

# Define the stock symbols you want to analyze
stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BRK-A', 'JNJ', 'V', 'WMT']
start_date = '2010-01-01'
end_date = '2023-10-01'

# Initialize an empty DataFrame to hold the merged data
main_df = None

# Load and merge the 'Close' price data from each stock
for symbol in stock_symbols:
    file_path = f'data/processed/{symbol}_processed.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
        if not df.empty:
            df = df[['Close']]  # Keep only the 'Close' column
            df.rename(columns={'Close': symbol}, inplace=True)  # Rename the column to the stock symbol
            if main_df is None:
                main_df = df
            else:
                main_df = main_df.join(df, how='inner')  # Merge on the 'Date' index
            print(f"Loaded {symbol} data with shape: {df.shape}")
        else:
            print(f"Warning: {symbol} data is empty. Skipping.")
    else:
        print(f"Warning: File {file_path} not found. Skipping.")

# Ensure that data has been loaded
if main_df is None or main_df.empty:
    raise ValueError("No data loaded. Please check the data files and try again.")

# Prepare the data for multi-output regression
def prepare_data_multi_output(df, time_steps):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df.values)
    X, y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i - time_steps:i])  # Sequence of past 'time_steps' data
        y.append(scaled_data[i])  # Corresponding target values
    X, y = np.array(X), np.array(y)
    return X, y, scaler

time_steps = 60  # Number of past days to consider for each prediction
X, y, scaler = prepare_data_multi_output(main_df, time_steps)
print(f"Prepared data shapes - X: {X.shape}, y: {y.shape}")

# Define the number of stocks (outputs)
num_stocks = len(stock_symbols)

# Create the multi-output LSTM model
def create_multi_output_model(input_shape, num_outputs):
    inputs = Input(shape=input_shape)
    x = LSTM(50, return_sequences=True)(inputs)
    x = LSTM(50)(x)
    outputs = Dense(num_outputs)(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Instantiate and compile the model
input_shape = (X.shape[1], X.shape[2])  # (time_steps, num_stocks)
model = create_multi_output_model(input_shape, num_outputs=num_stocks)

# Train the model
model.fit(X, y, epochs=50, batch_size=32)
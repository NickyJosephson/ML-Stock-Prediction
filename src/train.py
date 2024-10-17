# src/train.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping
from src.model import create_model

def prepare_data(df, time_steps):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df['Close'].values.reshape(-1, 1))
    X, y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i-time_steps:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler

# src/train.py

def train_model(X_train, y_train, input_shape, symbol):
    model = create_model(input_shape)
    early_stop = EarlyStopping(monitor='loss', patience=10)
    model.fit(X_train, y_train, epochs=50, batch_size=32, callbacks=[early_stop])
    # Save the model
    model.save(f'models/{symbol}_model.h5')
    return model
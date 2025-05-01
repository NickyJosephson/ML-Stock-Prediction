import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import joblib

# --- LOAD MODEL AND SCALERS ---
model = load_model("seq2seq_mc_dropout_model.h5", compile=False)
feature_scaler = joblib.load("feature_scaler.pkl")
target_scaler = joblib.load("target_scaler.pkl")

# --- LOAD & PREPROCESS DATA ---
data = pd.read_csv("1_merged_stock_sentiment.csv")
data['spy_return_5d'] = data['spy_Close'].pct_change(5)
data['spy_volatility_5d'] = data['spy_Close'].rolling(5).std()

N = 5  # forecast horizon
for i in range(1, N+1):
    data[f'spy_Close_t+{i}'] = data['spy_Close'].shift(-i)
data.dropna(inplace=True)

features = [
    'spy_Open', 'spy_High', 'spy_Low', 'spy_Close', 'spy_Volume',
    # 'qqq_Close', 'qqq_High', 'qqq_Low', 'qqq_Open', 'qqq_Volume',
    # 'spx_Close', 'spx_High', 'spx_Low', 'spx_Open', 'spx_Volume',
    # 'es_Close', 'es_High', 'es_Low', 'es_Open', 'es_Volume',
    'avg_headline_sentiment', 'avg_article_sentiment',
    'spy_return_5d', 'spy_volatility_5d'
]

future_cols = [f'spy_Close_t+{i}' for i in range(1, N+1)]
scaled_features = feature_scaler.transform(data[features])
scaled_targets = target_scaler.transform(data[future_cols])

# Create sequences
sequence_length = 30
X, y = [], []
for i in range(sequence_length, len(scaled_features)):
    X.append(scaled_features[i-sequence_length:i])
    y.append(scaled_targets[i])

X, y = np.array(X), np.array(y)
y = y.reshape((y.shape[0], N, 1))

# --- MONTE CARLO DROPOUT PREDICTIONS ---
def monte_carlo_predictions(model, X, num_samples=100):
    return np.stack([model(X, training=True).numpy() for _ in range(num_samples)])

mc_preds = monte_carlo_predictions(model, X, num_samples=100)
y_pred_mean = mc_preds.mean(axis=0)
y_pred_std = mc_preds.std(axis=0)

# --- INVERSE TRANSFORM ---
y_pred_mean_inv = target_scaler.inverse_transform(y_pred_mean.reshape(y_pred_mean.shape[0], N))
y_pred_std_inv = y_pred_std.reshape(y_pred_std.shape[0], y_pred_std.shape[1])
y_true_inv = target_scaler.inverse_transform(y.reshape(y.shape[0], N))

# --- PLOT ONE SAMPLE WITH CONE ---
idx = 0
days = np.arange(1, N+1)
plt.figure(figsize=(10, 5))
plt.plot(days, y_true_inv[idx], label='True Path', marker='o')
plt.plot(days, y_pred_mean_inv[idx], label='Predicted Mean', marker='x')
plt.fill_between(days,
                 y_pred_mean_inv[idx] - y_pred_std_inv[idx],
                 y_pred_mean_inv[idx] + y_pred_std_inv[idx],
                 alpha=0.3, label='Uncertainty Cone')
plt.title('5-Day Forecast with MC Dropout Cone')
plt.xlabel('Days Ahead')
plt.ylabel('SPY Close Price')
plt.grid(True)
plt.legend()
plt.show()

# --- OPTIONAL: VIEW MULTIPLE RANDOM TRAJECTORIES ---
num_trajectories = 10
plt.figure(figsize=(10, 5))
for i in range(num_trajectories):
    sample = mc_preds[i, idx].reshape(-1)
    sample_inv = target_scaler.inverse_transform(sample.reshape(1, -1)).flatten()
    plt.plot(days, sample_inv, alpha=0.3)

plt.plot(days, y_pred_mean_inv[idx], label='Mean Prediction', color='black')
plt.plot(days, y_true_inv[idx], label='True Path', color='blue')
plt.title(f'{num_trajectories} Sample Paths from MC Dropout')
plt.xlabel('Days Ahead')
plt.ylabel('SPY Close Price')
plt.legend()
plt.grid(True)
plt.show()

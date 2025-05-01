# Predicting ±1% Price Move Tomorrow Using XGBoost (Fixed & Fully Runnable)

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, classification_report
import xgboost as xgb

# ------------------------------------------------------------------ #
# Feature engineering
# ------------------------------------------------------------------ #

def engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['spy_return_5d']     = df['spy_Close'].pct_change(5)
    df['spy_volatility_5d'] = df['spy_Close'].rolling(5).std()
    df['avg_sentiment']     = (df['avg_headline_sentiment'] + df['avg_article_sentiment']) / 2
    df['sentiment_lag1']    = df['avg_sentiment'].shift(1)
    df['sentiment_delta']   = df['avg_sentiment'] - df['sentiment_lag1']
    df['spy_return_1d']     = df['spy_Close'].pct_change()
    df['gap_pct']           = (df['spy_Open'] - df['spy_Close'].shift(1)) / df['spy_Close'].shift(1)
    df['vol_z']             = (df['spy_Volume'] / df['spy_Volume'].rolling(20).mean()) - 1
    df['sent_div']          = df['avg_sentiment'] - df['spy_return_1d']
    df['spy_return_t+1']    = df['spy_Close'].shift(-1) / df['spy_Close'] - 1
    df['target']            = (df['spy_return_t+1'].abs() >= 0.01).astype(int)
    return df

# ------------------------------------------------------------------ #
# Prepare features / target
# ------------------------------------------------------------------ #

SELECTED_FEATURES = [
    'spy_return_1d', 'spy_return_5d', 'spy_volatility_5d',
    'gap_pct', 'vol_z', 'qqq_Close', 'spx_Close', 'es_Close',
    'avg_sentiment', 'sentiment_delta', 'sent_div'
]

def build_dataset(df: pd.DataFrame):
    df = df.dropna(subset=SELECTED_FEATURES + ['target'])
    X = df[SELECTED_FEATURES]
    y = df['target'].values
    return X, y, df.index

# ------------------------------------------------------------------ #
# Chronological split helper
# ------------------------------------------------------------------ #

def chrono_split(X, y, valid_size=0.15, test_size=0.15):
    n = len(X)
    n_test = int(n * test_size)
    n_valid = int(n * valid_size)
    n_train = n - n_valid - n_test
    return (
        X[:n_train], y[:n_train],
        X[n_train:n_train + n_valid], y[n_train:n_train + n_valid],
        X[n_train + n_valid:], y[n_train + n_valid:]
    )

# ------------------------------------------------------------------ #
# Train model
# ------------------------------------------------------------------ #

from sklearn.base import BaseEstimator, ClassifierMixin

class ScaledModel(BaseEstimator, ClassifierMixin):
    def __init__(self, scaler, clf):
        self.scaler = scaler
        self.clf = clf

    def predict_proba(self, X):
        return self.clf.predict_proba(self.scaler.transform(X))

    def predict(self, X):
        return self.clf.predict(self.scaler.transform(X))

    def get_booster(self):
        return self.clf.get_booster()

def train_model(X_train, y_train, X_valid, y_valid):
    scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
    booster = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='auc',
        max_depth=4,
        n_estimators=2000,
        learning_rate=0.02,
        subsample=0.8,
        colsample_bytree=0.7,
        gamma=1,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        n_jobs=-1
    )

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_valid_scaled = scaler.transform(X_valid)

    booster.fit(
        X_train_scaled, y_train,
        eval_set=[(X_valid_scaled, y_valid)],
        verbose=False
    )

    return ScaledModel(scaler, booster)

# ------------------------------------------------------------------ #
# Evaluation helpers
# ------------------------------------------------------------------ #

def print_metrics(y_true, proba, thresh=0.5):
    roc = roc_auc_score(y_true, proba)
    prec, rec, thr = precision_recall_curve(y_true, proba)
    pr_auc = auc(rec, prec)
    print(f"AUC  : {roc:.4f}")
    print(f"PR‑AUC: {pr_auc:.4f}\n")
    print(classification_report(y_true, (proba > thresh).astype(int)))

# ------------------------------------------------------------------ #
# Main execution block
# ------------------------------------------------------------------ #

data_path = Path("./data/processed/1_merged_stock_sentiment.csv")
df_raw = pd.read_csv(data_path, parse_dates=['date']).sort_values('date')
df     = engineer(df_raw)

X, y, idx = build_dataset(df)
X_train, y_train, X_valid, y_valid, X_test, y_test = chrono_split(X.values, y)

model = train_model(X_train, y_train, X_valid, y_valid)

print("Validation performance")
val_proba = model.predict_proba(X_valid)[:,1]
print_metrics(y_valid, val_proba)

print("Test performance")
test_proba = model.predict_proba(X_test)[:,1]
print_metrics(y_test, test_proba)

precision_target = 0.65
prec, rec, thr = precision_recall_curve(y_valid, val_proba)
thresh = thr[np.argmax(prec >= precision_target)]
print(f"Use p > {thresh:.2f} to get ≈{precision_target*100:.0f}% precision on validation")

output_path = Path("xgb_big_move_model.pkl")
joblib.dump(model, output_path)
print("Model saved to", output_path)

importances = model.get_booster().get_score(importance_type='gain')
fi = pd.DataFrame({
    'feature': list(importances.keys()),
    'gain': list(importances.values())
}).sort_values('gain', ascending=False)
fi.to_csv(output_path.with_suffix('.feature_importance.csv'), index=False)
print("Feature importances saved to", output_path.with_suffix('.feature_importance.csv'))

try:
    fi.head(10).plot(kind='barh', x='feature', y='gain', figsize=(6,4))
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.title("Top‑10 feature gain")
    plt.show()
except Exception as e:
    print("Plotting failed:", e)
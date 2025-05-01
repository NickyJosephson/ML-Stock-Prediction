import joblib
import pandas as pd
from scrapers.yahoo.recent_news import fetch_all_news
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import yfinance as yf
from datetime import datetime, timedelta

#Load FinBERT
device = torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone')
model_bert = AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')
model_bert.to(device)
model_bert.eval()

def get_sentiment_score(texts):
    sentiment_scores = []
    for text in texts:
        encodings = tokenizer(text, truncation=True, padding=True, return_tensors='pt', max_length=512).to(device)
        with torch.no_grad():
            outputs = model_bert(**encodings)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            score = (probs[:, 2] - probs[:, 0]).cpu().numpy()[0]
        sentiment_scores.append(score)
    return sentiment_scores

if __name__ == "__main__":
    articles = fetch_all_news()
    headlines = [article['title'] for article in articles]
    print("Calculating and averaging sentiment scores")
    headline_scores = get_sentiment_score(headlines)
    avg_headline_sentiment = sum(headline_scores) / len(headline_scores)

    df = yf.download("^GSPC", period="30d", interval="1d", progress=False)
    print("Stock Data Fetched")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={
        'Open': 'spx_Open',
        'High': 'spx_High',
        'Low': 'spx_Low',
        'Close': 'spx_Close',
        'Volume': 'spx_Volume'
    }).reset_index().rename(columns={"Date": "date"})
    print("Preprocessing Data")

    data = df.copy()
    data['spx_return_1d'] = data['spx_Close'].pct_change(1)
    data['spx_return_3d'] = data['spx_Close'].pct_change(3)
    data['spx_return_5d'] = data['spx_Close'].pct_change(5)
    data['spx_return_10d'] = data['spx_Close'].pct_change(10)

    data['spx_volatility_3d'] = data['spx_Close'].rolling(3).std()
    data['spx_volatility_5d'] = data['spx_Close'].rolling(5).std()
    data['spx_volatility_10d'] = data['spx_Close'].rolling(10).std()

    data['true_range_spx'] = data['spx_High'] - data['spx_Low']
    data['avg_true_range_5d_spx'] = data['true_range_spx'].rolling(5).mean()

    data['gap_pct_spx'] = (data['spx_Open'] - data['spx_Close'].shift(1)) / data['spx_Close'].shift(1)
    data['vol_z_spx'] = (data['spx_Volume'] / data['spx_Volume'].rolling(20).mean()) - 1

    data['avg_headline_sentiment'] = avg_headline_sentiment
    data['avg_article_sentiment'] = avg_headline_sentiment  # same for now

    data['spx_return_t+1'] = data['spx_Close'].pct_change().shift(-1)
    data['target'] = (data['spx_return_t+1'].abs() >= 0.0075).astype(int)

    data = data.dropna().reset_index(drop=True)

    drop_cols = ['date', 'spx_return_t+1', 'target']
    feature_cols = [col for col in data.columns if col not in drop_cols]
    latest_row = data[feature_cols].tail(1)

    print("Loading Model")
    model = joblib.load('./models/xgb_model.pkl')
    proba = model.predict_proba(latest_row)[0][1]
    pred = model.predict(latest_row)[0]
    print("Model Loaded")

    print(f"\nPrediction: {'Big move' if pred else 'Normal day'}")
    print(f"Probability of ±0.75% SPX move: {proba:.2%}")
import yfinance as yf
import pandas as pd
import numpy as np
import time
import os
from sklearn.preprocessing import StandardScaler

# Output CSV path
csv_path = "sp500_risk_scores.csv"

# Metrics to extract
extra_features = [
    'beta', 'dividendYield', 'revenueGrowth', 'priceToBook',
    'returnOnAssets', 'returnOnEquity', 'marketCap', 'shortRatio'
]

def get_sp500_tickers():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    return table['Symbol'].tolist()

def compute_features(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist.empty:
            return None

        hist['Return'] = hist['Close'].pct_change()
        volatility = np.std(hist['Return']) * 100
        cumulative = (1 + hist['Return'].fillna(0)).cumprod()
        drawdown = (cumulative / cumulative.cummax() - 1).min() * 100

        info = stock.info
        pe_ratio = info.get('trailingPE', 25.0)

        # Normalize risk score
        data = np.array([[volatility, abs(drawdown), pe_ratio]])
        reference = np.array([[15, 20, 25], [35, 60, 80]])
        scaler = StandardScaler().fit(reference)
        z = scaler.transform(data)[0]
        score = 100 - min(max((sum(z) * 10 + 50), 0), 100)

        row = {
            "Ticker": ticker,
            "Z-Score Risk": round(score),
            "Volatility": round(volatility, 2),
            "Drawdown": round(drawdown, 2),
        }

        for feat in extra_features:
            row[feat] = info.get(feat, np.nan)

        row["Date"] = pd.Timestamp.today().strftime("%Y-%m-%d")
        return row

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None

# Load existing CSV if available
existing_df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
existing_tickers = set(existing_df["Ticker"].unique()) if not existing_df.empty else set()

# Batch pull
tickers = get_sp500_tickers()
new_rows = []

for i, ticker in enumerate(tickers):
    if ticker in existing_tickers:
        continue

    result = compute_features(ticker)
    if result:
        new_rows.append(result)
        print(f"Added: {ticker}")

    time.sleep(3)  # throttle to avoid rate limits

# Append new data
if new_rows:
    update_df = pd.DataFrame(new_rows)
    final_df = pd.concat([existing_df, update_df], ignore_index=True)
    final_df.to_csv(csv_path, index=False)
    print(f"✅ CSV updated with {len(new_rows)} new rows.")
else:
    print("No new data added. All tickers may be up to date.")

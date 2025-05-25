import yfinance as yf
import pandas as pd
import numpy as np
import time
import os
from sklearn.preprocessing import StandardScaler
from datetime import datetime

# Output CSV path
csv_path = "sp500_risk_scores.csv"
LOG_PATH = "sp500_builder_log.txt"

# Features to extract
extra_features = [
    'beta', 'dividendYield', 'revenueGrowth', 'priceToBook',
    'returnOnAssets', 'returnOnEquity', 'marketCap', 'shortRatio'
]

# Fetch S&P 500 ticker list
def get_sp500_tickers():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    return table['Symbol'].tolist()

# Safely compute stock metrics
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

        # Normalize Z-Score Risk
        data = np.array([[volatility, abs(drawdown), pe_ratio]])
        reference = np.array([[15, 20, 25], [35, 60, 80]])
        scaler = StandardScaler().fit(reference)
        z = scaler.transform(data)[0]
        z_score_risk = 100 - min(max((sum(z) * 10 + 50), 0), 100)

        # Value-at-Risk (VaR 95%)
        var_95 = np.percentile(hist['Return'].dropna(), 5) * 100  # in %
        var_risk = 100 + var_95  # since VaR is negative, higher (less negative) is safer
        var_risk = min(max(var_risk, 0), 100)

        # Factor-Based Score (manual weights)
        weights = {
            'beta': 0.3,
            'priceToBook': 0.2,
            'returnOnAssets': -0.2,
            'debtToEquity': 0.3
        }
        factor_score = 0
        for key, weight in weights.items():
            val = info.get(key, np.nan)
            if pd.notna(val):
                factor_score += weight * val
        factor_score = 100 - min(max(factor_score, 0), 100)

        row = {
            "Ticker": ticker,
            "Z-Score Risk": round(z_score_risk),
            "Volatility": round(volatility, 2),
            "Drawdown": round(drawdown, 2),
            "VaR Risk": round(var_risk, 2),
            "Factor-Based": round(factor_score, 2),
            "Date": datetime.today().strftime("%Y-%m-%d")
        }

        for feat in extra_features:
            row[feat] = info.get(feat, np.nan)

        return row

    except Exception as e:
        with open(LOG_PATH, 'a') as f:
            f.write(f"{datetime.now()} - {ticker}: {e}\n")
        return None

# Load existing data
existing_df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
existing_tickers = set(existing_df["Ticker"].unique()) if not existing_df.empty else set()

# Fetch fresh list of tickers
tickers = get_sp500_tickers()

# Time-budgeted pull (~2 hours max)
MAX_BATCHES = 100
DELAY = 60  # seconds
new_rows = []

for i, ticker in enumerate(tickers):
    if ticker in existing_tickers:
        continue

    print(f"Fetching {ticker} ({i+1}/{len(tickers)})...")
    row = compute_features(ticker)
    if row:
        new_rows.append(row)
        print(f"✔️ {ticker} added")
    else:
        print(f"⚠️ Skipped {ticker}")

    # Save periodically every 10 rows
    if len(new_rows) > 0 and len(new_rows) % 10 == 0:
        temp_df = pd.DataFrame(new_rows)
        existing_df = pd.concat([existing_df, temp_df], ignore_index=True)
        existing_df.to_csv(csv_path, index=False)
        new_rows.clear()
        print("💾 Partial save complete.")

    time.sleep(DELAY)
    if i >= MAX_BATCHES:
        print("⏸️ Max batch limit reached. Stopping.")
        break

# Final save
if new_rows:
    final_df = pd.concat([existing_df, pd.DataFrame(new_rows)], ignore_index=True)
    final_df.to_csv(csv_path, index=False)
    print("✅ Final CSV update complete.")
else:
    print("No new data added. All current tickers may be up to date.")

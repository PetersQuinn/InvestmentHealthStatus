import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import os
from sklearn.preprocessing import StandardScaler

st.title("📘 S&P 500 Risk Score Listings (Optimized)")

@st.cache_data
def get_sp500_tickers():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    return table['Symbol'].tolist(), table

@st.cache_data(ttl=86400)
def compute_risk_score(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist is None or hist.empty:
            return np.nan, np.nan, np.nan

        hist['Return'] = hist['Close'].pct_change()
        volatility = np.std(hist['Return']) * 100
        cumulative = (1 + hist['Return'].fillna(0)).cumprod()
        drawdown = (cumulative / cumulative.cummax() - 1).min() * 100

        pe_ratio = 25.0  # Default placeholder
        data = np.array([[volatility, abs(drawdown), pe_ratio]])
        reference = np.array([[15, 20, 25], [35, 60, 80]])
        scaler = StandardScaler().fit(reference)
        z = scaler.transform(data)[0]
        score = 100 - min(max((sum(z) * 10 + 50), 0), 100)

        return float(round(score)), float(round(volatility, 2)), float(round(drawdown, 2))
    except:
        return np.nan, np.nan, np.nan

csv_path = "sp500_risk_scores.csv"

if os.path.exists(csv_path) and not st.button("🔄 Refresh SP500 Data"):
    df = pd.read_csv(csv_path)
    st.success("Loaded S&P 500 risk scores from cached CSV.")
else:
    tickers, sp500 = get_sp500_tickers()
    progress = st.progress(0)
    results = []

    for i, t in enumerate(tickers):
        z_score, vol, dd = compute_risk_score(t)
        results.append([t, z_score, vol, dd, np.nan, np.nan, np.nan])
        if i % 10 == 0:
            progress.progress(i / len(tickers))
        time.sleep(0.2)

    df = pd.DataFrame(results, columns=[
        "Ticker", "Z-Score Risk", "Volatility", "Drawdown",
        "VaR Risk", "Factor-Based", "ML Score"
    ])
    df.to_csv(csv_path, index=False)
    st.success("Fetched and saved fresh S&P 500 data.")

# Ensure Z-Score Risk is numeric
df["Z-Score Risk"] = pd.to_numeric(df["Z-Score Risk"], errors="coerce")

# Display with built-in formatting for sorting + N/A display
st.dataframe(
    df.reset_index(drop=True),
    column_config={
        "Z-Score Risk": st.column_config.NumberColumn(
            "Z-Score Risk",
            format="%d",
            help="Normalized risk score where higher = less risky"
        )
    }
)

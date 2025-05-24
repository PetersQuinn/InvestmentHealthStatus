import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
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
        if hist.empty:
            return "N/A", "N/A"

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

        return round(score), round(volatility, 2), round(drawdown, 2)
    except:
        return "N/A", "N/A", "N/A"

tickers, sp500 = get_sp500_tickers()
progress = st.progress(0)
results = []

for i, t in enumerate(tickers):
    z_score, vol, dd = compute_risk_score(t)
    results.append([t, z_score, vol, dd, "N/A", "N/A", "N/A"])
    if i % 10 == 0:
        progress.progress(i / len(tickers))
    time.sleep(0.2)

df = pd.DataFrame(results, columns=[
    "Ticker", "Z-Score Risk", "Volatility", "Drawdown",
    "VaR Risk", "Factor-Based", "ML Score"
])

sort_by = st.selectbox("Sort stocks by:", df.columns)
ascending = st.radio("Sort order:", ["Ascending", "Descending"]) == "Ascending"
df_sorted = df.sort_values(by=sort_by, ascending=ascending)

st.dataframe(df_sorted.reset_index(drop=True))

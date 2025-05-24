import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.title("📘 S&P 500 Risk Score Listings")

@st.cache_data
def get_sp500_tickers():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    return table['Symbol'].tolist(), table

def compute_risk_score(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        info = stock.info if stock.info else stock.fast_info
        hist['Return'] = hist['Close'].pct_change()
        volatility = np.std(hist['Return']) * 100
        cumulative = (1 + hist['Return'].fillna(0)).cumprod()
        drawdown = (cumulative / cumulative.cummax() - 1).min() * 100
        pe_ratio = info.get('trailingPE', np.nan)
        if np.isnan(pe_ratio): pe_ratio = 25.0
        data = np.array([[volatility, abs(drawdown), pe_ratio]])
        reference = np.array([[15, 20, 25], [35, 60, 80]])
        scaler = StandardScaler().fit(reference)
        z = scaler.transform(data)[0]
        score = 100 - min(max((sum(z) * 10 + 50), 0), 100)
        return round(score)
    except:
        return "N/A"

tickers, sp500 = get_sp500_tickers()
progress = st.progress(0)
results = []

for i, t in enumerate(tickers):
    score = compute_risk_score(t)
    results.append([t, score, "N/A", "N/A", "N/A"])  # Placeholders for other scores
    if i % 10 == 0:
        progress.progress(i / len(tickers))

df = pd.DataFrame(results, columns=["Ticker", "Z-Score Risk", "VaR Risk", "Factor-Based", "ML Score"])
st.dataframe(df)

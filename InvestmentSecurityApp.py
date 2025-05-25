import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# ---------------------------
# Utility functions
# ---------------------------
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y", interval="1d")

        info = getattr(stock, 'info', {})
        if not isinstance(info, dict) or 'trailingPE' not in info:
            info = getattr(stock, 'fast_info', {})

        return hist, info
    except:
        return None, None

def calculate_metrics(hist, info):
    # Calculate volatility (std dev of daily returns)
    hist['Return'] = hist['Close'].pct_change()
    volatility = np.std(hist['Return']) * 100

    # Max drawdown
    cumulative = (1 + hist['Return'].fillna(0)).cumprod()
    max_drawdown = (cumulative / cumulative.cummax() - 1).min() * 100

    # PE Ratio (or use fallback if not available)
    pe_ratio = info.get('trailingPE', np.nan)

    return {
        'volatility': round(volatility, 2),
        'max_drawdown': round(max_drawdown, 2),
        'pe_ratio': pe_ratio,
    }

def compute_normalized_risk_score(volatility, drawdown, pe_ratio):
    # Replace NaN PE with median-like value for normalization
    if np.isnan(pe_ratio):
        pe_ratio = 25.0

    data = np.array([[volatility, abs(drawdown), pe_ratio]])
    reference_data = np.array([
        [15, 20, 25],  # Reference lower-risk example
        [35, 60, 80]   # Reference higher-risk example
    ])

    scaler = StandardScaler()
    scaler.fit(reference_data)
    normalized = scaler.transform(data)[0]

    z_score_total = normalized[0] + normalized[1] + normalized[2]  # Higher means riskier
    normalized_risk_score = 100 - min(max((z_score_total * 10 + 50), 0), 100)

    return round(normalized_risk_score)

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="Should I Invest?", layout="centered")
st.title("📈 Should I Invest? Dashboard")

# Input
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA)", value="AAPL").upper()

if ticker.strip() == "":
    st.stop()  # Prevents running with an empty or invalid ticker

# Data & Metrics
hist, info = get_stock_data(ticker)
st.write("📦 Raw History:", hist)
st.write("ℹ️ Raw Info:", info)

if hist is not None and not hist.empty and info is not None:
    metrics = calculate_metrics(hist, info)
    risk_score = compute_normalized_risk_score(
        metrics['volatility'], metrics['max_drawdown'], metrics['pe_ratio']
    )

    st.subheader(f"Results for {ticker}")
    st.metric("📉 Annualized Volatility (1Y)", f"{metrics['volatility']}%")
    st.metric("🔻 Max Drawdown (1Y)", f"{metrics['max_drawdown']}%")
    st.metric("💰 P/E Ratio", f"{metrics['pe_ratio'] if not np.isnan(metrics['pe_ratio']) else 'N/A'}")
    st.metric("✅ Normalized Risk Score (Lower is Riskier)", f"{risk_score} / 100")

    st.line_chart(hist['Close'], use_container_width=True)

else:
    st.warning("Couldn't retrieve data for the given ticker. Please check the symbol or try again later.")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ---------------------------
# Utility functions
# ---------------------------
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        info = stock.info
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

    # Score (simple weighted score)
    score = 100
    score -= min(volatility, 30) * 1.5
    score += 10 if pe_ratio and pe_ratio < 30 else 0
    score += 5 if max_drawdown > -10 else 0
    score = max(0, min(100, round(score)))

    return {
        'volatility': round(volatility, 2),
        'max_drawdown': round(max_drawdown, 2),
        'pe_ratio': pe_ratio,
        'score': score
    }

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="Should I Invest?", layout="centered")
st.title("📈 Should I Invest? Dashboard")

# Input
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA)", value="AAPL").upper()

# Data & Metrics
hist, info = get_stock_data(ticker)
if hist is not None and not hist.empty:
    metrics = calculate_metrics(hist, info)

    st.subheader(f"Results for {ticker}")
    st.metric("📉 Volatility (1Y Std Dev)", f"{metrics['volatility']}%")
    st.metric("🔻 Max Drawdown (1Y)", f"{metrics['max_drawdown']}%")
    st.metric("💰 P/E Ratio", f"{metrics['pe_ratio'] if not np.isnan(metrics['pe_ratio']) else 'N/A'}")
    st.metric("✅ Risk Score", f"{metrics['score']} / 100")

    st.line_chart(hist['Close'], use_container_width=True)

else:
    st.warning("Couldn't retrieve data for the given ticker. Please check the symbol.")

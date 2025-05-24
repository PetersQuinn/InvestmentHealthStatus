import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.title("📊 Compare Up to 4 Stocks")

tickers = st.text_input("Enter up to 4 stock tickers separated by commas (e.g., AAPL, TSLA, MSFT, GOOGL)").upper().split(',')

def get_metrics(ticker):
    try:
        stock = yf.Ticker(ticker.strip())
        hist = stock.history(period="1y")
        info = stock.info if stock.info else stock.fast_info
        hist['Return'] = hist['Close'].pct_change()
        volatility = np.std(hist['Return']) * 100
        cumulative = (1 + hist['Return'].fillna(0)).cumprod()
        max_drawdown = (cumulative / cumulative.cummax() - 1).min() * 100
        pe_ratio = info.get('trailingPE', np.nan)
        # Risk Score (same normalized method)
        if np.isnan(pe_ratio): pe_ratio = 25.0
        data = np.array([[volatility, abs(max_drawdown), pe_ratio]])
        reference = np.array([[15, 20, 25], [35, 60, 80]])
        scaler = StandardScaler().fit(reference)
        z = scaler.transform(data)[0]
        score = 100 - min(max((sum(z) * 10 + 50), 0), 100)
        return [ticker.strip(), round(volatility, 2), round(max_drawdown, 2), pe_ratio, round(score)]
    except:
        return [ticker.strip(), 'N/A', 'N/A', 'N/A', 'N/A']

if tickers and tickers[0] != '':
    data = [get_metrics(t) for t in tickers[:4]]
    df = pd.DataFrame(data, columns=["Ticker", "Volatility", "Drawdown", "P/E", "Risk Score" ])
    st.dataframe(df)

from pathlib import Path

# Directory structure
base_path = Path("InvestmentHealthStatus")
pages_path = base_path / "pages"
pages_path.mkdir(parents=True, exist_ok=True)

# Content for About page
about_content = """import streamlit as st

st.title("ℹ️ About This App")

st.markdown(\"\"\"
Welcome to the **Should I Invest? Dashboard** — built by Quinn Peters.

This tool was created as a fast, interactive way to explore stock risk levels 
using real market data and transparent logic. As someone pursuing Risk, Data, and Financial Engineering,
I wanted to showcase how quantitative reasoning and rapid prototyping can work hand-in-hand in FinTech.

This app is not investment advice, but a demonstration of data-driven insights.

Feel free to explore, compare, and question.
\"\"\")
"""

# Content for Methodology page
methodology_content = """import streamlit as st

st.title("📚 Methodology")

st.markdown(\"\"\"
### 🔹 Current Risk Score Implemented:
**1. Normalized Risk Score (Z-Score-Based)**  
- Inputs: Annualized Volatility, Max Drawdown, P/E Ratio  
- Process: Each metric is normalized using z-scores compared to a synthetic benchmark range.  
- Output: A risk score out of 100 (higher = less risky)

---

### 🔸 Additional Scores (Coming Soon):

**2. Value-at-Risk (VaR)-Based Score**  
- Uses historical return distributions to estimate the worst-case loss over a period with 95% or 99% confidence.  
- *Status:* Under Development

**3. Factor-Based Composite Risk Score**  
- Combines multiple financial metrics and market sensitivities (e.g., beta, debt ratio, earnings stability).  
- *Status:* Under Development

**4. ML-Driven Risk Classification Score**  
- Learns patterns from labeled stock performance data and produces a data-driven risk score.  
- *Status:* Under Development
\"\"\")
"""

# Content for CompareStocks page
compare_content = """import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.title("📊 Compare Up to 4 Stocks")

tickers = st.text_input("Enter up to 4 stock tickers separated by commas (e.g., AAPL, TSLA, MSFT, GOOGL)").upper().split(',')

def get_metrics(ticker):
    try:
        stock = yf.Ticker(ticker.strip())
        hist = stock.history(period=\"1y\")
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
    df = pd.DataFrame(data, columns=[\"Ticker\", \"Volatility\", \"Drawdown\", \"P/E\", \"Risk Score\" ])
    st.dataframe(df)
"""

# Content for S&P 500 Listings Page (with cautionary note)
sp500_content = """import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.title(\"📘 S&P 500 Risk Score Listings\")

@st.cache_data
def get_sp500_tickers():
    table = pd.read_html(\"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies\")[0]
    return table['Symbol'].tolist(), table

def compute_risk_score(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=\"1y\")
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
        return \"N/A\"

tickers, sp500 = get_sp500_tickers()
progress = st.progress(0)
results = []

for i, t in enumerate(tickers):
    score = compute_risk_score(t)
    results.append([t, score, \"N/A\", \"N/A\", \"N/A\"])  # Placeholders for other scores
    if i % 10 == 0:
        progress.progress(i / len(tickers))

df = pd.DataFrame(results, columns=[\"Ticker\", \"Z-Score Risk\", \"VaR Risk\", \"Factor-Based\", \"ML Score\"])
st.dataframe(df)
"""

# Create files
(pages_path / "About.py").write_text(about_content, encoding="utf-8")
(pages_path / "Methodology.py").write_text(methodology_content, encoding="utf-8")
(pages_path / "CompareStocks.py").write_text(compare_content, encoding="utf-8")
(pages_path / "SP500_Listings.py").write_text(sp500_content, encoding="utf-8")

"Pages generated: About, Methodology, CompareStocks, SP500_Listings"

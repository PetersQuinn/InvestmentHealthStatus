import streamlit as st

st.title("📚 Methodology")

st.markdown("""
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
""")

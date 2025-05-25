import yfinance as yf

ticker = "AAPL"
stock = yf.Ticker(ticker)

print("=== HISTORY ===")
print(stock.history(period="1y", interval="1d"))

print("=== INFO ===")
print(stock.info)


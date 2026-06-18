import streamlit as st
import yfinance as yf
import pandas as pd

# -----------------------------
# RSI CALCULATION
# -----------------------------
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -----------------------------
# DAILY TIMEFRAME ANALYSIS
# -----------------------------
def analyze_daily(symbol, period):
    df = yf.download(
        symbol,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    if df is None or df.empty:
        return {"error": "No daily data found. Check symbol."}

    if len(df) < 30:
        return {"error": "Not enough daily candles to calculate RSI."}

    close = df["Close"]
    df["RSI"] = calculate_rsi(close, 14)
    df["RSI_MA20"] = df["RSI"].rolling(20).mean()

    latest = df.iloc[-1]

    rsi = latest["RSI"]
    rsi_ma = latest["RSI_MA20"]

    if pd.isna(rsi) or pd.isna(rsi_ma):
        return {"error": "RSI values not ready yet. Try a larger period."}

    call = (rsi > rsi_ma) and (rsi > 50)
    put = (rsi < rsi_ma) and (rsi < 50)

    return {
        "RSI": float(rsi),
        "RSI_MA20": float(rsi_ma),
        "CALL": call,
        "PUT": put,
        "data": df
    }

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Trading Signal App", layout="wide")

st.title("📈 Daily Trading Signal Analyzer")
st.write("Stable RSI + MA20 analysis using **daily candles** (works 24/7).")

symbol = st.text_input("Enter Stock Symbol (NSE):", value="RELIANCE.NS")
period = st.selectbox("Data Period:", ["1mo", "3mo", "6mo", "1y", "2y"])

st.caption("Examples: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ^NSEI")

if st.button("Run Analysis", use_container_width=True):
    st.subheader(f"Analyzing {symbol} (Daily)")

    result = analyze_daily(symbol, period)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.metric("RSI (Daily)", f"{result['RSI']:.2f}")
    st.metric("RSI MA20 (Daily)", f"{result['RSI_MA20']:.2f}")

    st.subheader("📌 Final Signal (Daily)")

    if result["CALL"]:
        st.success("🟢 CALL BUY SIGNAL (Daily)")
    elif result["PUT"]:
        st.error("🔴 PUT BUY SIGNAL (Daily)")
    else:
        st.warning("🟡 NO TRADE (Daily)")

    st.subheader("📊 RSI Trend (Daily)")
    st.line_chart(result["data"][["RSI", "RSI_MA20"]])

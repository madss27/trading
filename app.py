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
# SAFE FLOAT
# -----------------------------
def safe_float(x):
    try:
        return float(x)
    except:
        return None

# -----------------------------
# TRY MULTIPLE INTERVALS
# -----------------------------
def get_valid_timeframe(symbol, period):
    intervals = ["5m", "15m", "30m", "60m", "1d"]

    for interval in intervals:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False
        )

        if df is None or df.empty:
            continue

        if len(df) < 20:
            continue

        close = df["Close"]
        df["RSI"] = calculate_rsi(close, 14)
        df["RSI_MA20"] = df["RSI"].rolling(20).mean()

        latest = df.iloc[-1]

        rsi = safe_float(latest["RSI"])
        rsi_ma = safe_float(latest["RSI_MA20"])

        if rsi is None or rsi_ma is None:
            continue

        return interval, rsi, rsi_ma, df

    return None, None, None, None

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Trading Signal App", layout="wide")

st.title("📈 Trading Signal Analyzer")
st.write("Live RSI + MA20 analysis for Indian stocks (NSE).")

symbol = st.text_input("Enter Stock Symbol (NSE):", value="RELIANCE.NS")
period = st.selectbox("Data Period:", ["5d", "1mo", "3mo", "6mo", "1y"])

if st.button("Run Analysis", use_container_width=True):
    st.subheader(f"Analyzing {symbol}")

    interval, rsi, rsi_ma, df = get_valid_timeframe(symbol, period)

    if interval is None:
        st.error("No usable data found for ANY timeframe. Try another stock.")
        st.stop()

    st.success(f"Using timeframe: {interval}")

    st.metric("RSI", f"{rsi:.2f}")
    st.metric("RSI MA20", f"{rsi_ma:.2f}")

    if rsi > rsi_ma and rsi > 50:
        st.success("🟢 CALL BUY SIGNAL")
    elif rsi < rsi_ma and rsi < 50:
        st.error("🔴 PUT BUY SIGNAL")
    else:
        st.warning("🟡 NO TRADE")

    st.subheader("📊 RSI Trend")
    st.line_chart(df[["RSI", "RSI_MA20"]])

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
# TIMEFRAME ANALYSIS
# -----------------------------
def timeframe_analysis(symbol, period, interval):
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        return None

    close = df["Close"]
    df["RSI"] = calculate_rsi(close, 14)
    df["RSI_MA20"] = df["RSI"].rolling(20).mean()

    latest = df.iloc[-1]
    rsi = float(latest["RSI"])
    rsi_ma = float(latest["RSI_MA20"])

    call = (rsi > rsi_ma) and (rsi > 50)
    put = (rsi < rsi_ma) and (rsi < 50)

    return {
        "RSI": rsi,
        "RSI_MA20": rsi_ma,
        "CALL": call,
        "PUT": put,
        "data": df
    }


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Trading Signal App", layout="wide")

st.title("📈 Trading Signal Analyzer")
st.write("Live RSI + MA20 analysis for Indian stocks (NSE).")

# User input
symbol = st.text_input("Enter Stock Symbol (NSE):", value="RELIANCE.NS")
period = st.selectbox("Data Period:", ["5d", "1mo", "3mo", "6mo", "1y"])

st.caption("Examples: RELIANCE.NS, TCS.NS, HDFCBANK.NS, ^NSEI")

if st.button("Run Analysis", use_container_width=True):
    st.subheader(f"Analyzing {symbol}")

    tf5 = timeframe_analysis(symbol, period, "5m")
    tf15 = timeframe_analysis(symbol, period, "15m")

    if tf5 is None or tf15 is None:
        st.error("No data found. Check symbol or market hours.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.header("🕔 5-Minute")
            st.metric("RSI", f"{tf5['RSI']:.2f}")
            st.metric("RSI MA20", f"{tf5['RSI_MA20']:.2f}")

        with col2:
            st.header("🕒 15-Minute")
            st.metric("RSI", f"{tf15['RSI']:.2f}")
            st.metric("RSI MA20", f"{tf15['RSI_MA20']:.2f}")

        # Final Decision
        st.subheader("📌 Final Signal")

        if tf5["CALL"] and tf15["CALL"]:
            st.success("🟢 CALL BUY SIGNAL")
        elif tf5["PUT"] and tf15["PUT"]:
            st.error("🔴 PUT BUY SIGNAL")
        else:
            st.warning("🟡 NO TRADE")

        # Chart
        st.subheader("📊 RSI Trend")
        st.line_chart(tf15["data"][["RSI", "RSI_MA20"]])

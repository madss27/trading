import streamlit as st
import yfinance as yf
import pandas as pd

# -----------------------------
# SAFE FLOAT (prevents crashes)
# -----------------------------
def safe_float(x):
    try:
        return float(x)
    except:
        return None

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
# FLEXIBLE DAILY ANALYSIS
# -----------------------------
def analyze_daily(symbol):
    df = yf.download(
        symbol,
        period="6mo",          # Always enough data
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        return {"RSI": None, "RSI_MA20": None, "CALL": False, "PUT": False, "data": None}

    # Fix duplicate timestamps (common NSE bug)
    df = df[~df.index.duplicated(keep="last")]

    # Calculate indicators
    df["RSI"] = calculate_rsi(df["Close"], 14)
    df["RSI_MA20"] = df["RSI"].rolling(20).mean()

    latest = df.iloc[-1]

    # Convert safely
    rsi = safe_float(latest["RSI"])
    rsi_ma = safe_float(latest["RSI_MA20"])

    # If RSI is missing → still return NO TRADE instead of error
    if rsi is None or rsi_ma is None:
        return {"RSI": None, "RSI_MA20": None, "CALL": False, "PUT": False, "data": df}

    # Signal logic
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
st.set_page_config(page_title="Daily Trading Signal", layout="wide")

st.title("📈 Daily Trading Signal Analyzer")
st.write("Flexible RSI + MA20 signals using **daily candles** (never crashes).")

symbol = st.text_input("Enter Stock Symbol (NSE):", value="RELIANCE.NS")

if st.button("Run Analysis", use_container_width=True):
    st.subheader(f"Analyzing {symbol} (Daily)")

    result = analyze_daily(symbol)

    # If RSI missing → show NO TRADE but DO NOT ERROR
    if result["RSI"] is None:
        st.warning("RSI not available. Showing NO TRADE.")
    else:
        st.metric("RSI (Daily)", f"{result['RSI']:.2f}")
        st.metric("RSI MA20 (Daily)", f"{result['RSI_MA20']:.2f}")

    st.subheader("📌 Final Signal (Daily)")

    if result["CALL"]:
        st.success("🟢 CALL BUY SIGNAL")
    elif result["PUT"]:
        st.error("🔴 PUT BUY SIGNAL")
    else:
        st.warning("🟡 NO TRADE")

    # Show chart only if data exists
    if result["data"] is not None:
        st.subheader("📊 RSI Trend (Daily)")
        st.line_chart(result["data"][["RSI", "RSI_MA20"]])

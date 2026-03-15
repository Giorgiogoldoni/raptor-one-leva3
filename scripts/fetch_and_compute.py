import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# 1. FETCH DATA
# ============================================================

def fetch_data(ticker):
    df = yf.download(ticker, period="2y", interval="1d")
    df = df.rename(columns={"Close": "Close"})
    df = df.dropna()
    return df


# ============================================================
# 2. COMPUTE INDICATORS (VERSIONE CORRETTA)
# ============================================================

def compute_indicators(df):
    # Calcolo MMA20
    df["MMA20"] = df["Close"].rolling(window=20).mean()

    # Calcolo MOMENTUM 12M, 6M, 3M
    df["MOM_12M"] = df["Close"].pct_change(252)
    df["MOM_6M"] = df["Close"].pct_change(126)
    df["MOM_3M"] = df["Close"].pct_change(63)

    # Composite momentum
    df["MOM_COMPOSITE"] = (
        df["MOM_12M"] * 0.5 +
        df["MOM_6M"] * 0.3 +
        df["MOM_3M"] * 0.2
    )

    # 🔥 PULIZIA DATI: allineamento perfetto
    df = df.dropna(subset=["Close", "MOM_COMPOSITE", "MMA20"]).copy()

    close = df["Close"]

    # Segnali BUY/SELL
    df["BUY_SIGNAL"] = ((df["MOM_COMPOSITE"] > 0) & (close > df["MMA20"])).astype(int)
    df["SELL_SIGNAL"] = ((df["MOM_COMPOSITE"] < 0) & (close < df["MMA20"])).astype(int)

    return df


# ============================================================
# 3. SAVE DATA + CHART
# ============================================================

def save_outputs(df, ticker):
    os.makedirs("data", exist_ok=True)
    os.makedirs("charts", exist_ok=True)

    df.to_csv(f"data/{ticker}.csv")

    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Close"], label="Close")
    plt.plot(df.index, df["MMA20"], label="MMA20")
    plt.title(f"{ticker} Price + MMA20")
    plt.legend()
    plt.savefig(f"charts/{ticker}.png")
    plt.close()


# ============================================================
# 4. MAIN
# ============================================================

def main():
    ticker = "SPY"   # puoi cambiarlo
    df = fetch_data(ticker)
    df = compute_indicators(df)
    save_outputs(df, ticker)


if __name__ == "__main__":
    main()

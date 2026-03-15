import os
import datetime as dt

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TICKERS = [
    "QQQ3.MI", "3USL.MI", "3EUL.MI", "3ITL.MI", "3DEL.MI",
    "3EML.MI", "3GOL.MI", "3SIL.MI", "3NGL.MI", "3BRS.MI",
    "3TSL.MI", "3NVD.MI", "3PLT.MI", "3CON.MI", "3AMD.MI",
    "3GOO.MI", "3AMZ.MI", "3MSF.MI", "3FB.MI", "3LNV.MI",
]

DATA_DIR = "data"
CHARTS_DIR = "charts"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"]

    df["ROC_2"] = close.pct_change(2)
    df["ROC_4"] = close.pct_change(4)
    df["ROC_8"] = close.pct_change(8)

    df["MOM_COMPOSITE"] = (df["ROC_2"] + df["ROC_4"] + df["ROC_8"]) / 3

    df["MA20"] = close.rolling(20).mean()
    df["MA50"] = close.rolling(50).mean()

    high = df["High"]
    low = df["Low"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    df["SIGNAL"] = np.where(
        (df["MOM_COMPOSITE"] > 0) & (close > df["MA20"]),
        "BUY",
        "FLAT"
    )

    return df

def plot_chart(df: pd.DataFrame, ticker: str):
    if df.empty:
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Close"], label="Close", color="white")
    plt.plot(df.index, df["MA20"], label="MA20", color="orange", linewidth=1)
    plt.plot(df.index, df["MA50"], label="MA50", color="cyan", linewidth=1)

    buy_mask = df["SIGNAL"] == "BUY"
    plt.scatter(df.index[buy_mask], df["Close"][buy_mask],
                label="BUY", color="lime", s=10)

    plt.title(f"{ticker} – Price & Signals")
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    out_path = os.path.join(CHARTS_DIR, f"{ticker}_chart.png")
    plt.savefig(out_path, dpi=120, facecolor="black")
    plt.close()

def main():
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(days=120)

    all_summary = []

    for ticker in TICKERS:
        print(f"Processing {ticker}...")
        data = yf.download(ticker, start=start, end=end, interval="60m")

        if data.empty:
            print(f"No data for {ticker}, skipping.")
            continue

        data = compute_indicators(data)

        csv_path = os.path.join(DATA_DIR, f"{ticker}.csv")
        data.to_csv(csv_path)

        last = data.iloc[-1]
        all_summary.append({
            "Ticker": ticker,
            "Close": last["Close"],
            "MOM_COMPOSITE": last["MOM_COMPOSITE"],
            "MA20": last["MA20"],
            "MA50": last["MA50"],
            "ATR14": last["ATR14"],
            "SIGNAL": last["SIGNAL"],
        })

        plot_chart(data, ticker)

    if all_summary:
        df_sum = pd.DataFrame(all_summary)
        df_sum.sort_values("MOM_COMPOSITE", ascending=False, inplace=True)
        df_sum.to_csv(os.path.join(DATA_DIR, "summary_signals.csv"), index=False)

if __name__ == "__main__":
    main()

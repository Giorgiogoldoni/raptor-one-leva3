import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# 0. LISTA TICKER MULTI-ASSET
# ============================================================

tickers = [
    "LQQ", "CL2", "LBUL", "QQQ3", "3GOL", "3SIL", "3TSL", "3USL", "3BAL",
    "QQQS", "3NVD", "3NGL", "3USS", "3ITL", "3PLT", "3EUL", "3LNV", "3DEL",
    "3CON", "3NGS", "SOIL", "3DES", "3EML", "3MST", "3MSF", "3AMD", "3FB",
    "3GOO", "3EUS", "3LMI", "3EDF", "3LCO", "3BRS", "3AMZ", "3STS", "3BAB",
    "3LCR", "3RAC", "3SCR", "3SNV", "3LFB", "3LAA", "3CRE", "3MRN", "3AAP",
    "SNV3", "3SMI", "3EDS", "3EMS", "3UBR", "XOM3", "AVG3", "3DIE", "3SFB",
    "SBA3", "3SAA"
]


# ============================================================
# 1. FETCH DATA
# ============================================================

def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="2y", interval="1d")
    except Exception as e:
        print(f"[{ticker}] ERRORE download: {e}")
        return pd.DataFrame()

    if df is None or df.empty:
        print(f"[{ticker}] Nessun dato scaricato.")
        return pd.DataFrame()

    return df.dropna()


# ============================================================
# 2. COMPUTE INDICATORS (ROBUST VERSION)
# ============================================================

def compute_indicators(df, ticker):
    if df.empty:
        print(f"[{ticker}] DataFrame vuoto, salto indicatori.")
        return df

    try:
        df["MMA20"] = df["Close"].rolling(window=20).mean()
        df["MOM_12M"] = df["Close"].pct_change(252)
        df["MOM_6M"] = df["Close"].pct_change(126)
        df["MOM_3M"] = df["Close"].pct_change(63)

        df["MOM_COMPOSITE"] = (
            df["MOM_12M"] * 0.5 +
            df["MOM_6M"] * 0.3 +
            df["MOM_3M"] * 0.2
        )

        df = df.dropna(subset=["Close", "MMA20", "MOM_COMPOSITE"]).copy()

        close = df["Close"]
        df["BUY_SIGNAL"] = ((df["MOM_COMPOSITE"] > 0) & (close > df["MMA20"])).astype(int)
        df["SELL_SIGNAL"] = ((df["MOM_COMPOSITE"] < 0) & (close < df["MMA20"])).astype(int)

    except Exception as e:
        print(f"[{ticker}] ERRORE indicatori: {e}")
        return pd.DataFrame()

    return df


# ============================================================
# 3. SAVE DATA + CHART
# ============================================================

def save_outputs(df, ticker):
    os.makedirs("data", exist_ok=True)
    os.makedirs("charts", exist_ok=True)

    if df.empty:
        print(f"[{ticker}] Nessun dato da salvare, creo placeholder.")

        pd.DataFrame().to_csv(f"data/{ticker}.csv")

        plt.figure(figsize=(10,4))
        plt.text(0.5, 0.5, f"{ticker}\nNO DATA", ha="center", va="center", fontsize=20)
        plt.axis("off")
        plt.savefig(f"charts/{ticker}.png")
        plt.close()
        return

    df.to_csv(f"data/{ticker}.csv")

    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["Close"], label="Close")
    plt.plot(df.index, df["MMA20"], label="MMA20")
    plt.title(f"{ticker} Price + MMA20")
    plt.legend()
    plt.savefig(f"charts/{ticker}.png")
    plt.close()


# ============================================================
# 4. MAIN LOOP MULTI-TICKER
# ============================================================

def main():
    for ticker in tickers:
        print(f"\n=== PROCESSING {ticker} ===")
        df = fetch_data(ticker)
        df = compute_indicators(df, ticker)
        save_outputs(df, ticker)


if __name__ == "__main__":
    main()

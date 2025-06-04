import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Constants
RSI_PERIOD = 25

# --- Helper function for Wilder\s RSI ---
def calculate_rsi_wilder(prices, period=RSI_PERIOD):
    """Calculate RSI using Wilder\s smoothing method."""
    delta = prices.diff()
    delta = delta[1:]
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Check if enough data for initial SMA
    if len(gain) < period:
        return pd.Series(dtype=float) # Return empty series if not enough data
        
    avg_gain = gain.rolling(window=period, min_periods=period).mean()[:period]
    avg_loss = loss.rolling(window=period, min_periods=period).mean()[:period]
    
    # Check if initial averages are valid
    if avg_gain.isnull().all() or avg_loss.isnull().all():
         return pd.Series(dtype=float) # Return empty series if initial calc failed

    # Initialize numpy arrays for subsequent calculations
    np_avg_gain = np.array(avg_gain)
    np_avg_loss = np.array(avg_loss)

    for i in range(period, len(gain)):
        current_gain = gain.iloc[i]
        current_loss = loss.iloc[i]
        
        # Ensure previous average is valid before calculation
        if not np.isnan(np_avg_gain[-1]):
             next_avg_gain = (np_avg_gain[-1] * (period - 1) + current_gain) / period
        else:
             next_avg_gain = np.nan # Propagate NaN if previous avg is NaN
             
        if not np.isnan(np_avg_loss[-1]) and np_avg_loss[-1] != 0:
            next_avg_loss = (np_avg_loss[-1] * (period - 1) + current_loss) / period
        elif np_avg_loss[-1] == 0:
             # If previous avg loss was 0, recalculate using SMA for stability
             window_loss = loss.iloc[i-period+1:i+1]
             next_avg_loss = window_loss.mean() if len(window_loss) == period else np.nan
        else:
            next_avg_loss = np.nan # Propagate NaN

        np_avg_gain = np.append(np_avg_gain, next_avg_gain)
        np_avg_loss = np.append(np_avg_loss, next_avg_loss)
        
    # Handle division by zero for avg_loss
    rs = np.divide(np_avg_gain, np_avg_loss, out=np.full_like(np_avg_gain, np.nan), where=np_avg_loss!=0)
    
    rsi = 100 - (100 / (1 + rs))
    
    # Return the full RSI series, ensuring index alignment
    # The RSI series starts after the first 'period' calculations are done
    # The index should correspond to the days for which RSI is calculated
    rsi_index = prices.index[period + (len(prices.index) - len(delta)):] # Adjust index based on diff()
    
    # Ensure the length matches
    if len(rsi) > len(rsi_index):
        rsi = rsi[-len(rsi_index):] # Trim RSI if it\s longer
    elif len(rsi_index) > len(rsi):
         rsi_index = rsi_index[-len(rsi):] # Trim index if it\s longer
         
    return pd.Series(rsi, index=rsi_index)

def get_latest_rsi_for_validation(ticker):
    """Fetches data and calculates the latest RSI(25) using Wilder\s method."""
    try:
        stock = yf.Ticker(ticker)
        # Fetch more data (e.g., 1 year) to ensure enough history for accurate Wilder\s smoothing
        hist = stock.history(period="1y", interval="1d")
        
        if hist.empty or len(hist["Close"]) < RSI_PERIOD + 1:
            print(f"Not enough data for {ticker}")
            return None, np.nan
        
        rsi_series = calculate_rsi_wilder(hist["Close"], period=RSI_PERIOD)
        
        if rsi_series.empty or rsi_series.isnull().all():
            print(f"RSI calculation failed for {ticker}")
            return None, np.nan
            
        latest_rsi = rsi_series.iloc[-1]
        latest_date = rsi_series.index[-1].strftime("%Y-%m-%d")
        
        return latest_date, latest_rsi
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None, np.nan

# --- Validation --- 
tickers_to_validate = ["PNLF.JK", "BBCA.JK", "TLKM.JK", "ASII.JK"]
validation_results = {}

print("Validating RSI(25) Calculation (Wilder\s Smoothing)...")
for ticker in tickers_to_validate:
    print(f"Processing {ticker}...")
    date, rsi = get_latest_rsi_for_validation(ticker)
    if date:
        validation_results[ticker] = {"Date": date, "RSI(25)": f"{rsi:.2f}"}
    else:
        validation_results[ticker] = {"Date": "N/A", "RSI(25)": "Error"}

print("\n--- Validation Results ---")
for ticker, result in validation_results.items():
    print(f'{ticker}: Date={result["Date"]}, RSI(25)={result["RSI(25)"]}')

print("\nPlease compare these values with a reliable source like TradingView for the same dates.")


import json
import pandas as pd
import numpy as np

def calculate_rsi_wilder(prices, period=25):
    """Calculate RSI using Wilder's smoothing method."""
    delta = prices.diff()
    
    # Ensure delta starts from index 1
    delta = delta[1:]
    
    # Make the positive gains and negative losses series
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate the initial average gain and loss using SMA for the first period
    avg_gain = gain.rolling(window=period, min_periods=period).mean()[:period]
    avg_loss = loss.rolling(window=period, min_periods=period).mean()[:period]
    
    # Calculate subsequent averages using Wilder's smoothing
    # Formula: WilderAvg = (PreviousAvg * (period - 1) + CurrentValue) / period
    for i in range(period, len(gain)):
        avg_gain = np.append(avg_gain, (avg_gain[-1] * (period - 1) + gain.iloc[i]) / period)
        avg_loss = np.append(avg_loss, (avg_loss[-1] * (period - 1) + loss.iloc[i]) / period)
        
    # Handle division by zero for avg_loss
    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss!=0)
    
    rsi = 100 - (100 / (1 + rs))
    
    # Return the last RSI value
    return rsi[-1] if len(rsi) > 0 else np.nan

# Load the data
data_file = '/home/ubuntu/rsi_investigation/PNLF.JK_data.json'
try:
    with open(data_file, 'r') as f:
        data = json.load(f)

    # Extract timestamps and closing prices
    chart_data = data.get('chart', {}).get('result', [{}])[0]
    timestamps = chart_data.get('timestamp', [])
    close_prices = chart_data.get('indicators', {}).get('quote', [{}])[0].get('close', [])

    if not timestamps or not close_prices or len(timestamps) != len(close_prices):
        print("Error: Timestamps or close prices are missing or mismatched in the data.")
    else:
        # Create a pandas Series for closing prices
        prices = pd.Series(close_prices, index=pd.to_datetime(timestamps, unit='s'))
        
        # Ensure we have enough data points (at least period + 1)
        if len(prices) < 26:
             print(f"Error: Not enough data points ({len(prices)}) to calculate RSI(25).")
        else:
            # Calculate RSI(25) using Wilder's smoothing
            rsi_value_wilder = calculate_rsi_wilder(prices, period=25)
            print(f"Calculated RSI(25) for PNLF.JK (Wilder's Smoothing): {rsi_value_wilder:.2f}")

except FileNotFoundError:
    print(f"Error: Data file not found at {data_file}")
except Exception as e:
    print(f"An error occurred: {e}")


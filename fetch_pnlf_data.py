import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

client = ApiClient()

# Fetch historical data for PNLF.JK
symbol = "PNLF.JK"
interval = "1d"
data_range = "3mo"

try:
    # Attempting without specifying region first
    stock_data = client.call_api(
        'YahooFinance/get_stock_chart',
        query={
            'symbol': symbol,
            'interval': interval,
            'range': data_range,
            'includeAdjustedClose': True
        }
    )

    # Save the data to a JSON file
    output_file = f'/home/ubuntu/rsi_investigation/{symbol}_data.json'
    with open(output_file, 'w') as f:
        json.dump(stock_data, f, indent=2)

    print(f"Successfully fetched and saved data for {symbol} to {output_file}")

except Exception as e:
    print(f"Error fetching data for {symbol}: {e}")
    # If region is the issue, maybe try 'US' as a fallback, though unlikely for IDX
    # Or report the error


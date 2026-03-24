import yfinance as yf
import pandas as pd
import pandas_ta as ta 

def get_price_data(ticker, start_date, end_date):
    """Fetches historical price data from Yahoo Finance."""
    try:
        # 1. Clean up the dates just in case they have slashes (e.g., 2023/01/01 -> 2023-01-01)
        start_str = str(start_date).replace('/', '-')
        end_str = str(end_date).replace('/', '-')

        # 2. Use Ticker().history() instead of download(). It is much cleaner for single stocks!
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_str, end=end_str)
        
        # 3. Check if empty
        if df.empty:
            return None
            
        # 4. Remove timezone data from the index to prevent Plotly glitches
        df.index = df.index.tz_localize(None)
        # --- ADD TECHNICAL INDICATORS HERE ---
        # Calculate 20-day and 50-day Simple Moving Averages
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        # Note: pandas_ta names these columns 'SMA_20' and 'SMA_50' automatically
            
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
import yfinance as yf
import pandas as pd

def get_options_chain(ticker):
    """Fetches the options chain for the nearest expiration date."""
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        
        if not expirations:
            return None, None, None
            
        # Grab the very next expiration date
        nearest_expiry = expirations[0]
        chain = stock.option_chain(nearest_expiry)
        
        return nearest_expiry, chain.calls, chain.puts
    except Exception as e:
        print(f"Error fetching options: {e}")
        return None, None, None
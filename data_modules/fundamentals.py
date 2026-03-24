import yfinance as yf
import pandas as pd

def get_key_metrics(ticker):
    """Fetches high-level metrics like P/E, Market Cap, etc."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extracting only the useful metrics, handling missing data gracefully
        metrics = {
            "Market Cap": info.get("marketCap", "N/A"),
            "Trailing P/E": info.get("trailingPE", "N/A"),
            "Forward P/E": info.get("forwardPE", "N/A"),
            "Profit Margin": info.get("profitMargins", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A")
        }
        return metrics
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return None

def get_income_statement(ticker):
    """Fetches the annual income statement."""
    try:
        stock = yf.Ticker(ticker)
        # .financials returns the income statement
        df = stock.financials
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Error fetching income statement: {e}")
        return None
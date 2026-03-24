import numpy as np
import pandas as pd
import plotly.graph_objects as go

def calculate_risk_metrics(df):
    """Calculates Volatility, Max Drawdown, and Sharpe Ratio."""
    if df is None or df.empty:
        return None
    
    # Calculate daily percentage changes
    returns = df['Close'].pct_change().dropna()
    
    # Annualized Volatility (assuming 252 trading days in a year)
    daily_volatility = returns.std()
    annual_volatility = daily_volatility * np.sqrt(252)
    
    # Maximum Drawdown (The biggest historical drop from a peak)
    cumulative_returns = (1 + returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = cumulative_returns / rolling_max - 1
    max_drawdown = drawdown.min()
    
    # Sharpe Ratio (Assuming a basic 5% risk-free rate)
    risk_free_rate = 0.05
    annual_return = returns.mean() * 252
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    
    return {
        "Annual Volatility": annual_volatility,
        "Max Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe_ratio
    }

def run_monte_carlo(df, days_to_simulate=252, num_simulations=100):
    """Runs a Monte Carlo simulation generating 100 future price paths."""
    if df is None or df.empty:
        return None
        
    returns = df['Close'].pct_change().dropna()
    daily_vol = returns.std()
    mu = returns.mean()
    
    last_price = df['Close'].iloc[-1]
    
    # Generate random paths
    simulation_df = pd.DataFrame()
    for x in range(num_simulations):
        # Create a random normal distribution of returns
        daily_returns = np.random.normal(loc=mu, scale=daily_vol, size=days_to_simulate)
        price_series = [last_price]
        
        for r in daily_returns:
            # Calculate the next simulated day's price
            price_series.append(price_series[-1] * (1 + r))
            
        simulation_df[x] = price_series
        
    # Draw the chart using Plotly
    fig = go.Figure()
    for x in range(num_simulations):
        fig.add_trace(go.Scatter(
            y=simulation_df[x], 
            mode='lines', 
            line=dict(width=1, color='rgba(0, 150, 255, 0.1)'), # Transparent blue lines
            showlegend=False
        ))
        
    fig.update_layout(
        title=f"Monte Carlo Simulation ({num_simulations} Paths, Next {days_to_simulate} Days)",
        yaxis_title="Projected Price",
        xaxis_title="Days in Future",
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig
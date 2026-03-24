import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from data_modules.database import init_db, add_client, get_clients, add_holding, get_client_holdings
from data_modules.technicals import get_price_data
from data_modules.fundamentals import get_key_metrics, get_income_statement
from ai_module.gemini_bot import get_financial_summary
from data_modules.options import get_options_chain
from data_modules.quant import calculate_risk_metrics, run_monte_carlo
import datetime
init_db()

# --- 1. PAGE CONFIGURATION ---
# This sets the browser tab title and forces a wide layout for charts
st.set_page_config(page_title="Pro Terminal", page_icon="📈", layout="wide")

# --- 2. SIDEBAR (USER CONTROLS) ---
st.sidebar.header("⚙️ Terminal Controls")

# We use .NS for Indian stocks on Yahoo Finance. You can also type US tickers like AAPL.
ticker = st.sidebar.text_input("Enter Ticker (e.g., TCS.NS, RELIANCE.NS, AAPL)", "TCS.NS").upper()

# Date range selectors for historical data
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

st.sidebar.markdown("---") # Adds a nice divider line
st.sidebar.subheader("Technical Indicators")
show_sma20 = st.sidebar.checkbox("Show 20-Day SMA", value=False)
show_sma50 = st.sidebar.checkbox("Show 50-Day SMA", value=False)

st.sidebar.markdown("---")
st.sidebar.success("🟢 System Online")

# --- 3. MAIN DASHBOARD ---
st.title(f"📈 {ticker} - Financial Terminal")

# Create the 5 modular tabs for your specific pillars
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 1. Technical Analysis", 
    "🏢 2. Fundamental Analysis", 
    "📉 3. Options & Derivatives", 
    "🧮 4. Quant & Statistics", 
    "🤖 5. Gemini AI Insights", 
    "💼 6. Client Portfolios"
])

# Build the placeholders for each module
with tab1:
    st.header("Technical Analysis")
    
    # 1. Fetch the data with a loading spinner
    with st.spinner(f"Fetching market data for {ticker}..."):
        df = get_price_data(ticker, start_date, end_date)
    
    # 2. Check if data was found
    if df is not None:
        # 3. Build the Plotly Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        )])
        # --- NEW: ADD OVERLAYS IF CHECKED ---
        if show_sma20 and 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], 
                                     line=dict(color='blue', width=2), name='SMA 20'))
            
        if show_sma50 and 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], 
                                     line=dict(color='orange', width=2), name='SMA 50'))
        
        # 4. Format the chart to look professional
        fig.update_layout(
            title=f"{ticker} Live Price Action",
            yaxis_title="Price",
            xaxis_title="Date",
            template="plotly_dark",
            height=600,
            margin=dict(l=0, r=0, t=40, b=0), # Removes wasted space
            xaxis_rangeslider_visible=False
        )
        
        # 5. Display it in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error(f"❌ Could not fetch data for {ticker}. Please check the symbol and try again.")

with tab2:
    with tab2:
        st.header(f"{ticker} - Fundamental Analysis")
    
    with st.spinner("Fetching fundamentals..."):
        metrics = get_key_metrics(ticker)
        income_stmt = get_income_statement(ticker)
    
    if metrics:
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        # --- NEW: Indian Number Formatting (₹, Lakh Crore, Crore) ---
        mkt_cap = metrics["Market Cap"]
        if isinstance(mkt_cap, (int, float)):
            if mkt_cap >= 1e12: # Greater than 1 Lakh Crore
                mkt_cap_str = f"₹{mkt_cap/1e12:.2f} Lakh Cr"
            elif mkt_cap >= 1e7: # Greater than 1 Crore
                mkt_cap_str = f"₹{mkt_cap/1e7:.2f} Cr"
            else:
                mkt_cap_str = f"₹{mkt_cap:,.0f}"
        else:
            mkt_cap_str = mkt_cap

        margin = metrics["Profit Margin"]
        margin_str = f"{margin*100:.2f}%" if isinstance(margin, float) else margin
            
        col1.metric("Market Cap", mkt_cap_str)
        col2.metric("Trailing P/E", round(metrics["Trailing P/E"], 2) if isinstance(metrics["Trailing P/E"], float) else metrics["Trailing P/E"])
        col3.metric("Profit Margin", margin_str)
        
        # Updated 52W High to use the Rupee symbol
        col4.metric("52W High", f"₹{metrics['52 Week High']}" if metrics['52 Week High'] != 'N/A' else 'N/A')
        
    st.markdown("---") 
    
    if income_stmt is not None:
        st.subheader("Income Statement (in ₹ Lakh Crores)")
        
        # --- NEW: Format the Dataframe to Lakh Crores ---
        # 1. Convert all data to numbers safely
        numeric_stmt = income_stmt.apply(pd.to_numeric, errors='coerce')
        # 2. Divide by 1 Trillion (1 Lakh Crore)
        lakh_crore_stmt = numeric_stmt / 1e12
        # 3. Apply Streamlit Pandas styling to add the ₹ symbol and round to 3 decimal places
        styled_stmt = lakh_crore_stmt.style.format("₹{:.3f}")
        
        st.dataframe(styled_stmt, use_container_width=True)
    else:
        st.warning("Income Statement data not available for this ticker.")
   

with tab3:
    st.header(f"Options & Derivatives: {ticker}")
    
    with st.spinner("Fetching live options chain..."):
        expiry, calls, puts = get_options_chain(ticker)
        
    if expiry:
        st.subheader(f"Nearest Expiration Date: {expiry}")
        
        st.markdown("### 📈 Call Options (Bullish)")
        # We filter the dataframe to only show the most important columns
        st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']], use_container_width=True)
        
        st.markdown("### 📉 Put Options (Bearish)")
        st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']], use_container_width=True)
    else:
        st.warning(f"No options data available for {ticker}.")
    
with tab4:
    st.header(f"Quant & Statistics: {ticker}")
    
    with st.spinner("Calculating risk metrics and running simulations..."):
        # We fetch the price data again specifically for the math engine
        df = get_price_data(ticker, start_date, end_date)
        
        if df is not None:
            # --- RISK METRICS ---
            metrics = calculate_risk_metrics(df)
            if metrics:
                st.subheader("Risk & Return Profile")
                col1, col2, col3 = st.columns(3)
                
                vol = metrics["Annual Volatility"]
                dd = metrics["Max Drawdown"]
                sharpe = metrics["Sharpe Ratio"]
                
                col1.metric("Annualized Volatility", f"{vol*100:.2f}%")
                col2.metric("Maximum Drawdown", f"{dd*100:.2f}%")
                col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
            
            st.markdown("---")
            
            # --- MONTE CARLO SIMULATION ---
            st.subheader("Monte Carlo Price Projection")
            st.markdown("Simulating 100 possible future price paths based on historical volatility.")
            
            mc_fig = run_monte_carlo(df)
            if mc_fig:
                st.plotly_chart(mc_fig, use_container_width=True)
        else:
            st.error("Could not fetch data to run quantitative analysis.")

with tab5:
    with tab5:
        st.header(f"🤖 Gemini AI Insights: {ticker}")
        st.markdown("Generate an automated executive summary based on the current fundamental data.")
    
    # We only run the heavy AI task if the user clicks the button
        if st.button("Generate AI Report", type="primary"):
            with st.spinner("Gemini is analyzing the financials. Please wait..."):
            
            # 1. Fetch the data quietly in the background
             metrics = get_key_metrics(ticker)
             income_stmt = get_income_statement(ticker)
            
            # 2. Convert the dataframe to a string so the AI can read it
             if income_stmt is not None:
                # Get the last 3 years of data to keep the prompt size manageable
                stmt_string = income_stmt.iloc[:, :3].to_string() 
             else:
                stmt_string = "Income statement data unavailable."
                
            # 3. Call the AI module
             ai_report = get_financial_summary(ticker, metrics, stmt_string)
            
            # 4. Display the results beautifully
             st.markdown("---")
             st.write(ai_report)

with tab6:
    st.header("💼 Client Portfolio Management")
    st.markdown("Manage client holdings and track live Profit & Loss (P&L).")

    
    # Fetch existing clients
    clients_df = get_clients()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Manage Clients")
        new_client_name = st.text_input("New Client Name")
        if st.button("Add Client"):
            if new_client_name:
                success, msg = add_client(new_client_name)
                if success:
                    st.success(msg)
                    st.rerun() # Refreshes the app instantly to show the new client
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a name.")
                
        st.markdown("---")
        
        st.subheader("2. Add Trade Entry")
        if not clients_df.empty:
            # Create a dropdown mapping names to their database IDs
            client_dict = dict(zip(clients_df['name'], clients_df['id']))
            selected_client = st.selectbox("Select Client", options=list(client_dict.keys()))
            
            trade_ticker = st.text_input("Ticker (e.g., RELIANCE.NS, AAPL)").upper()
            trade_qty = st.number_input("Quantity", min_value=0.01, step=1.0)
            trade_price = st.number_input("Average Buy Price", min_value=0.01, step=1.0)
            
            if st.button("Log Trade"):
                if trade_ticker and trade_qty > 0 and trade_price > 0:
                    add_holding(client_dict[selected_client], trade_ticker, trade_qty, trade_price)
                    st.success(f"Logged {trade_qty} shares of {trade_ticker} for {selected_client}!")
                    st.rerun()
                else:
                    st.warning("Please fill out all trade fields correctly.")
        else:
            st.info("Add a client above to start logging trades.")

    with col2:
        st.subheader("Live Portfolio Dashboard")
        if not clients_df.empty:
            view_client = st.selectbox("View Dashboard For:", options=list(client_dict.keys()), key="view_client")
            holdings = get_client_holdings(client_dict[view_client])
            
            if not holdings.empty:
                st.write(f"**Current Holdings for {view_client}**")
                
                # Calculate Live P&L
                total_invested = 0
                total_current_value = 0
                
                # Create empty columns to store live data
                holdings['Live Price'] = 0.0
                holdings['Current Value'] = 0.0
                holdings['P&L (%)'] = 0.0
                
                with st.spinner("Fetching live market prices..."):
                    for index, row in holdings.iterrows():
                        try:
                            # Fetch the current price from Yahoo Finance
                            live_price = yf.Ticker(row['ticker']).history(period="1d")['Close'].iloc[-1]
                            invested = row['quantity'] * row['avg_price']
                            current_val = row['quantity'] * live_price
                            
                            holdings.at[index, 'Live Price'] = round(live_price, 2)
                            holdings.at[index, 'Current Value'] = round(current_val, 2)
                            holdings.at[index, 'P&L (%)'] = round(((current_val - invested) / invested) * 100, 2)
                            
                            total_invested += invested
                            total_current_value += current_val
                        except Exception:
                            holdings.at[index, 'Live Price'] = "Error"
                
                # Display high-level metrics
                total_pnl = total_current_value - total_invested
                pnl_color = "normal" if total_pnl >= 0 else "inverse"
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Invested", f"₹{total_invested:,.2f}")
                m2.metric("Current Portfolio Value", f"₹{total_current_value:,.2f}", f"₹{total_pnl:,.2f}", delta_color=pnl_color)
                
                # Display the beautifully formatted table
                st.dataframe(holdings.style.applymap(lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''), subset=['P&L (%)']), use_container_width=True)
                
            else:
                st.info(f"{view_client} has no trades logged yet.")
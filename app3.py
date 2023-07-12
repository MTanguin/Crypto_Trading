import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Disable the PyplotGlobalUseWarning
st.set_option('deprecation.showPyplotGlobalUse', False)

# Function to fetch the latest market data for a given cryptocurrency
def get_market_data(symbol):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD"
    headers = {
        "X-CMC_PRO_API_KEY": "589080bf-caaa-446c-9f76-9aed6450859e"  # Replace with your CoinMarketCap API key
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["data"][symbol]

st.title("Cryptocurrency Trading Strategies Based on Price Change Analysis")

# Function to visualize the percent change analysis
def visualize_percent_change(df):
    fig = px.bar(df, x="Symbol", y=["Percent Change 1h", "Percent Change 24h", "Percent Change 7d"],
                 title="Percent Change Analysis")
    fig.update_layout(xaxis_title="Cryptocurrency", yaxis_title="Percent Change (%)")
    st.plotly_chart(fig)

# Function to fetch the list of available cryptocurrencies from the API
def get_available_cryptocurrencies():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "X-CMC_PRO_API_KEY": "589080bf-caaa-446c-9f76-9aed6450859e"  # Replace with your CoinMarketCap API key
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    
    crypto_data = data["data"]
    crypto_symbols = [crypto["symbol"] for crypto in crypto_data]
    crypto_names = [crypto["name"] for crypto in crypto_data]
    crypto_prices = [crypto["quote"]["USD"]["price"] for crypto in crypto_data]
    crypto_percent_changes_1h = [crypto["quote"]["USD"]["percent_change_1h"] for crypto in crypto_data]
    crypto_percent_changes_24h = [crypto["quote"]["USD"]["percent_change_24h"] for crypto in crypto_data]
    crypto_percent_changes_7d = [crypto["quote"]["USD"]["percent_change_7d"] for crypto in crypto_data]
    market_cap_rank = [crypto["cmc_rank"] for crypto in crypto_data]

    df = pd.DataFrame({
        "Symbol": crypto_symbols,
        "Name": crypto_names,
        "Price (USD)": crypto_prices,
        "Percent Change 1h": crypto_percent_changes_1h,
        "Percent Change 24h": crypto_percent_changes_24h,
        "Percent Change 7d": crypto_percent_changes_7d,
        "Market Cap Rank": market_cap_rank
    })
    
    return df

# Fetch the available cryptocurrencies
crypto_data = get_available_cryptocurrencies()

# Display the data in a DataFrame format
st.markdown("##### Top 100 Cryptocurrencies Data:")
st.dataframe(crypto_data)

# Visualize the percent change analysis
visualize_percent_change(crypto_data)



# Trading strategy
def quantitative_trading(chosen_crypto, initial_capital):
    # Fetch the latest market data for the chosen cryptocurrency
    market_data = {chosen_crypto: get_market_data(chosen_crypto)}

    # Extract relevant information for trading decisions
    for symbol, data in market_data.items():
        price = data["quote"]["USD"]["price"]
        percent_change_1h = data["quote"]["USD"]["percent_change_1h"]
        percent_change_24h = data["quote"]["USD"]["percent_change_24h"]
        percent_change_7d = data["quote"]["USD"]["percent_change_7d"]
        market_cap_rank = data["cmc_rank"]

        # Trading logic
        if percent_change_1h > 0 and percent_change_24h > 0 or percent_change_7d > 0 and market_cap_rank <= 10:
            # Buy if all percent changes are positive and the cryptocurrency is within the top 10 by market cap
            st.write(f"Buy {symbol} at ${price:.10f}")
        elif percent_change_1h < 0 or percent_change_24h < 0 or percent_change_7d < 0:
            # Sell if any percent change is negative
            st.write(f"Sell {symbol} at ${price:.10f}")
        else:
            # Hold otherwise
            st.write(f"Hold {symbol} at ${price:.10f}")

        # Profit-taking logic
        if percent_change_24h > 10 or percent_change_7d > 10:
            # If the price has increased by more than 10% in the last 24 hours or 7 days, consider taking profits
            st.write(f"Take profits for {symbol} at ${price:.10f}")
        elif percent_change_24h < -10 or percent_change_7d < -10:
            # If the price has decreased by more than 10% in the last 24 hours or 7 days, consider cutting losses
            st.write(f"Cut losses for {symbol} at ${price:.10f}")

        # Calculate daily, weekly, and monthly returns
        returns_1d = percent_change_24h / 100
        returns_1w = percent_change_7d / 100
        returns_1m = None  # Replace with actual monthly returns calculation if available

        # Simulate trades with risk management
        capital = initial_capital
        position_size = capital * 0.1  # Allocate 10% of capital per trade
        num_trades = 10
        portfolio_value = []

        for _ in range(num_trades):
            # Execute the trade based on the trading strategy and risk management rules
            if percent_change_1h > 0 and percent_change_24h > 0 and percent_change_7d > 0 and market_cap_rank <= 10:
                # Buy
                shares = position_size / price
                capital -= position_size
            else:
                # Sell or hold
                shares = 0

            # Calculate portfolio value
            portfolio_value.append(capital + shares * price)

        # Calculate performance metrics
        if len(portfolio_value) > 1 and portfolio_value[0] != 0:
            cumulative_returns = (portfolio_value[-1] - portfolio_value[0]) / portfolio_value[0]
            average_daily_returns = np.mean(np.diff(portfolio_value) / portfolio_value[:-1])
            volatility = np.std(np.diff(portfolio_value) / portfolio_value[:-1])
        else:
            cumulative_returns = 0
            average_daily_returns = 0
            volatility = 0

        st.write(f"Symbol: {symbol}")
        st.write(f"Cumulative Returns: {cumulative_returns:.2%}")
        st.write(f"Average Daily Returns: {average_daily_returns:.2%}")
        st.write(f"Volatility: {volatility:.2%}")

        # Data for visualization
        data = {
            "Metric": ["Percent Change 1h", "Percent Change 24h", "Percent Change 7d", "Market Cap Rank"],
            "Value": [percent_change_1h, percent_change_24h, percent_change_7d, market_cap_rank],
            "Cryptocurrency": [symbol] * 4
        }
        df = pd.DataFrame(data)

        # Visualization - Bar plot of percent changes and market cap rank
        fig = px.bar(df, x="Metric", y="Value", color="Metric", barmode="group", title=f"{symbol} Data")
        st.plotly_chart(fig)

        # Visualization - Line plot of portfolio value
        data = {"Trade": range(num_trades),
                "Portfolio Value": portfolio_value}
        df_portfolio = pd.DataFrame(data)

        fig_portfolio = go.Figure()
        fig_portfolio.add_trace(go.Scatter(x=df_portfolio['Trade'], y=df_portfolio['Portfolio Value'], mode='lines+markers', name='Portfolio Value'))
        fig_portfolio.update_layout(xaxis_title="Trade", yaxis_title="Portfolio Value ($)", title="Portfolio Value Over Time")
        st.plotly_chart(fig_portfolio)

# Create the Streamlit app
def run_app():
    # Set app title
    st.title("Trading Strategies")

    # Fetch the available cryptocurrencies
    available_cryptos = get_available_cryptocurrencies()

    # Prompt the user to choose the cryptocurrency for trading
    chosen_crypto = st.selectbox("Select the cryptocurrency for trading:", available_cryptos)
    initial_capital = st.number_input("Enter your initial capital:", min_value=0.0)

    # Execute the trading strategy
    quantitative_trading(chosen_crypto, initial_capital)

# Run the Streamlit app
if __name__ == "__main__":
    run_app()


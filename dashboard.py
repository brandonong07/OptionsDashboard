import datetime
import api as api
import streamlit as st
import pandas as pd
import json
import plotly.express as px

def main():
    st.set_page_config(layout="wide") # Expands dashboard to utilize full screen width
    
    st.title("⚡ Options Dashboard")
    st.subheader("Underlying Asset: SPX")
    
    # Put your informational Greeks markdown in a clean sidebar expander to save screen real estate
    with st.sidebar.expander("Read Greek Definitions"):
        st.markdown("""
        **Standard Greeks**
        * **IV**: Implied Volatility (0-25% Quiet, 50%+ Wild).
        * **Delta**: Directional sensitivity ($0 to $1 change).
        * **Gamma**: Acceleration of Delta.
        * **Theta**: Time decay factor.
        * **Scholes**: Analytical Fair Price.
        
        **Advanced Greeks**
        * **Vanna**: Delta sensitivity to IV shifts.
        * **Charm**: Hourly/Daily Delta bleed.
        * **Speed**: Gamma sensitivity to price shifts.
        * **Vomma**: Vega acceleration to IV shifts.
        """)

    # Date Selection Configuration
    st.sidebar.header("Select Date Options")
    default_date = datetime.date.today()
    selected_date = st.sidebar.date_input("Target Expiration Date", default_date)
    amt_strikes = st.sidebar.number_input("Number of Strikes to Display", min_value=1, max_value=50, value=20, step=1)
    
    if selected_date < default_date:
        st.sidebar.error("Please select a valid date (0DTE or in the future).")
        return

    # Triggering Backend Data Refreshes via the Schwab Client Engine
    if st.sidebar.button("Update Data Pipeline"):
        with st.spinner("Fetching live metrics from Schwab API..."):
            status = api.main(selected_date, amt_strikes)
            if status == "API Request Failed":
                st.sidebar.error("Failed to update data.")
            else:
                st.sidebar.success(f"Updated for {selected_date}!")

    # SAFE FILE READING - Always executes outside the button condition
    try:
        with open("options_ladder.json", "r") as f:
            options_data = json.load(f)
        df = pd.DataFrame(options_data)
    except (FileNotFoundError, json.JSONDecodeError):
        st.info(" No live options matrix detected. Click 'Update Data Pipeline' to fetch market variables.")
        return

    if not df.empty:
        # Dynamically calculate days to expiry for display
        days_to_expiry = (selected_date - datetime.date.today()).days
        
        # Display Key Metrics in nice clean cards
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(label="SPX Spot Price", value=f"${df['Underlying'].iloc[0]:,.2f}")
        with col_metric2:
            st.metric(label="Days to Expiration", value=f"{days_to_expiry} Days (0DTE Mode)" if days_to_expiry == 0 else f"{days_to_expiry} Days")

        # Split Data Streams for specialized layouts
        callData = df[df["Direction"] == "CALL"]
        putData = df[df["Direction"] == "PUT"]

        # Main Layout Navigation Tabs
        tab1, tab2, tab3 = st.tabs(["Combined Analytics Ladder", "Calls Engine", "Puts Engine"])
        
        target_columns = ["Strike", "Bid", "Ask", "IV", "Delta", "Gamma", "Theta", "Scholes", "Vanna_1%_IV", "Charm_per_hour", "Speed_10pt", "Vomma_1%_IV"]

        with tab1:
            st.subheader("Combined Order Matrix Grid")
            st.dataframe(df[["Direction"] + target_columns], use_container_width=True, height=400)

        with tab2:
            st.subheader("Calls Advanced Analytics Stream")
            st.dataframe(callData[target_columns], use_container_width=True, height=400)

        with tab3:
            st.subheader("Puts Advanced Analytics Stream")
            st.dataframe(putData[target_columns], use_container_width=True, height=400)


if __name__ == "__main__":
    main()
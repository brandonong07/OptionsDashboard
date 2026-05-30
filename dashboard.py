import streamlit as st
import pandas as pd
import json
import plotly.express as px

def main():
    st.title("Options Ladder Dashboard")
    
    # Load the options ladder data from the JSON file
    with open("options_ladder.json", "r") as f:
        options_data = json.load(f)
    
    df = pd.DataFrame(options_data)
    
    callData = df[df["Direction"] == "CALL"]
    putData = df[df["Direction"] == "PUT"]
    # Display the options ladder in a table
    st.subheader("Underlying Asset: SPX")
    st.write("Price: " + str(df["Underlying"].iloc[0]))
    st.subheader("Options Greeks")
    st.markdown("""
    - IV: Implied Volatility
        - Low IV means the stock is expected to be quiet, making the option cheaper.
            - (0-25): Options are generally cheaper, indicating low expected volatility.
            - (25-50): Options are moderately priced, indicating moderate expected volatility.
        - High IV means larger expected price swings, which makes the option more expensive.
            - (50-100): Options are more expensive, indicating high expected volatility.
            - (100+): Options are very expensive, indicating extremely high expected volatility.
    - Delta: Measures how much the option price changes for a $1 change in the underlying asset price.
        - For calls, delta ranges from 0 to 1. 
        - For puts, it ranges from -1 to 0.
    - Gamma: Measures how much the delta changes for a $1 change in the underlying asset price.
    - Theta: Measures how much the option price decreases as time passes, all else being equal.
    - Scholes: Theoretical price of the option based on the Black-Scholes model.
    """)
    st.subheader("Advanced Options Greeks")
    st.markdown("""
    - Vanna: Measures how much the option's delta changes for a 1% change in implied volatility.
    - Charm: Measures how much the option's delta changes as time passes, all else being equal.
    - Speed: Measures how much the option's gamma changes for a $1 change in the underlying asset price.
    - Vomma: Measures how much the option's vega changes for a 1% change in implied volatility.
    """)

    st.subheader("Calls Ladder")
    st.dataframe(callData[["Strike", "Bid", "Ask", "IV", "Delta", "Gamma", "Theta", "Scholes", "Vanna", "Charm", "Speed", "Vomma"]])
    
    st.subheader("Puts Ladder")
    st.dataframe(putData[["Strike", "Bid", "Ask", "IV", "Delta", "Gamma", "Theta", "Scholes", "Vanna", "Charm", "Speed", "Vomma"]])
    
    st.subheader("Combined Ladder")
    st.dataframe(df[["Direction", "Strike", "Bid", "Ask", "IV", "Delta", "Gamma", "Theta", "Scholes", "Vanna", "Charm", "Speed", "Vomma"]])

    # Create a scatter plot of Strike vs IV colored by Option Type
    st.subheader("Strike vs Implied Volatility")
    fig = px.scatter(df, x="Strike", y="IV", color="Direction", title="Strike vs IV")
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
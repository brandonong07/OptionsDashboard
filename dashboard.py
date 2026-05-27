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
    
    # Display the options ladder in a table
    st.subheader("Options Ladder")
    st.dataframe(df)
    
    # Create a scatter plot of Strike vs IV colored by Option Type
    st.subheader("Strike vs Implied Volatility")
    fig = px.scatter(df, x="Strike", y="IV", color="Direction", title="Strike vs IV")
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
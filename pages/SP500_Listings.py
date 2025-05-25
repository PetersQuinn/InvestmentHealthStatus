import streamlit as st
import pandas as pd
import os

st.title("📘 S&P 500 Risk Score Listings (CSV Mode)")

csv_path = "sp500_risk_scores.csv"

if not os.path.exists(csv_path):
    st.error("CSV file not found. Please generate it using the batch builder script.")
    st.stop()

# Load the existing CSV
try:
    df = pd.read_csv(csv_path)
    st.success("Loaded S&P 500 risk scores from CSV cache.")
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

# Display the dataframe with column sorting and formatting
st.dataframe(
    df.reset_index(drop=True),
    column_config={
        "Z-Score Risk": st.column_config.NumberColumn(
            "Z-Score Risk",
            format="%d",
            help="Normalized risk score where higher = less risky"
        )
    }
)

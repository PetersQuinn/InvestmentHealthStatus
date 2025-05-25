import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

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

# Display the date range of the dataset
if "Date" in df.columns:
    try:
        df["Date"] = pd.to_datetime(df["Date"])
        min_date = df["Date"].min().strftime("%Y-%m-%d")
        max_date = df["Date"].max().strftime("%Y-%m-%d")
        st.info(f"Data last updated from: {min_date} to {max_date}")
    except Exception:
        st.warning("Could not parse date column properly.")

# Prompt for updating with a warning
if st.button("🔄 Update Dataset"):
    st.warning(
        "You're about to refresh the dataset. This may trigger Yahoo Finance rate limits."
        " Consider using the current dataset unless updates are absolutely needed.",
        icon="⚠️"
    )
    confirm = st.checkbox("I understand the risks and want to update.")
    if confirm:
        st.error("Update logic not yet implemented. Please run the batch builder script instead.")
    else:
        st.stop()

# Show average statistics if numeric columns exist
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if numeric_cols:
    st.subheader("📊 Column Averages")
    averages = df[numeric_cols].mean().round(2)
    for col, val in averages.items():
        st.write(f"**{col}**: {val}")

# Display the dataframe with column sorting and formatting
st.dataframe(
    df.reset_index(drop=True),
    column_config={
        "Z-Score Risk": st.column_config.NumberColumn(
            "Z-Score Risk",
            format="%d",
            help="Normalized risk score where higher = less risky"
        ),
        "VaR Risk": st.column_config.NumberColumn(
            "VaR Risk",
            format="%.2f",
            help="Value-at-Risk-based score where higher = less risky"
        ),
        "Factor-Based": st.column_config.NumberColumn(
            "Factor-Based",
            format="%.2f",
            help="Weighted factor score including beta, ROA, price-to-book, etc."
        )
    }
)


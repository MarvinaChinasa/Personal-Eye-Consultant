import streamlit as st
import pandas as pd

# 1. Secure Import for Google Sheets Connection
try:
    from st_gsheets_connection import GSheetsConnection
except ImportError:
    from streamlit_gsheets_connection import GSheetsConnection

# 2. Page Configuration
st.set_page_config(page_title="Eye Consultant AI", page_icon="👁️")

st.title("👁️ Personal Eye Consultant")

# 3. Establish Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Test read: change 'Sheet1' to your actual sheet name if different
    df = conn.read()
    
    st.success("Successfully connected to Google Sheets!")
    
    # Show a preview of the data
    if st.checkbox("Show Data Preview"):
        st.write(df.head())

except Exception as e:
    st.error("Connection failed. Please check your Secrets and Google Sheet sharing settings.")
    st.info(f"Error Details: {e}")

# --- YOUR APP LOGIC BELOW ---
st.write("Welcome to your AI consultant. Use the sidebar to navigate.")

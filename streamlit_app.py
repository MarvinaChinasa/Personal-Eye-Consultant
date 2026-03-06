import streamlit as st
from st_gsheets_connection import GSheetsConnection

st.set_page_config(page_title="Eye Consultant Test")

st.title("👁️ Eye Consultant Connection Test")

# Attempt to connect
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    st.success("✅ Connection Successful!")
    st.write("Here is the data from your sheet:")
    st.dataframe(df.head())
except Exception as e:
    st.error("❌ Connection failed.")
    st.exception(e)

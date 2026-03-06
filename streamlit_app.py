import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Eye Consultant", page_icon="👁️")

st.title("👁️ Personal Eye Consultant")

# Connection Logic
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    st.success("✅ Database Connected!")
    st.dataframe(df.head())
except Exception as e:
    st.error("❌ Connection failed. Check your Secrets and Sheet sharing.")
    st.info(f"Technical error: {e}")

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Personal Eye Consultant",
    page_icon="👁️",
    layout="wide"
)

# --- CUSTOM CSS FOR AESTHETICS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007BFF;
        color: white;
    }
    .status-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/health_64dp.png", width=80)
    st.title("Navigation")
    page = st.radio("Go to", ["Home", "Consultation", "History & Analytics"])
    st.divider()
    st.info("This AI tool provides guidance based on clinical data. Always consult a real doctor for emergencies.")

# --- DATABASE CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    connection_status = True
except Exception as e:
    connection_status = False
    error_msg = str(e)

# --- MAIN PAGE LOGIC ---
if page == "Home":
    st.title("👁️ Personal Eye Consultant")
    st.subheader("Your AI-Powered Vision Health Companion")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### How it works:
        1. **Input Symptoms**: Describe your eye discomfort.
        2. **AI Analysis**: Our model compares data to suggest possible causes.
        3. **Track Health**: View your history over time.
        """)
        if st.button("Start Consultation"):
            st.info("Please select 'Consultation' from the sidebar.")
            
    with col2:
        if connection_status:
            st.success("✅ System Online: Database Connected")
        else:
            st.error("⚠️ System Offline: Database Connection Error")

elif page == "Consultation":
    st.title("🩺 Symptom Assessment")
    
    with st.form("consultation_form"):
        st.write("Fill in the details below for an AI assessment:")
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
        symptom = st.selectbox("Primary Symptom", ["Redness", "Blurry Vision", "Itching", "Pain", "Dryness"])
        duration = st.slider("Duration (Days)", 1, 30, 3)
        
        submitted = st.form_submit_button("Analyze Results")
        
        if submitted:
            if connection_status:
                st.balloons()
                st.write("### Assessment Results")
                st.write(f"Based on your report of **{symptom}**, we are analyzing the database...")
                # Here you would add your joblib.load() and model.predict() logic
            else:
                st.warning("Assessment is limited because the database is disconnected.")

elif page == "History & Analytics":
    st.title("📊 Health Trends")
    if connection_status and not df.empty:
        st.write("Visualizing your consultation history:")
        fig = px.bar(df, x=df.columns[0], y=df.columns[1], title="Consultation Frequency")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No history data available yet.")

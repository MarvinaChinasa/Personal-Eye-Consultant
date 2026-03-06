import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="Personal Eye Consultant",
    page_icon="👁️",
    layout="wide"
)

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007BFF; color: white; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY CHECK ---
def check_password():
    """Returns True if the user had the correct password in Secrets."""
    if "ADMIN_PASSWORD" not in st.secrets:
        st.error("Configuration Error: 'ADMIN_PASSWORD' not found in Streamlit Secrets.")
        return False

    if "password_correct" not in st.session_state:
        st.title("🔒 Eye Consultant Secure Portal")
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Unlock System"):
            if password == st.secrets["ADMIN_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password")
        return False
    return True

# --- 3. MAIN APP EXECUTION ---
if check_password():
    
    # --- DATABASE CONNECTION ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_history = conn.read(ttl=0)
        db_connected = True
    except Exception as e:
        db_connected = False
        db_error = str(e)

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2850/2850935.png", width=100)
        st.title("Main Menu")
        page = st.radio("Navigation", ["Dashboard", "AI Consultation", "History Log"])
        st.divider()
        if st.button("Logout"):
            del st.session_state["password_correct"]
            st.rerun()

    # --- PAGE 1: DASHBOARD ---
    if page == "Dashboard":
        st.title("👁️ Personal Eye Consultant AI")
        st.write("Welcome to the clinical decision support system.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("System Status", "Online" if db_connected else "Offline")
        with col2:
            count = len(df_history) if db_connected else 0
            st.metric("Total Consultations", count)
        with col3:
            st.metric("AI Model Status", "Ready")

        st.subheader("Instructions")
        st.info("""
        1. Navigate to **AI Consultation** to input patient metrics.
        2. Provide details including screen time, light exposure, and physical metrics.
        3. The AI will provide a recommendation and sync it to your Google Sheet.
        """)

    # --- PAGE 2: AI CONSULTATION ---
    elif page == "AI Consultation":
        st.title("🩺 AI Symptom Assessment")
        
        model_path = 'eye_health_model.pkl'
        model_ready = False

        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                model_ready = True
            except Exception as e:
                st.error(f"⚠️ Model Load Error: {e}")
        
        with st.form(key="final_eye_form"):
            st.subheader("Section 1: Physical & Lifestyle Metrics")
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", 0, 110, 25)
                height_cm = st.number_input("Height (cm)", 100, 220, 170)
                glasses_number = st.number_input("Glasses Number (Diopters)", -20.0, 20.0, 0.0)
            with c2:
                exercise_hours = st.number_input("Weekly Exercise (Hours)", 0, 40, 5)
                mental_health_score = st.slider("Mental Health Score (1-10)", 1, 10, 7)

            st.divider()
            st.subheader("Section 2: Digital Habits & Environment")
            c3, c4 = st.columns(2)
            with c3:
                screen_time_hours = st.number_input("Daily Screen Time (Hours)", 0, 24, 8)
                screen_distance_cm = st.number_input("Screen Distance (cm)", 10, 100, 50)
                screen_brightness_avg = st.slider("Average Screen Brightness (%)", 0, 100, 70)
            with c4:
                outdoor_light_exposure_hours = st.number_input("Outdoor Light Exposure (Hours)", 0, 24, 2)
                night_mode_usage = st.selectbox("Night Mode Usage", ["Always

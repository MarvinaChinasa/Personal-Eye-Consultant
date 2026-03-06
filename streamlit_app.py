import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Eye Consultant", page_icon="👁️", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PASSWORD PROTECTION ---
def check_password():
    """Returns True if the user had the correct password."""
    # Check if ADMIN_PASSWORD even exists in Secrets
    if "ADMIN_PASSWORD" not in st.secrets:
        st.error("Missing Secret: 'ADMIN_PASSWORD' not found in Streamlit Secrets.")
        st.info("Please go to Settings -> Secrets and add: ADMIN_PASSWORD = 'yourpassword'")
        return False

    if "password_correct" not in st.session_state:
        st.title("🔒 Security Portal")
        password = st.text_input("Please enter the Admin Password", type="password")
        if st.button("Unlock App"):
            if password == st.secrets["ADMIN_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password")
        return False
    return True

# --- 3. MAIN APP LOGIC ---
if check_password():
    # SIDEBAR
    with st.sidebar:
        st.title("👁️ Navigation")
        page = st.radio("Go to", ["Home", "Consultation", "Analytics"])
        st.divider()
        if st.button("Logout"):
            del st.session_state["password_correct"]
            st.rerun()

    # DATABASE CONNECTION
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        db_connected = True
    except Exception as e:
        db_connected = False
        error_details = str(e)

    # PAGE ROUTING
    if page == "Home":
        st.title("👁️ Eye Consultant AI")
        st.subheader("Welcome to your professional vision health assistant.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Getting Started\nUse the sidebar to navigate to your assessment.")
            if db_connected:
                st.success("✅ Database System: Online")
            else:
                st.error("❌ Database System: Offline")
        
    elif page == "Consultation":
        st.title("🩺 Symptom Assessment")
        if not db_connected:
            st.warning("Assessment is in 'Offline Mode' - Data saving is disabled.")
        
        with st.form("medical_form"):
            age = st.number_input("Patient Age", 0, 120, 25)
            symptom = st.selectbox("Main Symptom", ["Redness", "Blurry Vision", "Pain", "Itching"])
            notes = st.text_area("Additional Details")
            submitted = st.form_submit_button("Analyze")
            
            if submitted:
                st.info("Analysis complete. Suggestion: Please rest your eyes and consult a specialist.")

    elif page == "Analytics":
        st.title("📊 History & Data")
        if db_connected and not df.empty:
            st.dataframe(df)
            fig = px.pie(df, names=df.columns[0], title="Symptom Distribution")
            st.plotly_chart(fig)
        else:
            st.info("No data available to display.")


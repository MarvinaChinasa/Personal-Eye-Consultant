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
    
    # DATABASE CONNECTION
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_history = conn.read(ttl=0)
        db_connected = True
    except Exception as e:
        db_connected = False
        db_error = str(e)

    # SIDEBAR
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2850/2850935.png", width=100)
        st.title("Main Menu")
        page = st.radio("Navigation", ["Dashboard", "AI Consultation", "History Log"])
        st.divider()
        if st.button("Logout"):
            del st.session_state["password_correct"]
            st.rerun()

    # PAGE 1: DASHBOARD
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

        st.info("Navigate to **AI Consultation** to begin a patient assessment.")

    # PAGE 2: AI CONSULTATION
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
                # --- FIXED LINE BELOW ---
                night_mode_usage = st.selectbox("Night Mode Usage", ["Always", "Sometimes", "Never"])
                nm_map = {"Always": 2, "Sometimes": 1, "Never": 0}
                nm_val = nm_map[night_mode_usage]
            
            submit = st.form_submit_button("🚀 Run AI Diagnosis")

            if submit:
                if model_ready:
                    try:
                        input_data = pd.DataFrame([[
                            age, exercise_hours, glasses_number, height_cm, 
                            mental_health_score, nm_val, outdoor_light_exposure_hours, 
                            screen_brightness_avg, screen_distance_cm, screen_time_hours
                        ]], columns=[
                            'age', 'exercise_hours', 'glasses_number', 'height_cm', 
                            'mental_health_score', 'night_mode_usage', 'outdoor_light_exposure_hours', 
                            'screen_brightness_avg', 'screen_distance_cm', 'screen_time_hours'
                        ])
                        
                        prediction = model.predict(input_data)
                        result = prediction[0]

                        st.markdown("---")
                        st.subheader("AI Recommendation")
                        st.success(f"Assessment: **{result}**")

                        if db_connected:
                            new_row = pd.DataFrame([{
                                "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                                "Age": age,
                                "Recommendation": result
                            }])
                            updated_df = pd.concat([df_history, new_row], ignore_index=True)
                            conn.update(data=updated_df)
                            st.write("✅ Record synced to cloud database.")
                            
                    except Exception as e:
                        st.error(f"Prediction Error: {e}")
                else:
                    st.error("AI Analysis unavailable.")

    # PAGE 3: HISTORY LOG
    elif page == "History Log":
        st.title("📊 Consultation History")
        if db_connected and not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("No records found.")

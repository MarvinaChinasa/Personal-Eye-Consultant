import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Personal Eye Consultant", page_icon="👁️", layout="wide")

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
        st.error("Configuration Error: 'ADMIN_PASSWORD' not found in Secrets.")
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

    # SIDEBAR
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2850/2850935.png", width=100)
        st.title("Main Menu")
        page = st.radio("Navigation", ["Dashboard", "AI Consultation", "History Log"])
        if st.button("Logout"):
            del st.session_state["password_correct"]
            st.rerun()

    # PAGE 1: DASHBOARD
    if page == "Dashboard":
        st.title("👁️ Personal Eye Consultant AI")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("System Status", "Online" if db_connected else "Offline")
        with col2: st.metric("Total Consultations", len(df_history) if db_connected else 0)
        with col3: st.metric("AI Model Status", "Ready")
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
            st.subheader("Patient Metrics & Habits")
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", 0, 110, 25)
                height_cm = st.number_input("Height (cm)", 100, 220, 170)
                glasses_number = st.number_input("Glasses Number", -20.0, 20.0, 0.0)
                exercise_hours = st.number_input("Weekly Exercise (Hours)", 0, 40, 5)
                mental_health_score = st.slider("Mental Health Score (1-10)", 1, 10, 7)
            with c2:
                screen_time_hours = st.number_input("Daily Screen Time (Hours)", 0, 24, 8)
                screen_distance_cm = st.number_input("Screen Distance (cm)", 10, 100, 50)
                screen_brightness_avg = st.slider("Screen Brightness (%)", 0, 100, 70)
                outdoor_light_exposure_hours = st.number_input("Outdoor Light (Hours)", 0, 24, 2)
                night_mode_usage = st.selectbox("Night Mode Usage", ["Always", "Sometimes", "Never"])
                nm_map = {"Always": 2, "Sometimes": 1, "Never": 0}
                nm_val = nm_map[night_mode_usage]
            
            submit = st.form_submit_button("🚀 Run AI Diagnosis")

            if submit and model_ready:
                try:
                    # 1. Gather all inputs into a dictionary
                    features = {
                        'age': age,
                        'exercise_hours': exercise_hours,
                        'glasses_number': glasses_number,
                        'height_cm': height_cm,
                        'mental_health_score': mental_health_score,
                        'night_mode_usage': nm_val,
                        'outdoor_light_exposure_hours': outdoor_light_exposure_hours,
                        'screen_brightness_avg': screen_brightness_avg,
                        'screen_distance_cm': screen_distance_cm,
                        'screen_time_hours': screen_time_hours
                    }
                    
                    # 2. Create initial DataFrame
                    input_df = pd.DataFrame([features])
                    
                    # 3. AUTO-ALIGNMENT: Force the DataFrame to match the model's training order
                    if hasattr(model, "feature_names_in_"):
                        # This tells the code to reorganize itself based on the model's internal memory
                        input_df = input_df[model.feature_names_in_]
                    
                    # 4. Predict
                    prediction = model.predict(input_df)
                    result = prediction[0]

                    st.markdown("---")
                    st.success(f"AI Recommendation: **{result}**")

                    if db_connected:
                        new_row = pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Age": age, "Result": result}])
                        updated_df = pd.concat([df_history, new_row], ignore_index=True)
                        conn.update(data=updated_df)
                        st.write("✅ Saved to History.")
                            
                except Exception as e:
                    st.error(f"Prediction Error: {e}")
                    # Debug helper: if it still fails, let's see what order the model wants
                    if hasattr(model, "feature_names_in_"):
                        st.info(f"The model expects this order: {list(model.feature_names_in_)}")

    # PAGE 3: HISTORY LOG
    elif page == "History Log":
        st.title("📊 Consultation History")
        if db_connected and not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("No records found.")

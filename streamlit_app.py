import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Public Eye Consultant", page_icon="👁️", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #007BFF; color: white; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION (Global) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_history = conn.read(ttl=0)
    db_connected = True
except Exception:
    db_connected = False
    df_history = pd.DataFrame()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2850/2850935.png", width=100)
    st.title("Eye AI Portal")
    page = st.radio("Navigation", ["Welcome", "AI Consultation", "Admin History Log"])
    st.divider()
    st.info("Public access enabled for Consultations.")

# --- PAGE 1: WELCOME (PUBLIC) ---
if page == "Welcome":
    st.title("👁️ Personal Eye Consultant AI")
    st.write("Welcome to the public portal for eye health assessment.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("System Status", "Online & Ready")
    with col2:
        st.metric("Privacy", "Anonymous Use")

    st.info("👈 Select **AI Consultation** from the sidebar to begin your assessment.")

# --- PAGE 2: AI CONSULTATION (PUBLIC) ---
elif page == "AI Consultation":
    st.title("🩺 Start Your Assessment")
    model_path = 'eye_health_model.pkl'
    
    # Model Loading
    model_ready = False
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            model_ready = True
        except:
            st.error("Model load error.")
    else:
        st.warning("Model file not found.")

    # THE FORM (Inputs Only)
    with st.form(key="public_eye_form"):
        st.subheader("Please provide your metrics:")
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
        
        submit = st.form_submit_button("🚀 Get AI Result")

    # LOGIC OUTSIDE THE FORM (Results & Download)
    if submit and model_ready:
        try:
            # Prepare data
            features = {
                'age': age, 'exercise_hours': exercise_hours, 'glasses_number': glasses_number,
                'height_cm': height_cm, 'mental_health_score': mental_health_score,
                'night_mode_usage': nm_val, 'outdoor_light_exposure_hours': outdoor_light_exposure_hours,
                'screen_brightness_avg': screen_brightness_avg, 'screen_distance_cm': screen_distance_cm,
                'screen_time_hours': screen_time_hours
            }
            input_df = pd.DataFrame([features])
            
            # Auto-align columns to model's expected order
            if hasattr(model, "feature_names_in_"):
                input_df = input_df[model.feature_names_in_]
            
            prediction = model.predict(input_df)
            result = prediction[0]

            st.markdown("---")
            st.success(f"### AI Recommendation: {result}")
            
            # Download Button (SAFE OUTSIDE FORM)
            report_text = f"Eye AI Assessment Report\n" \
                          f"------------------------\n" \
                          f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n" \
                          f"Age: {age}\n" \
                          f"Result: {result}\n" \
                          f"Note: This is an AI-generated suggestion, not a medical diagnosis."
            
            st.download_button(
                label="📥 Download My Report",
                data=report_text,
                file_name=f"Eye_Report_{age}.txt",
                mime="text/plain"
            )

            # Sync to Google Sheets (Hidden from user)
            if db_connected:
                new_row = pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Age": age, "Result": result}])
                updated_df = pd.concat([df_history, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
        except Exception as e:
            st.error(f"Analysis Error: {e}")

# --- PAGE 3: ADMIN HISTORY LOG (PASSWORD PROTECTED) ---
elif page == "Admin History Log":
    st.title("🔒 Admin Records")
    
    # Session state for login persistence
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        passwd = st.text_input("Enter Admin Password", type="password")
        if st.button("Access Logs"):
            if passwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    else:
        # If logged in
        col_header, col_logout = st.columns([4, 1])
        with col_logout:
            if st.button("Logout Admin"):
                st.session_state["admin_logged_in"] = False
                st.rerun()
            
        if db_connected and not df_history.empty:
            st.write("### Patient Consultation History")
            st.dataframe(df_history, use_container_width=True)
            
            # Analytics Chart
            if "Result" in df_history.columns:
                fig = px.pie(df_history, names="Result", title="Historical Diagnosis Distribution")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No records found in the connected Google Sheet.")

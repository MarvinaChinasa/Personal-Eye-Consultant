import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Eye AI Consultant", page_icon="👁️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    section[data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    section[data-testid="stSidebar"] * {
        color: #fbbf24 !important;
        font-size: 18px !important;
        font-weight: 800 !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%);
        color: white;
        font-weight: bold;
        height: 3.5em;
    }
    .result-box {
        padding: 20px;
        border-radius: 15px;
        background-color: #ecfdf5;
        border: 2px solid #10b981;
        text-align: center;
        color: #065f46;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_history = conn.read(ttl=0)
    db_connected = True
except:
    db_connected = False
    df_history = pd.DataFrame()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### VISION MENU")
    page = st.radio("", ["🏠 Welcome", "🩺 AI Consultation", "🔒 Admin Records"])

# --- PAGE 1: WELCOME ---
if page == "🏠 Welcome":
    st.title("👁️ Personal Eye Consultant AI")
    st.write("Understand your eye health through the lens of Artificial Intelligence.")
    st.info("Our model evaluates 10 different physical and digital lifestyle factors to estimate eye strain risks.")
    st.markdown("""
    ### How it Works
    - **Digital Hygiene:** Tracks screen time and brightness.
    - **Environment:** Analyzes outdoor light and exercise.
    - **Physical Baseline:** Accounts for age and current prescription.
    """)

# --- PAGE 2: AI CONSULTATION ---
elif page == "🩺 AI Consultation":
    st.title("🩺 AI Assessment")
    model_path = 'eye_health_model.pkl'
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        
        with st.form(key="eye_form"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", 0, 110, 25)
                height = st.number_input("Height (cm)", 100, 220, 170)
                glasses = st.number_input("Glasses Power", -20.0, 20.0, 0.0)
                exercise = st.number_input("Exercise (Hrs/Week)", 0, 40, 5)
                mental = st.slider("Well-being (1-10)", 1, 10, 7)
            with col2:
                scr_time = st.number_input("Screen Time (Hrs/Day)", 0, 24, 8)
                scr_dist = st.number_input("Screen Distance (cm)", 10, 100, 50)
                bright = st.slider("Brightness (%)", 0, 100, 70)
                outdoor = st.number_input("Outdoor (Hrs/Day)", 0, 24, 2)
                night = st.selectbox("Night Mode", ["Always", "Sometimes", "Never"])
            
            submit = st.form_submit_button("🔍 ANALYZE")

        if submit:
            nm_map = {"Always": 2, "Sometimes": 1, "Never": 0}
            features = {
                'age': age, 'exercise_hours': exercise, 'glasses_number': glasses,
                'height_cm': height, 'mental_health_score': mental,
                'night_mode_usage': nm_map[night], 'outdoor_light_exposure_hours': outdoor,
                'screen_brightness_avg': bright, 'screen_distance_cm': scr_dist,
                'screen_time_hours': scr_time
            }
            input_df = pd.DataFrame([features])
            
            if hasattr(model, "feature_names_in_"):
                input_df = input_df[model.feature_names_in_]
            
            result = model.predict(input_df)[0]
            st.markdown(f'<div class="result-box"><h2>Result: {result}</h2></div>', unsafe_allow_html=True)
            
            # Save data to Google Sheets
            if db_connected:
                new_row = pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Age": age, "Result": result}])
                updated_history = pd.concat([df_history, new_row], ignore_index=True)
                conn.update(data=updated_history)
    else:
        st.error("Model file 'eye_health_model.pkl' not found in your GitHub repository.")

# --- PAGE 3: ADMIN ---
elif page == "🔒 Admin Records":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Access Denied.")
    else:
        st.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
        st.write("### Consultation History")
        st.dataframe(df_history, use_container_width=True)
        if not df_history.empty:
            fig = px.pie(df_history, names="Result", hole=0.4, title="Distribution of Diagnoses")
            st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & SOPHISTICATED STYLING ---
st.set_page_config(page_title="Eye AI Consultant", page_icon="👁️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    
    /* SIDEBAR - DIM WHITE TEXT AESTHETIC */
    section[data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    section[data-testid="stSidebar"] * {
        color: #d1d5db !important; 
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%);
        color: white;
        font-weight: bold;
        height: 3.5em;
        border: none;
    }
    
    .result-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #ffffff;
        border-left: 10px solid #3b82f6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        color: #1e3a8a;
    }

    .recommendation-section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
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
    st.markdown("### NAVIGATION")
    page = st.radio("", ["🏠 Home", "🩺 Consultation", "🔒 Admin"])
    st.write("") 
    st.divider()
    st.markdown("⚠️ **Disclaimer:** This AI is a decision-support tool. It is not a clinical diagnosis. Always consult a qualified optometrist.")

# --- PAGE 1: HOME ---
if page == "🏠 Home":
    st.title("👁️ Personal Eye Consultant AI")
    st.write("Professional vision habit analysis powered by Machine Learning.")
    st.markdown("""
    ### How our AI evaluates your vision:
    The model identifies correlations between your physical baseline and digital environment.
    - **Refractive Mapping:** Translates complex data into clear vision categories.
    - **Habit Analysis:** Evaluates the impact of screen distance and brightness.
    - **Personalized Feedback:** Tailored advice based on clinical patterns.
    """)
    st.info("Navigate to **Consultation** to begin.")

# --- PAGE 2: CONSULTATION ---
elif page == "🩺 Consultation":
    st.title("🩺 Vision Assessment")
    model_path = 'eye_health_model.pkl'
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        
        with st.form(key="eye_form"):
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", 0, 110, 25)
                height = st.number_input("Height (cm)", 100, 220, 170)
                glasses = st.number_input("Glasses Power", -20.0, 20.0, 0.0)
                exercise = st.number_input("Weekly Exercise (Hrs)", 0, 40, 5)
                mental = st.slider("Well-being (1-10)", 1, 10, 7)
            with c2:
                scr_time = st.number_input("Daily Screen Time (Hrs)", 0, 24, 8)
                scr_dist = st.number_input("Screen Distance (cm)", 10, 100, 50)
                bright = st.slider("Screen Brightness (%)", 0, 100, 70)
                outdoor = st.number_input("Outdoor Exposure (Hrs)", 0, 24, 2)
                night = st.selectbox("Night Mode Usage", ["Always", "Sometimes", "Never"])
            
            submit = st.form_submit_button("🔍 RUN AI ANALYSIS")

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
            
            prediction = model.predict(input_df)[0]
            
            # --- TRANSLATION MAP ---
            # Mapping numbers to human-readable clinical groups
            result_map = {
                107: "Hyperopic Patterns (Far-Sightedness)",
                65: "Myopic Patterns (Near-Sightedness)",
                0: "Healthy / Normal Vision",
                1: "Mild Digital Eye Strain"
            }
            
            # Use the map, default to "Group X" if number isn't listed
            friendly_result = result_map.get(prediction, f"Refractive Group {prediction}")

            # --- RESULTS SECTION ---
            st.markdown(f'<div class="result-box"><h2>AI Diagnosis: {friendly_result}</h2></div>', unsafe_allow_html=True)
            
            # DOWNLOAD BUTTON
            report_text = f"EYE AI REPORT\nDate: {pd.Timestamp.now()}\nDiagnosis: {friendly_result}\nAge: {age}"
            st.download_button("📥 Download Report", report_text, file_name="Eye_Report.txt")

            st.subheader("📋 Comprehensive Report")
            res_val = friendly_result.lower()
            
            with st.container():
                st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                
                if "myopic" in res_val or "65" in str(prediction):
                    st.error("### 👓 Focus: Myopic Pattern (Near-Sightedness)")
                    st.write("Your profile matches patterns where distant vision is compromised by eye elongation.")
                    st.markdown("""
                    - **Recommendation:** Increase outdoor daylight to 2 hours daily to regulate eye growth.
                    - **Habit:** Reduce continuous near-work; blink consciously to refresh the tear film.
                    """)
                elif "hyperopic" in res_val or "107" in str(prediction):
                    st.warning("### 🔍 Focus: Hyperopic Pattern (Far-Sightedness)")
                    st.write("Your profile suggests your eyes work harder to focus on close objects.")
                    st.markdown("""
                    - **Recommendation:** Increase font sizes on digital devices.
                    - **Habit:** Ensure your workspace has bright, even ambient lighting to reduce strain.
                    """)
                else:
                    st.success("### ✅ Focus: Balanced Vision")
                    st.write("Your habits are currently supporting healthy ocular recovery.")
                    st.markdown("- **Recommendation:** Follow the 20-20-20 rule to prevent future strain.")
                
                st.markdown('</div>', unsafe_allow_html=True)

            if db_connected:
                new_row = pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Age": age, "Result": friendly_result}])
                conn.update(data=pd.concat([df_history, new_row], ignore_index=True))
    else:
        st.error("Model 'eye_health_model.pkl' not found.")

# --- PAGE 3: ADMIN ---
elif page == "🔒 Admin":
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Access Logs"):
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied.")
    else:
        st.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
        st.dataframe(df_history, use_container_width=True)
        if not df_history.empty:
            fig = px.pie(df_history, names="Result", hole=0.4, title="Global Data Overview")
            st.plotly_chart(fig)

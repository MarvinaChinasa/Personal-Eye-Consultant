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
    st.spacer(10)
    st.divider()
    st.markdown("⚠️ **Disclaimer:** This AI is a decision-support tool for educational purposes only. It is not a clinical diagnosis. Always consult a qualified optometrist.")

# --- PAGE 1: HOME ---
if page == "🏠 Home":
    st.title("👁️ Personal Eye Consultant AI")
    st.write("Professional vision habit analysis powered by Machine Learning.")
    
    st.markdown("""
    ### How our AI evaluates your vision:
    The model identifies correlations between your physical baseline and digital environment.
    - **Accommodation Stress:** How hard your lenses work based on screen distance.
    - **Circadian Impact:** How night-mode and brightness affect eye fatigue.
    - **Developmental Factors:** The role of outdoor light in maintaining eye shape.
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
            
            # --- DETAILED AI INTERPRETATION ---
            st.markdown(f'<div class="result-box"><h2>AI Diagnosis: {prediction}</h2></div>', unsafe_allow_html=True)
            
            st.subheader("📋 Comprehensive Report")
            
            res_val = str(prediction).lower()
            
            with st.container():
                st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                
                # 1. HEALTHY / NORMAL
                if any(x in res_val for x in ["good", "normal", "healthy"]):
                    st.success("### ✅ Optimal Vision Balance")
                    st.write("Your metrics indicate that your lifestyle habits effectively compensate for digital strain.")
                    st.markdown("""
                    **Detailed Recommendations:**
                    - **Maintain Ergonomics:** Continue keeping screens at least 50cm away.
                    - **Sunlight Intake:** Your outdoor light exposure is helping regulate your eye's dopamine levels, which prevents myopia.
                    - **Preventative Care:** Follow the **20-20-20 rule** to ensure your ciliary muscles remain flexible.
                    """)

                # 2. STRAIN / FATIGUE
                elif any(x in res_val for x in ["strain", "fatigue", "des"]):
                    st.warning("### ⚠️ Digital Eye Strain (DES) Detected")
                    st.write("The AI has flagged a high correlation between your screen time and insufficient recovery time.")
                    st.markdown("""
                    **Detailed Recommendations:**
                    - **Immediate Change:** Lower your screen brightness to match the room lighting.
                    - **Night Mode:** Enable blue-light filters 2 hours before sleep to reduce retinal stress.
                    - **Distance:** Your screen distance may be too close. Aim for an arm's length (approx. 60cm).
                    """)

                # 3. MYOPIA / NEARSIGHTEDNESS
                elif "myopia" in res_val:
                    st.error("### 👓 Potential Myopic Progression")
                    st.write("The model suggests your habits (low outdoor light + high close-up work) are patterns seen in myopic progression.")
                    st.markdown("""
                    **Detailed Recommendations:**
                    - **Outdoor Time:** Aim for at least 90-120 minutes of outdoor daylight to slow axial eye growth.
                    - **Focus Variety:** Spend time looking at distant objects (clouds, trees) to relax the lens.
                    - **Professional Exam:** This result strongly suggests a need for a refraction test.
                    """)

                # 4. HYPEROPIA / FAR
                elif "hyperopia" in res_val:
                    st.info("### 🔍 Hyperopic Patterns")
                    st.write("Your profile matches patterns where the eye must work harder to focus on close objects.")
                    st.markdown("""
                    **Detailed Recommendations:**
                    - **Workplace Lighting:** Ensure your task area is brightly and evenly lit.
                    - **Font Size:** Increase text size on digital devices to reduce the strain of accommodation.
                    """)

                # 5. CATCH-ALL / UNIQUE
                else:
                    st.info("### ℹ️ Diverse Habit Profile")
                    st.write("Your inputs show a unique combination of factors that don't fit a singular category.")
                    st.markdown("""
                    **General Recommendations:**
                    - Ensure your mental well-being and exercise remain high, as physical health impacts ocular blood flow.
                    - Keep a diary of any headaches or blurred vision to share with your doctor.
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)

            if db_connected:
                new_row = pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Age": age, "Result": prediction}])
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
    else:
        st.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
        st.dataframe(df_history, use_container_width=True)
        if not df_history.empty:
            fig = px.pie(df_history, names="Result", hole=0.4, title="Global Assessment Distribution")
            st.plotly_chart(fig)

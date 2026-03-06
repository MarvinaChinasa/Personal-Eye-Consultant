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
    
    /* SIDEBAR - DIM WHITE TEXT FOR BETTER AESTHETICS */
    section[data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    section[data-testid="stSidebar"] * {
        color: #d1d5db !important; /* Dimmed light grey/white */
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
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        border-left: 10px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .recommendation-card {
        background-color: #f9fafb;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
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

# --- PAGE 1: HOME ---
if page == "🏠 Home":
    st.title("👁️ Personal Eye Consultant AI")
    st.write("Professional vision habit analysis powered by Machine Learning.")
    
    

[Image of the anatomy of the human eye showing retina, lens and cornea]

    
    st.markdown("""
    ### System Capabilities
    - **Risk Mapping:** Analyzes 10 environmental and physical variables.
    - **Habit Analysis:** Evaluates digital vs. natural light exposure.
    - **Personalized Feedback:** Get tailored advice based on your specific AI result.
    """)

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
            
            submit = st.form_submit_button("🔍 RUN ANALYSIS")

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
            
            # --- AI INTERPRETATION LOGIC ---
            st.markdown(f'<div class="result-box"><h3>AI Result: {prediction}</h3></div>', unsafe_allow_html=True)
            
            st.subheader("📋 Interpretation & Recommendations")
            
            # Create a card for recommendations
            with st.container():
                if "Good" in str(prediction) or "Normal" in str(prediction):
                    st.success("**What this means:** Your current lifestyle and physical metrics suggest a balanced eye environment.")
                    st.markdown("""
                    - **Recommendation 1:** Maintain the 20-20-20 rule during long screen sessions.
                    - **Recommendation 2:** Continue getting at least 2 hours of natural light daily.
                    """)
                elif "Strain" in str(prediction) or "Risk" in str(prediction):
                    st.warning("**What this means:** The AI has detected patterns commonly associated with digital eye fatigue or vision strain.")
                    st.markdown("""
                    - **Recommendation 1:** Increase your screen distance to at least 50cm.
                    - **Recommendation 2:** Use 'Night Mode' consistently after sunset to reduce blue light.
                    - **Recommendation 3:** **Schedule a professional eye exam** to verify these findings.
                    """)
                else:
                    st.info("**What this means:** Based on your inputs, your profile shows unique characteristics.")
                    st.markdown("- **Recommendation:** Monitor for any signs of blurred vision or headaches and consult an optometrist.")

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

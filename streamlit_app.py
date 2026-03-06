import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & HIGH-CONTRAST STYLING ---
st.set_page_config(page_title="Eye AI | Consultant", page_icon="👁️", layout="wide")

# Custom CSS for high readability and professional aesthetics
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f0f4f8; }
    
    /* SIDEBAR NAVIGATION - HIGH CONTRAST ELECTRIC YELLOW */
    section[data-testid="stSidebar"] { 
        background-color: #1e3a8a !important; 
    }
    
    /* Force all text in sidebar to Electric Yellow */
    section[data-testid="stSidebar"] .st-bd, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #fbbf24 !important; 
        font-size: 18px !important;
        font-weight: 800 !important;
    }

    /* Buttons - Gradient Style */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%);
        color: white;
        font-weight: bold;
        border: none;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; transform: scale(1.02); }
    
    /* Metric Cards */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    
    /* Result Box */
    .result-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #ecfdf5;
        border: 2px solid #10b981;
        color: #065f46;
        text-align: center;
        margin-top: 20px;
    }
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
    st.markdown("### VISION MENU")
    page = st.radio("", ["🏠 Welcome", "🩺 AI Consultation", "🔒 Admin Records"])
    st.divider()
    st.caption("Public Eye Health Portal v2.1")

# --- PAGE 1: WELCOME (PUBLIC) ---
if page == "🏠 Welcome":
    st.title("👁️ Personal Eye Consultant AI")
    st.subheader("Your Vision, Analyzed by Intelligence")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><b>🔬 Precision AI</b><br>Pattern matching based on clinical vision metrics.</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><b>⚡ Instant</b><br>Get your habit-based assessment in seconds.</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><b>🔒 Secure</b><br>Your personal inputs are not stored publicly.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### **Understanding the Science**")
    st.write("This tool evaluates the balance between your digital strain and your eyes' recovery environment.")
    
    

    c1, c2 = st.columns(2)
    with c1:
        st.info("**Digital Hygiene:** Factors like screen distance and brightness determine how hard your ciliary muscles are working.")
    with c2:
        st.success("**Recovery Environment:** Outdoor light exposure helps regulate eye growth and prevents fatigue.")
    
    st.write("Select **AI Consultation** from the sidebar to begin.")

# --- PAGE 2: AI CONSULTATION (PUBLIC) ---
elif page == "🩺 AI Consultation":
    st.title("🩺 AI-Powered Assessment")
    st.write("Please enter your current habits and physical metrics below.")
    
    model_path = 'eye_health_model.pkl'
    model_ready = False
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            model_ready = True
        except: st.error("⚠️ Failed to load AI model.")
    
    with st.form(key="eye_v2_form"):
        st.markdown("#### **1. Personal Profile**")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 0, 110, 25)
            height_cm = st.number_input("Height (cm)", 100, 220, 170)
            glasses = st.number_input("Glasses Power (Diopters)", -20.0, 20.0, 0.0)
        with col2:
            exercise = st.number_input("Weekly Exercise (Hours)", 0, 40, 5)
            mental = st.slider("Well-being Score (1-10)", 1, 10, 7)
            
        st.markdown("#### **2. Digital Habits**")
        col3, col4 = st.columns(2)
        with col3:
            scr_time = st.number_input("Daily Screen Time (Hours)", 0, 24, 8)
            scr_dist = st.number_input("Screen Distance (cm)", 10, 100, 50)
            bright = st.slider("Typical Screen Brightness (%)", 0, 100, 70)
        with col4:
            outdoor = st.number_input("Daily Outdoor Light (Hours)", 0, 24, 2)
            night = st.selectbox("Night Mode Usage", ["Always", "Sometimes", "Never"])
            nm_map = {"Always": 2, "Sometimes": 1, "Never": 0}
            nm_val = nm_map[night]
            
        submit = st.form_submit_button("🔍 ANALYZE MY VISION")

    if submit and model_ready:
        try:
            # Auto-align features
            features = {
                'age': age, 'exercise_hours': exercise, 'glasses_number': glasses,
                'height_cm': height_cm, 'mental_health_score': mental,
                'night_mode_usage': nm_val, 'outdoor_light_exposure_hours': outdoor,
                'screen_brightness_avg': bright, 'screen_distance_cm': scr_dist,
                'screen_time_hours': scr_time
            }
            input_df = pd.DataFrame([features])
            if hasattr(model, "feature_names_in_

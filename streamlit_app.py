import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & ADVANCED STYLING ---
st.set_page_config(page_title="Eye AI | Consultant", page_icon="👁️", layout="wide")

# Custom CSS for Colors, Gradients, and Card Effects
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f0f4f8; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] label { color: white !important; }
    
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
    div[data-testid="stMetricValue"] { color: #1e3a8a; font-weight: bold; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3b82f6;
    }
    
    /* Result Box */
    .result-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #ecfdf5;
        border: 2px solid #10b981;
        color: #065f46;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_history = conn.read(ttl=0)
    db_connected = True
except Exception:
    db_connected = False
    df_history = pd.DataFrame()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2850/2850935.png", width=100)
    st.markdown("## **Vision Navigation**")
    page = st.radio("Go to:", ["🏠 Welcome Home", "🩺 AI Consultation", "🔒 Admin Portal"])
    st.divider()
    st.caption("v2.0 | Powered by Machine Learning")

# --- PAGE 1: WELCOME (PUBLIC) ---
if page == "🏠 Welcome Home":
    st.title("👁️ Personal Eye Consultant AI")
    st.subheader("Smart Analysis for the Digital Age")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><b>🔬 Precision</b><br>Trained on clinical datasets</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><b>⚡ Speed</b><br>Instant result in <1 sec</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><b>🌍 Access</b><br>Free for everyone</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### **How it Works**")
    
    # Explaining the Result logic to the user
    st.write("""
    Our AI analyzes **10 key data points** to evaluate your eye health. 
    It doesn't just look at how well you see; it looks at **how you live**.
    """)
    
    
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("**Digital Habits:** We track screen time, distance, and brightness to calculate potential digital eye strain (DES).")
    with c2:
        st.success("**Environmental Factors:** Outdoor light and exercise levels are factored in to see how your eyes recover.")

# --- PAGE 2: AI CONSULTATION ---
elif page == "🩺 AI Consultation":
    st.title("🩺 Smart Assessment")
    st.write("Complete the form below to receive your AI-generated suggestion.")
    
    model_path = 'eye_health_model.pkl'
    model_ready = False
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            model_ready = True
        except: st.error("Model Error")
    
    with st.form(key="eye_v2_form"):
        st.markdown("#### **Personal & Physical**")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 0, 110, 25)
            height_cm = st.number_input("Height (cm)", 100, 220, 170)
            glasses = st.number_input("Glasses Power (Diopters)", -20.0, 20.0, 0.0)
        with col2:
            exercise = st.number_input("Exercise (Hrs/Week)", 0, 40, 5)
            mental = st.slider("Well-being Score", 1, 10, 7)
            
        st.markdown("#### **Digital Habits**")
        col3, col4 = st.columns(2)
        with col3:
            scr_time = st.number_input("Screen Time (Hrs/Day)", 0, 24, 8)
            scr_dist = st.number_input("Screen Distance (cm)", 10, 100, 50)
            bright = st.slider("Screen Brightness (%)", 0, 100, 70)
        with col4:
            outdoor = st.number_input("Outdoor Light (Hrs/Day)", 0, 24, 2)
            night = st.selectbox("Night Mode Usage", ["Always", "Sometimes", "Never"])
            nm_map = {"Always": 2, "Sometimes": 1, "Never": 0}
            nm_val = nm_map[night]
            
        submit = st.form_submit_button("🔍 ANALYZE MY VISION")

    if submit and model_ready:
        try:
            # Data Alignment
            features = {
                'age': age, 'exercise_hours': exercise, 'glasses_number': glasses,
                'height_cm': height_cm, 'mental_health_score': mental,
                'night_mode_usage': nm_val, 'outdoor_light_exposure_hours': outdoor,
                'screen_brightness_avg': bright, 'screen_distance_cm': scr_dist,
                'screen_time_hours': scr_time
            }
            input_df = pd.DataFrame([features])
            if hasattr(model, "feature_names_in_"):
                input_df = input_df[model.feature_names_in_]
            
            result = model.predict(input_df)[0]
            
            st.markdown("---")
            st.markdown(f'<div class="result-box"><h2>Analysis: {result}</h2></div>', unsafe_allow_html=True)
            
            # Actionable advice based on result keywords
            if "Strain" in result or "High" in result:
                st.warning("**Recommendation:** High probability of eye fatigue detected. Please follow the 20-20-20 rule and consider a professional exam.")
            else:
                st.success("**Recommendation:** Your metrics look healthy! Continue maintaining good digital hygiene.")

            # Download Report
            report = f"EYE CONSULTANT REPORT\nResult: {result}\nDate: {pd.Timestamp.now()}"
            st.download_button("📥 Download Official Report", report, file_name="Eye_Analysis.txt")

            if db_connected:
                new_row = pd.DataFrame([{"Timestamp": pd.Timestamp.now(), "Age": age, "Result": result}])
                conn.update(data=pd.concat([df_history, new_row], ignore_index=True))
                
        except Exception as e:
            st.error(f"Error: {e}")

# --- PAGE 3: ADMIN ---
elif page == "🔒 Admin Portal":
    st.title("🔒 Security Access")
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        passwd = st.text_input("Admin Password", type="password")
        if st.button("Unlock Database"):
            if passwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else: st.error("Access Denied.")
    else:
        if st.button("Logout"):
            st.session_state["admin_logged_in"] = False
            st.rerun()
        
        st.write("### Data Trends")
        st.dataframe(df_history, use_container_width=True)
        if not df_history.empty:
            fig = px.bar(df_history, x="Result", color="Result", title="Consultation Outcomes")
            st.plotly_chart(fig, use_container_width=True)

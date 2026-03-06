import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
from st_gsheets_connection import GSheetsConnection

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="EyeScan AI", page_icon="👁️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & MODEL LOADING ---
@st.cache_resource
def load_assets():
    model = joblib.load('eye_health_model.pkl')
    df_baseline = pd.read_csv('eye_score.csv')
    return model, df_baseline

try:
    model, df_baseline = load_assets()
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Setup Error: Check your files (csv/pkl) and GSheets connection.")
    st.stop()

# --- 3. SIDEBAR & TUTORIAL ---
with st.sidebar:
    st.title("Settings")
    st.markdown("### 🚦 Quick Start Guide")
    st.caption("1. Adjust sliders to match your day.\n2. Click 'Calculate' to see your score.\n3. Compare with the global average.")
    
    st.divider()
    age = st.slider("Age", 5, 85, 25)
    screen_time = st.slider("Daily Screen Time (Hrs)", 0.0, 16.0, 6.0)
    brightness = st.slider("Screen Brightness (%)", 0, 100, 50)
    outdoor_time = st.slider("Outdoor Light (Hrs)", 0.0, 5.0, 1.5)
    exercise = st.slider("Weekly Exercise (Hrs)", 0.0, 20.0, 5.0)
    mental_health = st.slider("Mental Well-being", 0, 100, 75)
    distance = st.slider("Screen Distance (cm)", 20, 100, 50)
    
    st.divider()
    admin_access = st.checkbox("🔑 Admin Dashboard")
    if admin_access:
        pwd = st.text_input("Admin Password", type="password")
        is_admin = (pwd == st.secrets.get("ADMIN_PASSWORD", "admin123"))
    else:
        is_admin = False

# --- 4. MAIN INTERFACE ---
st.title("👁️ EyeScan AI: Visual Health Analytics")

with st.expander("❓ How does this AI work?"):
    st.write("""
    This app uses a **Random Forest** model to predict eye health based on environmental and lifestyle stressors.
    It analyzes the correlation between screen distance, light exposure, and digital fatigue.
    """)
    

# --- 5. PREDICTION & LOGGING ---
features = ['exercise_hours', 'mental_health_score', 'screen_time_hours', 
            'screen_brightness_avg', 'age', 'height_cm', 
            'outdoor_light_exposure_hours', 'night_mode_usage', 
            'screen_distance_cm', 'glasses_number']

input_df = pd.DataFrame([[exercise, mental_health, screen_time, brightness, 
                          age, 170, outdoor_time, 50, distance, 0]], columns=features)

if st.button("Calculate My Eye Health Score", type="primary"):
    prediction = model.predict(input_df)[0]
    avg_score = df_baseline['eye_health_score'].mean()
    percentile = (df_baseline['eye_health_score'] < prediction).mean() * 100
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Your Score", f"{prediction:.1f}/100", f"{prediction-avg_score:.1f} vs Avg")
    col2.metric("Status", "Healthy" if prediction > 70 else "At Risk")
    col3.metric("Global Rank", f"Top {100-percentile:.1f}%")

    if prediction > 80: st.balloons()

    # --- SOCIAL PROOF CHART ---
    st.subheader("📊 Where do you stand?")
    fig = px.scatter(df_baseline.sample(500), x='screen_time_hours', y='eye_health_score', 
                     color='eye_health_score', color_continuous_scale='RdYlGn', opacity=0.4)
    fig.add_trace(go.Scatter(x=[screen_time], y=[prediction], mode='markers+text',
                             text=["YOU"], textposition="top center",
                             marker=dict(color='black', size=15, symbol='star')))
    st.plotly_chart(fig, use_container_width=True)

    # --- DATA LOGGING ---
    try:
        new_row = pd.DataFrame([{"timestamp": pd.Timestamp.now(), "age": age, "score": prediction}])
        existing_logs = conn.read(worksheet="Sheet1")
        updated_logs = pd.concat([existing_logs, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_logs)
    except:
        st.warning("Note: Result not saved to cloud (Check GSheets secrets).")

# --- 6. ADMIN DASHBOARD ---
if is_admin:
    st.divider()
    st.header("🔐 Admin Dashboard")
    try:
        logs = conn.read(worksheet="Sheet1")
        st.write(f"Total Users Logged: {len(logs)}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.histogram(logs, x="score", title="User Score Distribution"))
        with c2:
            st.dataframe(logs.tail(10))
    except:
        st.error("Could not load logs from Google Sheets.")

# --- 7. DOWNLOAD REPORT ---
    report = f"EyeScan AI Report\nScore: {prediction:.1f}\nPercentile: {100-percentile:.1f}%"
    st.download_button("📥 Download Report", report, file_name="EyeReport.txt")


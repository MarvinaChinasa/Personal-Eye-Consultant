import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

# --- PAGE CONFIG ---
st.set_page_config(page_title="EyeScan AI", page_icon="👁️", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA & MODEL ---
@st.cache_data
def load_assets():
    # Load your dataset and model
    df = pd.read_csv('eye_score.csv')
    model = joblib.load('eye_health_model.pkl')
    return df, model

try:
    df, model = load_assets()
except Exception as e:
    st.error("Make sure 'eye_score.csv' and 'eye_health_model.pkl' are in the same folder!")
    st.stop()

# --- HEADER ---
st.title("👁️ EyeScan AI: Visual Health Analytics")
st.markdown("---")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Your Lifestyle Profile")
    st.info("Adjust the sliders to see your real-time eye health prediction.")
    
    age = st.slider("Age", 5, 85, 25)
    screen_time = st.slider("Daily Screen Time (Hours)", 0.0, 16.0, 6.0)
    brightness = st.slider("Avg Screen Brightness (%)", 0, 100, 50)
    outdoor_time = st.slider("Outdoor Light (Hours)", 0.0, 5.0, 1.5)
    exercise = st.slider("Weekly Exercise (Hours)", 0.0, 20.0, 5.0)
    mental_health = st.slider("Mental Well-being (0-100)", 0, 100, 75)
    distance = st.slider("Screen Distance (cm)", 20, 100, 50)
    
    # Matching the exact features expected by your model
    features = ['exercise_hours', 'mental_health_score', 'screen_time_hours', 
                'screen_brightness_avg', 'age', 'height_cm', 
                'outdoor_light_exposure_hours', 'night_mode_usage', 
                'screen_distance_cm', 'glasses_number']
    
    # Creating a temporary input dataframe
    input_data = pd.DataFrame([[exercise, mental_health, screen_time, brightness, 
                               age, 170, outdoor_time, 50, distance, 0]], columns=features)

# --- PREDICTION ---
prediction = model.predict(input_data)[0]
avg_score = df['eye_health_score'].mean()
percentile = (df['eye_health_score'] < prediction).mean() * 100

# --- DASHBOARD LAYOUT ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Your Eye Health Score", value=f"{prediction:.1f}/100", delta=f"{prediction-avg_score:.1f} vs Avg")

with col2:
    status = "Healthy" if prediction > 70 else "At Risk"
    st.metric(label="Status", value=status)

with col3:
    st.metric(label="Global Percentile", value=f"Top {100-percentile:.1f}%")

st.markdown("### 📊 Social Proof & Data Correlation")

# Create the Correlation Chart
# We sample the data so the chart stays fast and responsive
chart_data = df.sample(n=min(1000, len(df)))

fig = px.scatter(
    chart_data, 
    x='screen_time_hours', 
    y='eye_health_score',
    color='eye_health_score',
    color_continuous_scale='RdYlGn',
    labels={'screen_time_hours': 'Daily Screen Time (Hrs)', 'eye_health_score': 'Score'},
    title="Screen Time vs. Eye Health (Global Trends)",
    opacity=0.4
)

# Add the specific "YOU" marker
fig.add_trace(go.Scatter(
    x=[screen_time], 
    y=[prediction],
    mode='markers+text',
    name='YOU',
    text=['YOU ARE HERE'],
    textposition='top center',
    marker=dict(color='black', size=15, symbol='star', line=dict(width=2, color='white'))
))

st.plotly_chart(fig, use_container_width=True)

# --- DYNAMIC ADVICE ---
st.markdown("### 💡 AI Recommendations")
adv_col1, adv_col2 = st.columns(2)

with adv_col1:
    if screen_time > 8:
        st.warning(f"**Reduce Screen Fatigue:** You spend {screen_time} hours on screens. Try the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds.")
    else:
        st.success("**Great Balance:** Your screen time is within a healthy range for digital workers.")

with adv_col2:
    if outdoor_time < 1:
        st.error("**Low Natural Light:** Increasing outdoor exposure to at least 2 hours can improve your score by roughly 10 points.")
    else:
        st.success("**Natural Light King:** You're getting enough natural light to help regulate eye growth and circadian rhythms.")
# --- DOWNLOAD REPORT SECTION ---
st.markdown("---")
st.subheader("📄 Save Your Results")

# Create the report content
report_text = f"""
EYESCAN AI - PERSONAL VISION REPORT
-----------------------------------
Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}
Your Eye Health Score: {prediction:.2f}/100
Global Average: {avg_score:.2f}/100
Percentile: Top {100-percentile:.1f}%

LIFESTYLE SUMMARY:
- Age: {age}
- Daily Screen Time: {screen_time} hours
- Outdoor Exposure: {outdoor_time} hours
- Screen Distance: {distance} cm

AI RECOMMENDATIONS:
1. Screen Habits: {"Great balance!" if screen_time < 8 else "Reduce screen fatigue using the 20-20-20 rule."}
2. Light Exposure: {"Perfect outdoor time." if outdoor_time > 1.5 else "Try to get 1 more hour of natural light."}
-----------------------------------
Disclaimer: This is an AI prediction, not medical advice.
"""

# Add the download button
st.download_button(
    label="📥 Download My Eye Health Report",
    data=report_text,
    file_name=f"EyeScan_Report_{age}.txt",
    mime="text/plain"
)

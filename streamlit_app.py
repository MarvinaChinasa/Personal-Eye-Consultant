import streamlit as st
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import os

# 1. Page Configuration
st.set_page_config(page_title="Eye Health Predictor", page_icon="👁️", layout="wide")

# 2. Auto-Train Logic: This creates the model file if it is missing
def load_data_and_train():
    if not os.path.exists('eye_health_model.pkl'):
        # Ensure eye_score.csv is also uploaded to your GitHub
        df = pd.read_csv('eye_score.csv')
        X = df.drop(columns=['Unnamed: 0', 'id', 'eye_health_score'])
        y = df['eye_health_score']
        model = LinearRegression().fit(X, y)
        joblib.dump(model, 'eye_health_model.pkl')
    return joblib.load('eye_health_model.pkl')

model = load_data_and_train()

# 3. User Interface
st.title("👁️ Personal Eye Health Consultant")
st.markdown("Analyze your digital habits to predict eye health scores and receive expert advice.")

st.sidebar.header("📊 Your Daily Habits")

def get_user_inputs():
    age = st.sidebar.slider("Age", 5, 80, 30)
    screen_time = st.sidebar.slider("Daily Screen Time (Hours)", 0.0, 16.0, 6.0)
    outdoor_time = st.sidebar.slider("Outdoor Light (Hours)", 0.0, 5.0, 1.0)
    exercise = st.sidebar.slider("Weekly Exercise (Hours)", 0.0, 14.0, 3.0)
    brightness = st.sidebar.slider("Screen Brightness (%)", 0, 100, 50)
    distance = st.sidebar.slider("Screen Distance (cm)", 20, 80, 50)
    night_mode = st.sidebar.slider("Night Mode Usage (%)", 0, 100, 50)
    mental_health = st.sidebar.slider("Mental Health Score", 0, 100, 70)
    height = st.sidebar.number_input("Height (cm)", 100, 220, 170)
    glasses = st.sidebar.selectbox("Number of Glasses", [0, 1, 2, 3])
    
    return pd.DataFrame({
        'exercise_hours': [exercise], 'mental_health_score': [mental_health],
        'screen_time_hours': [screen_time], 'screen_brightness_avg': [brightness],
        'age': [age], 'height_cm': [height],
        'outdoor_light_exposure_hours': [outdoor_time], 'night_mode_usage': [night_mode],
        'screen_distance_cm': [distance], 'glasses_number': [glasses]
    })

input_df = get_user_inputs()

if st.button("Generate Health Report"):
    prediction = model.predict(input_df)[0]
    
    st.divider()
    st.metric(label="Predicted Eye Health Score", value=f"{prediction:.1f} / 100")
    
    st.subheader("💡 Expert Recommendations")
    if input_df['screen_time_hours'][0] > 6:
        st.warning("**20-20-20 Rule:** Every 20 mins, look 20 feet away for 20 secs.")
    if input_df['outdoor_light_exposure_hours'][0] < 2:
        st.write("☀️ **Increase Outdoor Time:** Natural light protects your vision.")
    if input_df['screen_distance_cm'][0] < 45:
        st.write("📏 **Distance:** Move your screen to at least 50cm away.")

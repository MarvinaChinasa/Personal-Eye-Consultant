import streamlit as st
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import os

# --- NEW AUTO-TRAIN LOGIC ---
def ensure_model_exists():
    if not os.path.exists('eye_health_model.pkl'):
        # If model is missing, train it on the fly using the CSV
        df = pd.read_csv('eye_score.csv')
        X = df.drop(columns=['Unnamed: 0', 'id', 'eye_health_score'])
        y = df['eye_health_score']
        model = LinearRegression().fit(X, y)
        joblib.dump(model, 'eye_health_model.pkl')

ensure_model_exists()
# ----------------------------

@st.cache_resource
def load_model():
    return joblib.load('eye_health_model.pkl')

model = load_model()
except:
    st.error("Model file not found. Please ensure 'eye_health_model.pkl' is in the same directory.")

st.title("👁️ Personal Eye Health Consultant")
st.markdown("This AI-powered tool predicts your eye health score and provides personalized medical-grade advice based on your digital habits.")

# Sidebar for User Inputs
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
    glasses = st.sidebar.selectbox("Number of Glasses/Prescriptions", [0, 1, 2, 3])
    
    data = {
        'exercise_hours': exercise,
        'mental_health_score': mental_health,
        'screen_time_hours': screen_time,
        'screen_brightness_avg': brightness,
        'age': age,
        'height_cm': height,
        'outdoor_light_exposure_hours': outdoor_time,
        'night_mode_usage': night_mode,
        'screen_distance_cm': distance,
        'glasses_number': glasses
    }
    return pd.DataFrame(data, index=[0])

input_df = get_user_inputs()

if st.button("Generate Health Report"):
    prediction = model.predict(input_df)[0]
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Predicted Eye Health Score", value=f"{prediction:.1f} / 100")
        st.progress(min(max(int(prediction), 0), 100))
        
    with col2:
        if prediction > 75:
            st.success("✅ Excellent! Your habits strongly support eye health.")
        elif prediction > 55:
            st.info("⚠️ Moderate Risk. Small lifestyle changes can help.")
        else:
            st.error("🚨 High Risk. Immediate changes to screen habits recommended.")

    st.subheader("💡 Expert Personalized Recommendations")
    
    if input_df['screen_time_hours'][0] > 6:
        st.warning("**The 20-20-20 Rule:** Every 20 minutes, look at something 20 feet away for 20 seconds.")
    
    if input_df['outdoor_light_exposure_hours'][0] < 2:
        st.write("☀️ **Increase Outdoor Time:** Aim for 2 hours daily to significantly boost your score.")
    
    if input_df['screen_brightness_avg'][0] > 75:
        st.write("🌙 **Dim the Lights:** Match screen brightness to ambient light to reduce strain.")
    
    if input_df['screen_distance_cm'][0] < 45:

        st.write("📏 **Distance Check:** Sit an arm's length (50-70 cm) away from your screen.")

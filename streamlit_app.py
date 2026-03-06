import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="Personal Eye Consultant",
    page_icon="👁️",
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007BFF; color: white; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY CHECK ---
def check_password():
    """Returns True if the user had the correct password in Secrets."""
    if "ADMIN_PASSWORD" not in st.secrets:
        st.error("Configuration Error: 'ADMIN_PASSWORD' not found in Streamlit Secrets.")
        return False

    if "password_correct" not in st.session_state:
        st.title("🔒 Eye Consultant Secure Portal")
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Unlock System"):
            if password == st.secrets["ADMIN_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password")
        return False
    return True

# --- 3. MAIN APP EXECUTION ---
if check_password():
    
    # --- DATABASE CONNECTION ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # We use ttl=0 to ensure we always get the freshest data from your sheet
        df_history = conn.read(ttl=0)
        db_connected = True
    except Exception as e:
        db_connected = False
        db_error = str(e)

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2850/2850935.png", width=100)
        st.title("Main Menu")
        page = st.radio("Navigation", ["Dashboard", "AI Consultation", "History Log"])
        st.divider()
        if st.button("Logout"):
            del st.session_state["password_correct"]
            st.rerun()

    # --- PAGE 1: DASHBOARD ---
    if page == "Dashboard":
        st.title("👁️ Personal Eye Consultant AI")
        st.write("Welcome to the clinical decision support system.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("System Status", "Online" if db_connected else "Offline")
        with col2:
            count = len(df_history) if db_connected else 0
            st.metric("Total Consultations", count)
        with col3:
            st.metric("AI Model", "Ready")

        st.subheader("Instructions")
        st.info("""
        1. Navigate to **AI Consultation** to input patient symptoms.
        2. The AI will analyze the data against the `eye_health_model.pkl.txt` database.
        3. Results are automatically logged to your connected Google Sheet.
        """)

    # --- PAGE 2: AI CONSULTATION ---
    elif page == "AI Consultation":
        st.title("🩺 Symptom Assessment & Prediction")
        
        # Load the specific model file
        model_path = 'eye_health_model.pkl.txt'
        
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                model_ready = True
            except:
                st.error("The model file is present but failed to load. Check format.")
                model_ready = False
        else:
            st.warning(f"Model file '{model_path}' not found. Prediction is disabled.")
            model_ready = False

        with st.form("consult_form"):
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", 0, 110, 30)
                gender = st.selectbox("Gender", ["Male", "Female"])
            with c2:
                symptom = st.selectbox("Primary Symptom", ["Blurry Vision", "Redness", "Itching", "Pain", "Dryness"])
                duration = st.slider("Duration (Days)", 1, 30, 2)
            
            submit = st.form_submit_button("🚀 Run AI Diagnosis")

            if submit:
                if model_ready:
                    # Prepare input for the AI (matching the model's training features)
                    # Note: You may need to encode 'symptom' if your model uses numbers
                    input_data = pd.DataFrame([[age, duration]], columns=['Age', 'Duration'])
                    
                    prediction = model.predict(input_data)
                    result = prediction[0]

                    st.markdown("---")
                    st.subheader("AI Recommendation")
                    st.success(f"Assessment: **{result}**")
                    st.warning("⚠️ Disclaimer: This is not a substitute for professional medical advice.")

                    # SAVE TO GOOGLE SHEETS
                    if db_connected:
                        try:
                            # Creating a timestamped entry
                            new_data = pd.DataFrame([{
                                "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                                "Age": age,
                                "Symptom": symptom,
                                "Duration": duration,
                                "Result": result
                            }])
                            # Append to the sheet
                            updated_df = pd.concat([df_history, new_data], ignore_index=True)
                            conn.update(data=updated_df)
                            st.write("✅ Record synced to cloud database.")
                        except Exception as e:
                            st.error(f"Failed to save to sheet: {e}")
                else:
                    st.error("AI Analysis unavailable. Please check model file.")

    # --- PAGE 3: HISTORY LOG ---
    elif page == "History Log":
        st.title("📊 Consultation History")
        if db_connected and not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
            
            # Simple Chart
            if "Symptom" in df_history.columns:
                fig = px.histogram(df_history, x="Symptom", title="Trend of Reported Symptoms")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No records found in the database.")

import streamlit as st
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

st.title("Propagation Prediction ML Model")

# API URL
API_URL = "http://dx.jxqz.org:8080/api/spots?band=10m"

# Function to fetch spots
def fetch_spots():
    try:
        response = requests.get(API_URL, verify=False)
        response.raise_for_status()
        data = response.json()
        return data.get('spots', [])
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

spots = fetch_spots()

if spots:
    df = pd.DataFrame(spots)
    df = df.dropna(subset=['frequency', 'mode'])
    df['frequency'] = df['frequency'].astype(float)
    
    if not df.empty and len(df['mode'].unique()) > 1:
        # Encode modes
        le = LabelEncoder()
        df['mode_encoded'] = le.fit_transform(df['mode'])
        
        # Features and target
        X = df[['frequency']]
        y = df['mode_encoded']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Model
        model = KNeighborsClassifier(n_neighbors=3)
        model.fit(X_train, y_train)
        
        # Predict on test
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        st.write(f"Model Accuracy: {accuracy:.2f}")
        
        # Prediction interface
        st.subheader("Predict Mode for a Frequency")
        freq = st.number_input("Enter frequency (kHz)", min_value=28000.0, max_value=30000.0, value=28500.0)
        if st.button("Predict"):
            pred = model.predict([[freq]])
            predicted_mode = le.inverse_transform(pred)[0]
            st.write(f"Predicted Mode: {predicted_mode}")
    else:
        st.write("Not enough data or modes to train the model.")
else:
    st.write("No spots available.")
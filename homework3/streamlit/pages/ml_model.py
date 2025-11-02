
import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

st.title("DX Band Openness Prediction (LSTM Model)")

# Load example data
csv_path = "../lstm-model/example_lstm_dx_spot_data.csv"
df = pd.read_csv(csv_path, comment="#")

feature_cols = ['total_spots', 'unique_dx_stations', 'unique_spotters', 'spots_10m', 'spots_12m', 'spots_15m', 'spots_10m_fm']
label_options = {
    '10m': 'band_open_10m',
    '12m': 'band_open_12m',
    '15m': 'band_open_15m'
}

band = st.selectbox("Select band to predict", options=list(label_options.keys()), index=0)
label_col = label_options[band]
SEQUENCE_LENGTH = 3

def create_sequences(df, feature_cols, label_col, seq_len):
    X, y = [], []
    for i in range(len(df) - seq_len):
        seq_x = df.iloc[i:i+seq_len][feature_cols].values
        seq_y = df.iloc[i+seq_len][label_col]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

X, y = create_sequences(df, feature_cols, label_col, SEQUENCE_LENGTH)
if len(X) == 0:
    st.warning("Not enough data to train the model.")
else:
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_shape = X_train.shape
    X_test_shape = X_test.shape
    X_train = scaler.fit_transform(X_train.reshape(-1, len(feature_cols))).reshape(X_train_shape)
    X_test = scaler.transform(X_test.reshape(-1, len(feature_cols))).reshape(X_test_shape)

    # Build and train LSTM model
    model = Sequential([
        LSTM(32, input_shape=(SEQUENCE_LENGTH, len(feature_cols))),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=15, batch_size=2, verbose=0)

    # Evaluate
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    st.metric("Test Accuracy", f"{acc:.2f}")

    # Predict next day openness
    st.subheader(f"Predicted Probability {band} is Open (Next Day)")
    if len(X_test) > 0:
        preds = model.predict(X_test)
        st.write("Predictions:", preds.flatten())
        st.write("Ground Truth:", y_test)
    else:
        st.write("Not enough test data for prediction.")
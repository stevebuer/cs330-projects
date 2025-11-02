"""
LSTM training example for DX band openness prediction using example_lstm_dx_spot_data.csv
"""
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Parameters
SEQUENCE_LENGTH = 3  # Number of days in each input sequence
LABEL_BAND = 'band_open_10m'  # Change to 'band_open_12m' or 'band_open_15m' as needed

# Load data
csv_path = '../homework3/example_lstm_dx_spot_data.csv'
df = pd.read_csv(csv_path)

# Features to use
feature_cols = ['total_spots', 'unique_dx_stations', 'unique_spotters', 'spots_10m', 'spots_12m', 'spots_15m', 'spots_10m_fm']

# Prepare sequences and labels
def create_sequences(df, feature_cols, label_col, seq_len):
    X, y = [], []
    for i in range(len(df) - seq_len):
        seq_x = df.iloc[i:i+seq_len][feature_cols].values
        seq_y = df.iloc[i+seq_len][label_col]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

X, y = create_sequences(df, feature_cols, LABEL_BAND, SEQUENCE_LENGTH)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_shape = X_train.shape
X_test_shape = X_test.shape
X_train = scaler.fit_transform(X_train.reshape(-1, len(feature_cols))).reshape(X_train_shape)
X_test = scaler.transform(X_test.reshape(-1, len(feature_cols))).reshape(X_test_shape)

# Build LSTM model
model = Sequential([
    LSTM(32, input_shape=(SEQUENCE_LENGTH, len(feature_cols))),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train
model.fit(X_train, y_train, epochs=30, batch_size=2, validation_data=(X_test, y_test))

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"Test accuracy: {acc:.2f}")

# Predict next day openness
preds = model.predict(X_test)
print("Predictions:", preds.flatten())

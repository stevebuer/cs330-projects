#!/usr/bin/env python3
"""
Simple RNN training example for DX band openness prediction using example_rnn_dx_spot_data.csv

This RNN model is a basic implementation to compare against the LSTM model.
Key differences from LSTM:
- Uses SimpleRNN instead of LSTM layers (fewer parameters, simpler)
- Single RNN layer instead of stacked architecture
- Useful for learning how RNNs compare to LSTMs on the same data
"""
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import sys

# Parameters
SEQUENCE_LENGTH = 3  # Number of days in each input sequence
LABEL_BAND = 'band_open_10m'  # Change to 'band_open_12m' or 'band_open_15m' as needed
EPOCHS = 30
BATCH_SIZE = 2

# Load data
csv_path = os.path.join(os.path.dirname(__file__), 'example_rnn_dx_spot_data.csv')
if not os.path.exists(csv_path):
    print(f"Error: Data file not found at {csv_path}")
    print("Please ensure example_rnn_dx_spot_data.csv exists in this directory")
    sys.exit(1)

try:
    df = pd.read_csv(csv_path, comment='#')
    print(f"✓ Loaded data: {len(df)} records")
except Exception as e:
    print(f"Error loading CSV: {e}")
    sys.exit(1)

# Features to use
feature_cols = ['total_spots', 'unique_dx_stations', 'unique_spotters', 'spots_10m', 
                'spots_12m', 'spots_15m', 'spots_10m_fm']

# Verify required columns exist
missing_cols = [col for col in feature_cols + [LABEL_BAND] if col not in df.columns]
if missing_cols:
    print(f"Error: Missing columns in CSV: {missing_cols}")
    print(f"Available columns: {list(df.columns)}")
    sys.exit(1)

print(f"✓ Using features: {feature_cols}")
print(f"✓ Label column: {LABEL_BAND}")

# Prepare sequences and labels
def create_sequences(df, feature_cols, label_col, seq_len):
    """Create sequences of length seq_len for training"""
    X, y = [], []
    for i in range(len(df) - seq_len):
        seq_x = df.iloc[i:i+seq_len][feature_cols].values
        seq_y = df.iloc[i+seq_len][label_col]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

X, y = create_sequences(df, feature_cols, LABEL_BAND, SEQUENCE_LENGTH)
print(f"✓ Created {len(X)} sequences of length {SEQUENCE_LENGTH}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"✓ Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")

# Scale features
scaler = StandardScaler()
X_train_shape = X_train.shape
X_test_shape = X_test.shape
X_train = scaler.fit_transform(X_train.reshape(-1, len(feature_cols))).reshape(X_train_shape)
X_test = scaler.transform(X_test.reshape(-1, len(feature_cols))).reshape(X_test_shape)
print("✓ Features scaled")

# Build Simple RNN model
print("\n" + "="*60)
print("Building Simple RNN Model")
print("="*60)
print(f"Input shape: (batch_size, {SEQUENCE_LENGTH}, {len(feature_cols)})")
print(f"RNN units: 32 (compared to LSTM: typically more parameters)")
print(f"Output layer: 1 neuron with sigmoid (binary classification)")

model = Sequential([
    SimpleRNN(32, input_shape=(SEQUENCE_LENGTH, len(feature_cols)), activation='relu'),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
print("\nModel summary:")
model.summary()

# Train
print("\n" + "="*60)
print(f"Training for {EPOCHS} epochs with batch size {BATCH_SIZE}")
print("="*60)
history = model.fit(X_train, y_train, 
                   epochs=EPOCHS, 
                   batch_size=BATCH_SIZE, 
                   validation_data=(X_test, y_test),
                   verbose=1)

# Evaluate
print("\n" + "="*60)
print("Model Evaluation")
print("="*60)
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {loss:.4f}")
print(f"Test Accuracy: {acc:.4f}")

# Make predictions
print("\n" + "="*60)
print("Sample Predictions (first 10 test samples)")
print("="*60)
preds = model.predict(X_test[:10], verbose=0)
for i, (pred, true) in enumerate(zip(preds.flatten()[:10], y_test[:10])):
    print(f"Sample {i+1}: Predicted={pred:.4f}, Actual={int(true)}, " + 
          f"{'✓ Correct' if (pred > 0.5) == true else '✗ Wrong'}")

# Save model
model_path = os.path.join(os.path.dirname(__file__), 'rnn_model.h5')
model.save(model_path)
print(f"\n✓ Model saved to {model_path}")

# Training history summary
print("\n" + "="*60)
print("Training Summary")
print("="*60)
print(f"Final training accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
print(f"Final training loss: {history.history['loss'][-1]:.4f}")
print(f"Final validation loss: {history.history['val_loss'][-1]:.4f}")

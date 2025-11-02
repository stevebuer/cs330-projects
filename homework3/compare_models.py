#!/usr/bin/env python3
"""
Compare RNN vs LSTM model performance on the same DX prediction task

This script trains both models on the same data and displays a side-by-side comparison
of their performance metrics, training time, and model complexity.
"""
import os
import sys
import time
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, LSTM, Dense

# Parameters
SEQUENCE_LENGTH = 3
LABEL_BAND = 'band_open_10m'
EPOCHS = 30
BATCH_SIZE = 2

# Paths
rnn_data_path = os.path.join(os.path.dirname(__file__), 'rnn-model', 'example_rnn_dx_spot_data.csv')
lstm_data_path = os.path.join(os.path.dirname(__file__), 'lstm-model', 'example_lstm_dx_spot_data.csv')

def load_and_prepare_data(csv_path):
    """Load data and create sequences"""
    if not os.path.exists(csv_path):
        print(f"Warning: Data file not found at {csv_path}")
        return None, None, None
    
    df = pd.read_csv(csv_path, comment='#')
    feature_cols = ['total_spots', 'unique_dx_stations', 'unique_spotters', 'spots_10m', 
                    'spots_12m', 'spots_15m', 'spots_10m_fm']
    
    def create_sequences(df, feature_cols, label_col, seq_len):
        X, y = [], []
        for i in range(len(df) - seq_len):
            seq_x = df.iloc[i:i+seq_len][feature_cols].values
            seq_y = df.iloc[i+seq_len][label_col]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)
    
    X, y = create_sequences(df, feature_cols, LABEL_BAND, SEQUENCE_LENGTH)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_shape = X_train.shape
    X_test_shape = X_test.shape
    X_train = scaler.fit_transform(X_train.reshape(-1, len(feature_cols))).reshape(X_train_shape)
    X_test = scaler.transform(X_test.reshape(-1, len(feature_cols))).reshape(X_test_shape)
    
    return (X_train, X_test, y_train, y_test), feature_cols, len(df)

def build_rnn_model(seq_len, num_features):
    """Build SimpleRNN model"""
    model = Sequential([
        SimpleRNN(32, input_shape=(seq_len, num_features), activation='relu'),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def build_lstm_model(seq_len, num_features):
    """Build LSTM model"""
    model = Sequential([
        LSTM(32, input_shape=(seq_len, num_features)),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_and_evaluate(model_name, model, X_train, X_test, y_train, y_test):
    """Train model and return metrics"""
    print(f"\n{'='*60}")
    print(f"Training {model_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    history = model.fit(X_train, y_train,
                       epochs=EPOCHS,
                       batch_size=BATCH_SIZE,
                       validation_data=(X_test, y_test),
                       verbose=0)
    training_time = time.time() - start_time
    
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    
    return {
        'model_name': model_name,
        'training_time': training_time,
        'test_loss': loss,
        'test_accuracy': accuracy,
        'final_train_loss': history.history['loss'][-1],
        'final_train_acc': history.history['accuracy'][-1],
        'final_val_loss': history.history['val_loss'][-1],
        'final_val_acc': history.history['val_accuracy'][-1],
        'params': model.count_params()
    }

def main():
    print("RNN vs LSTM Model Comparison")
    print("="*60)
    
    # Load data
    print("\nLoading training data...")
    
    # Try to load from both directories
    data_rnn, features_rnn, records_rnn = load_and_prepare_data(rnn_data_path)
    data_lstm, features_lstm, records_lstm = load_and_prepare_data(lstm_data_path)
    
    # Use whichever data we can load
    if data_rnn is not None:
        data = data_rnn
        features = features_rnn
        records = records_rnn
        print(f"✓ Loaded RNN data: {records} records")
    elif data_lstm is not None:
        data = data_lstm
        features = features_lstm
        records = records_lstm
        print(f"✓ Loaded LSTM data: {records} records")
    else:
        print("Error: Could not load data from either rnn-model or lstm-model directories")
        sys.exit(1)
    
    X_train, X_test, y_train, y_test = data
    num_features = len(features)
    
    print(f"✓ Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"✓ Features: {features}")
    
    # Build and train models
    rnn_model = build_rnn_model(SEQUENCE_LENGTH, num_features)
    lstm_model = build_lstm_model(SEQUENCE_LENGTH, num_features)
    
    print(f"\nRNN Parameters: {rnn_model.count_params()}")
    print(f"LSTM Parameters: {lstm_model.count_params()}")
    
    rnn_metrics = train_and_evaluate("SimpleRNN", rnn_model, X_train, X_test, y_train, y_test)
    lstm_metrics = train_and_evaluate("LSTM", lstm_model, X_train, X_test, y_train, y_test)
    
    # Display comparison
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    print(f"\n{'Metric':<25} {'SimpleRNN':<20} {'LSTM':<20}")
    print("-" * 65)
    print(f"{'Model Parameters':<25} {rnn_metrics['params']:<20} {lstm_metrics['params']:<20}")
    print(f"{'Training Time (sec)':<25} {rnn_metrics['training_time']:<20.2f} {lstm_metrics['training_time']:<20.2f}")
    print(f"{'Test Accuracy':<25} {rnn_metrics['test_accuracy']:<20.4f} {lstm_metrics['test_accuracy']:<20.4f}")
    print(f"{'Test Loss':<25} {rnn_metrics['test_loss']:<20.4f} {lstm_metrics['test_loss']:<20.4f}")
    print(f"{'Final Train Accuracy':<25} {rnn_metrics['final_train_acc']:<20.4f} {lstm_metrics['final_train_acc']:<20.4f}")
    print(f"{'Final Validation Acc':<25} {rnn_metrics['final_val_acc']:<20.4f} {lstm_metrics['final_val_acc']:<20.4f}")
    
    # Analysis
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    
    param_ratio = lstm_metrics['params'] / rnn_metrics['params']
    time_ratio = lstm_metrics['training_time'] / rnn_metrics['training_time']
    acc_diff = lstm_metrics['test_accuracy'] - rnn_metrics['test_accuracy']
    
    print(f"\nLSTM has {param_ratio:.1f}x more parameters than RNN")
    print(f"LSTM training took {time_ratio:.1f}x longer than RNN")
    print(f"Accuracy difference: {acc_diff:+.4f} (LSTM - RNN)")
    
    if acc_diff > 0.02:
        print("→ LSTM shows better accuracy (more than 2% improvement)")
    elif acc_diff < -0.02:
        print("→ RNN shows better accuracy (more than 2% improvement)")
    else:
        print("→ Models perform similarly on this dataset")
    
    print("\nConclusion:")
    if time_ratio > 1.5 and acc_diff < 0.05:
        print("  RNN is a good choice: faster training with comparable accuracy")
    else:
        print("  LSTM may be worth the extra complexity for this task")

if __name__ == "__main__":
    main()

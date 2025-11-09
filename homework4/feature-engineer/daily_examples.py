#!/usr/bin/env python3
"""
Complete examples for daily radio wave propagation analysis.
Demonstrates how to use daily aggregated features with neural networks.
"""

import numpy as np
from daily_extractor import DailyFeatureExtractor


def example_1_extract_daily():
    """Example 1: Extract and view daily features"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Extract Daily Features")
    print("="*70)
    
    extractor = DailyFeatureExtractor()
    
    # Fetch data
    print("\nFetching data...")
    spots = extractor.fetch_data(limit=300)
    if not spots:
        return
    
    # Group by date
    print("Grouping by date...")
    daily_data = extractor.group_by_date(spots)
    
    # Extract daily features
    print("Extracting daily features...")
    daily_features = extractor.extract_daily_features()
    
    # Normalize
    print("Normalizing...")
    normalized = extractor.normalize_features()
    
    # Display
    print(f"\nDaily Feature Summary:")
    print(f"{'Date':<12} {'Freq':>8} {'Bands':>6} {'Spots':>6} {'SigQ':>6} {'Hrs':>4} {'Peak':>5} {'LW%':>5}")
    print("-"*70)
    
    for vec in normalized[:10]:
        date = vec[0]
        freq = vec[1]
        bands = vec[2]
        spots_count = vec[3]
        sigq = vec[4]
        hrs = vec[8]
        peak = vec[9]
        lw_pct = vec[10]
        
        print(f"{date:<12} {freq:>8.4f} {bands:>6.4f} {spots_count:>6.4f} {sigq:>6.4f} {hrs:>4.2f} {peak:>5.1f} {lw_pct:>5.2f}")


def example_2_pytorch_daily_lstm():
    """Example 2: LSTM model for daily propagation forecasting with PyTorch"""
    print("\n" + "="*70)
    print("EXAMPLE 2: PyTorch LSTM for Daily Propagation Forecasting")
    print("="*70)
    
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
    except ImportError:
        print("PyTorch not installed. Install with: pip install torch")
        return
    
    # Extract daily features
    print("\nExtracting daily features...")
    extractor = DailyFeatureExtractor()
    spots = extractor.fetch_data(limit=500)
    if not spots:
        return
    
    extractor.group_by_date(spots)
    daily_features = extractor.extract_daily_features()
    normalized = extractor.normalize_features()
    
    # Prepare data
    X = torch.tensor(
        [[float(v) for v in vec[1:]] for vec in normalized],
        dtype=torch.float32
    )
    
    print(f"Loaded {X.shape[0]} days of data with {X.shape[1]} features each")
    
    # Create sequences (7-day windows)
    seq_len = 7
    if X.shape[0] < seq_len + 1:
        print(f"Need at least {seq_len + 1} days of data, have {X.shape[0]}")
        return
    
    X_seq = []
    y_seq = []
    for i in range(X.shape[0] - seq_len):
        X_seq.append(X[i:i+seq_len])
        y_seq.append(X[i+seq_len, 3])  # Predict signal quality (index 3)
    
    X_seq = torch.stack(X_seq)
    y_seq = torch.tensor(y_seq, dtype=torch.float32).unsqueeze(1)
    
    print(f"Created {X_seq.shape[0]} sequences of length {seq_len}")
    print(f"  X_seq shape: {X_seq.shape} (samples × days × features)")
    print(f"  y_seq shape: {y_seq.shape}")
    
    # Build LSTM model
    class PropagationLSTM(nn.Module):
        def __init__(self):
            super(PropagationLSTM, self).__init__()
            self.lstm1 = nn.LSTM(10, 32, batch_first=True)
            self.dropout1 = nn.Dropout(0.2)
            self.lstm2 = nn.LSTM(32, 16, batch_first=True)
            self.dropout2 = nn.Dropout(0.2)
            self.fc = nn.Linear(16, 1)
        
        def forward(self, x):
            lstm1_out, _ = self.lstm1(x)
            lstm1_out = self.dropout1(lstm1_out)
            lstm2_out, _ = self.lstm2(lstm1_out)
            lstm2_out = self.dropout2(lstm2_out)
            last_output = lstm2_out[:, -1, :]
            output = self.fc(last_output)
            return output
    
    model = PropagationLSTM()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    print(f"\nTraining LSTM model...")
    for epoch in range(50):
        optimizer.zero_grad()
        outputs = model(X_seq)
        loss = criterion(outputs, y_seq)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1:3d}: Loss = {loss.item():.6f}")
    
    print(f"✓ Training complete!")
    
    # Make predictions
    print(f"\nSample Predictions (predict next day's signal quality):")
    with torch.no_grad():
        predictions = model(X_seq)
        for i in range(min(5, len(predictions))):
            actual = y_seq[i, 0].item()
            predicted = predictions[i, 0].item()
            error = abs(actual - predicted)
            print(f"  Day {i+1}: Actual={actual:.4f}, Predicted={predicted:.4f}, Error={error:.4f}")


def example_3_tensorflow_daily_lstm():
    """Example 3: TensorFlow LSTM for daily propagation"""
    print("\n" + "="*70)
    print("EXAMPLE 3: TensorFlow LSTM for Daily Propagation")
    print("="*70)
    
    try:
        import tensorflow as tf
    except ImportError:
        print("TensorFlow not installed. Install with: pip install tensorflow")
        return
    
    # Extract daily features
    print("\nExtracting daily features...")
    extractor = DailyFeatureExtractor()
    spots = extractor.fetch_data(limit=500)
    if not spots:
        return
    
    extractor.group_by_date(spots)
    daily_features = extractor.extract_daily_features()
    normalized = extractor.normalize_features()
    
    # Prepare data
    X = np.array([[float(v) for v in vec[1:]] for vec in normalized])
    dates = np.array([vec[0] for vec in normalized])
    
    print(f"Loaded {X.shape[0]} days with {X.shape[1]} features")
    
    # Create sequences
    seq_len = 7
    if X.shape[0] < seq_len + 1:
        print(f"Need at least {seq_len + 1} days of data")
        return
    
    X_seq = []
    y_seq = []
    for i in range(X.shape[0] - seq_len):
        X_seq.append(X[i:i+seq_len])
        y_seq.append(X[i+seq_len, 3])  # Predict signal quality
    
    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)
    
    print(f"Created {X_seq.shape[0]} sequences")
    
    # Build model
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(32, input_shape=(seq_len, 10), return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(16),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    print(f"\nTraining...")
    history = model.fit(
        X_seq, y_seq,
        epochs=50,
        batch_size=4,
        verbose=0
    )
    
    final_loss = history.history['loss'][-1]
    final_mae = history.history['mae'][-1]
    
    print(f"✓ Training complete!")
    print(f"  Final Loss: {final_loss:.6f}")
    print(f"  Final MAE: {final_mae:.6f}")
    
    # Predictions
    print(f"\nSample Predictions:")
    predictions = model.predict(X_seq[:5], verbose=0)
    for i in range(5):
        print(f"  Day {i+1}: Actual={y_seq[i]:.4f}, Predicted={predictions[i, 0]:.4f}")


def example_4_clustering_propagation_days():
    """Example 4: Cluster similar propagation days"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Clustering Similar Propagation Days")
    print("="*70)
    
    try:
        from sklearn.cluster import KMeans
    except ImportError:
        print("Scikit-learn not installed. Install with: pip install scikit-learn")
        return
    
    # Extract daily features
    print("\nExtracting daily features...")
    extractor = DailyFeatureExtractor()
    spots = extractor.fetch_data(limit=400)
    if not spots:
        return
    
    extractor.group_by_date(spots)
    daily_features = extractor.extract_daily_features()
    normalized = extractor.normalize_features()
    
    # Prepare data
    dates = [vec[0] for vec in normalized]
    X = np.array([[float(v) for v in vec[1:]] for vec in normalized])
    
    print(f"Loaded {len(dates)} days")
    
    # Cluster
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    
    print(f"\nClustered into {n_clusters} propagation patterns:")
    print("-"*70)
    
    for cluster_id in range(n_clusters):
        cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]
        cluster_dates = [dates[i] for i in cluster_indices]
        
        print(f"\nCluster {cluster_id} ({len(cluster_dates)} days):")
        print(f"  Sample dates: {', '.join(cluster_dates[:3])}")
        if len(cluster_dates) > 3:
            print(f"  ... and {len(cluster_dates) - 3} more")
        
        # Show cluster characteristics
        cluster_data = X[cluster_indices]
        print(f"  Avg frequency: {cluster_data[:, 0].mean():.4f}")
        print(f"  Avg num bands: {cluster_data[:, 1].mean():.2f}")
        print(f"  Avg activity: {cluster_data[:, 2].mean():.4f}")
        print(f"  Avg signal quality: {cluster_data[:, 3].mean():.4f}")
        print(f"  Peak hour: {cluster_data[:, 8].mean():.1f}")


def example_5_daily_statistics():
    """Example 5: Detailed daily statistics"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Daily Propagation Statistics")
    print("="*70)
    
    # Extract daily features
    print("\nExtracting daily features...")
    extractor = DailyFeatureExtractor()
    spots = extractor.fetch_data(limit=300)
    if not spots:
        return
    
    extractor.group_by_date(spots)
    daily_features = extractor.extract_daily_features()
    normalized = extractor.normalize_features()
    
    # Prepare data
    X = np.array([[float(v) for v in vec[1:]] for vec in normalized])
    
    feature_names = [
        "avg_frequency_mhz",
        "num_bands_active",
        "total_spots",
        "avg_signal_quality",
        "signal_quality_std",
        "cw_percentage",
        "ssb_percentage",
        "activity_hours_count",
        "peak_hour",
        "40m_band_percentage"
    ]
    
    print(f"\nDaily Feature Statistics (normalized [0, 1]):")
    print("-"*70)
    print(f"{'Feature':<30} {'Mean':<10} {'Std':<10} {'Min':<10} {'Max':<10}")
    print("-"*70)
    
    for i, name in enumerate(feature_names):
        values = X[:, i]
        mean = values.mean()
        std = values.std()
        min_val = values.min()
        max_val = values.max()
        
        print(f"{name:<30} {mean:>9.4f} {std:>9.4f} {min_val:>9.4f} {max_val:>9.4f}")
    
    print(f"\nTotal days analyzed: {X.shape[0]}")


def main():
    """Run examples"""
    print("\n" + "="*70)
    print("Daily Radio Propagation Analysis - Examples")
    print("="*70)
    
    examples = {
        '1': ('Extract Daily Features', example_1_extract_daily),
        '2': ('PyTorch LSTM', example_2_pytorch_daily_lstm),
        '3': ('TensorFlow LSTM', example_3_tensorflow_daily_lstm),
        '4': ('Clustering Days', example_4_clustering_propagation_days),
        '5': ('Daily Statistics', example_5_daily_statistics),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}: {name}")
    print(f"  0: Run all examples")
    print(f"  q: Quit")
    
    while True:
        choice = input("\nSelect example (0-5, q): ").strip().lower()
        
        if choice == 'q':
            print("Exiting...")
            break
        elif choice == '0':
            for key in ['1', '2', '3', '4', '5']:
                _, func = examples[key]
                try:
                    func()
                except Exception as e:
                    print(f"Error: {e}")
            break
        elif choice in examples:
            _, func = examples[choice]
            try:
                func()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            '1': example_1_extract_daily,
            '2': example_2_pytorch_daily_lstm,
            '3': example_3_tensorflow_daily_lstm,
            '4': example_4_clustering_propagation_days,
            '5': example_5_daily_statistics,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Invalid example: {example_num}")
    else:
        main()

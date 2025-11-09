#!/usr/bin/env python3
"""
Complete end-to-end example: Extract API data and train a simple neural network.
This demonstrates how to use the feature extraction pipeline in a real project.
"""

import sys
from simple_extractor import SimpleFeatureExtractor

def example_1_basic_extraction():
    """Example 1: Basic feature extraction"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Feature Extraction")
    print("="*70)
    
    extractor = SimpleFeatureExtractor()
    
    # Fetch and process
    spots = extractor.fetch_data(limit=30)
    if not spots:
        return None
    
    raw = extractor.extract_features(spots)
    normalized = extractor.normalize_features()
    
    # Display
    print("\nFeature names:")
    names = ["frequency_mhz", "band_id", "hour_of_day", "day_of_week", "signal_report", "mode_id"]
    for i, name in enumerate(names):
        print(f"  {i}: {name}")
    
    print(f"\nFirst 3 normalized feature vectors:")
    for i, vec in enumerate(normalized[:3]):
        print(f"  Sample {i+1}: {[f'{v:.4f}' for v in vec]}")
    
    return normalized


def example_2_statistics():
    """Example 2: Compute statistics on features"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Feature Statistics")
    print("="*70)
    
    extractor = SimpleFeatureExtractor()
    spots = extractor.fetch_data(limit=50)
    if not spots:
        return
    
    raw = extractor.extract_features(spots)
    normalized = extractor.normalize_features()
    
    # Calculate statistics
    names = ["frequency_mhz", "band_id", "hour_of_day", "day_of_week", "signal_report", "mode_id"]
    
    print(f"\n{'Feature':<20} {'Mean':<10} {'Min':<10} {'Max':<10} {'Std':<10}")
    print("-"*60)
    
    for i, name in enumerate(names):
        values = [v[i] for v in normalized]
        mean = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        std = (sum((v - mean)**2 for v in values) / len(values)) ** 0.5
        
        print(f"{name:<20} {mean:<10.4f} {min_val:<10.4f} {max_val:<10.4f} {std:<10.4f}")


def example_3_pytorch_training():
    """Example 3: Train a simple neural network with PyTorch"""
    print("\n" + "="*70)
    print("EXAMPLE 3: PyTorch Neural Network Training")
    print("="*70)
    
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
    except ImportError:
        print("PyTorch not installed. Install with: pip install torch")
        return
    
    # Extract features
    extractor = SimpleFeatureExtractor()
    spots = extractor.fetch_data(limit=100)
    if not spots:
        return
    
    raw = extractor.extract_features(spots)
    normalized = extractor.normalize_features()
    
    # Convert to PyTorch tensors
    X = torch.tensor(normalized, dtype=torch.float32)
    
    # Create simple model: predict frequency from other features
    class SimpleNN(nn.Module):
        def __init__(self):
            super(SimpleNN, self).__init__()
            self.fc1 = nn.Linear(5, 16)  # 5 input features (exclude frequency)
            self.fc2 = nn.Linear(16, 8)
            self.fc3 = nn.Linear(8, 1)   # Predict frequency
            self.relu = nn.ReLU()
        
        def forward(self, x):
            x = self.relu(self.fc1(x))
            x = self.relu(self.fc2(x))
            x = self.fc3(x)
            return x
    
    model = SimpleNN()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    # Prepare data: use features 1-5 to predict feature 0
    X_input = X[:, 1:]  # band, hour, dow, signal, mode
    y_target = X[:, 0:1]  # frequency
    
    print(f"\nTraining model to predict frequency from other features...")
    print(f"Input shape: {X_input.shape}")
    print(f"Target shape: {y_target.shape}")
    
    # Simple training loop
    best_loss = float('inf')
    for epoch in range(100):
        optimizer.zero_grad()
        predictions = model(X_input)
        loss = criterion(predictions, y_target)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:3d}: Loss = {loss.item():.6f}")
    
    print(f"✓ Training complete!")
    
    # Show predictions on first 5 samples
    print(f"\nSample Predictions (actual vs predicted frequency):")
    with torch.no_grad():
        predictions = model(X_input[:5])
        for i in range(5):
            actual = y_target[i, 0].item()
            predicted = predictions[i, 0].item()
            error = abs(actual - predicted)
            print(f"  Sample {i+1}: Actual={actual:.4f}, Predicted={predicted:.4f}, Error={error:.4f}")


def example_4_tensorflow_training():
    """Example 4: Train with TensorFlow/Keras"""
    print("\n" + "="*70)
    print("EXAMPLE 4: TensorFlow/Keras Neural Network Training")
    print("="*70)
    
    try:
        import tensorflow as tf
        import numpy as np
    except ImportError:
        print("TensorFlow not installed. Install with: pip install tensorflow")
        return
    
    # Extract features
    extractor = SimpleFeatureExtractor()
    spots = extractor.fetch_data(limit=100)
    if not spots:
        return
    
    raw = extractor.extract_features(spots)
    normalized = np.array(extractor.normalize_features())
    
    # Prepare data
    X_input = normalized[:, 1:]  # band, hour, dow, signal, mode
    y_target = normalized[:, 0:1]  # frequency
    
    print(f"\nInput shape: {X_input.shape}")
    print(f"Target shape: {y_target.shape}")
    
    # Create model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(16, activation='relu', input_shape=(5,)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    print(f"\nTraining TensorFlow model...")
    history = model.fit(
        X_input, y_target,
        epochs=100,
        batch_size=16,
        verbose=0
    )
    
    # Show final loss
    final_loss = history.history['loss'][-1]
    final_mae = history.history['mae'][-1]
    print(f"✓ Training complete!")
    print(f"  Final Loss: {final_loss:.6f}")
    print(f"  Final MAE: {final_mae:.6f}")
    
    # Show predictions
    print(f"\nSample Predictions (actual vs predicted frequency):")
    predictions = model.predict(X_input[:5], verbose=0)
    for i in range(5):
        actual = y_target[i, 0]
        predicted = predictions[i, 0]
        error = abs(actual - predicted)
        print(f"  Sample {i+1}: Actual={actual:.4f}, Predicted={predicted:.4f}, Error={error:.4f}")


def example_5_save_and_load():
    """Example 5: Save features to CSV and load them"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Save and Load Features")
    print("="*70)
    
    # Extract and save
    extractor = SimpleFeatureExtractor()
    spots = extractor.fetch_data(limit=50)
    if not spots:
        return
    
    raw = extractor.extract_features(spots)
    normalized = extractor.normalize_features()
    
    # Save to CSV
    filename = "example_features.csv"
    with open(filename, 'w') as f:
        f.write("frequency_mhz,band_id,hour_of_day,day_of_week,signal_report,mode_id\n")
        for vec in normalized:
            f.write(",".join(f"{v:.6f}" for v in vec) + "\n")
    
    print(f"✓ Saved {len(normalized)} feature vectors to {filename}")
    
    # Load and verify
    loaded_data = []
    with open(filename, 'r') as f:
        header = f.readline()  # Skip header
        for line in f:
            if line.strip():
                values = [float(x) for x in line.strip().split(',')]
                loaded_data.append(values)
    
    print(f"✓ Loaded {len(loaded_data)} feature vectors from {filename}")
    print(f"\nFirst row:")
    print(f"  {loaded_data[0]}")


def example_6_clustering():
    """Example 6: Cluster radio spots by characteristics"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Clustering Radio Spots")
    print("="*70)
    
    try:
        from sklearn.cluster import KMeans
        import numpy as np
    except ImportError:
        print("Scikit-learn not installed. Install with: pip install scikit-learn")
        return
    
    # Extract features
    extractor = SimpleFeatureExtractor()
    spots = extractor.fetch_data(limit=100)
    if not spots:
        return
    
    raw = extractor.extract_features(spots)
    normalized = np.array(extractor.normalize_features())
    
    # Perform clustering
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(normalized)
    
    print(f"\nClustered {len(clusters)} spots into {n_clusters} groups")
    
    # Show cluster distribution
    print(f"\nCluster distribution:")
    for i in range(n_clusters):
        count = sum(1 for c in clusters if c == i)
        percentage = count / len(clusters) * 100
        print(f"  Cluster {i}: {count:3d} spots ({percentage:5.1f}%)")
    
    # Show cluster centers
    names = ["frequency_mhz", "band_id", "hour_of_day", "day_of_week", "signal_report", "mode_id"]
    print(f"\nCluster Centers:")
    print(f"{'Cluster':<8} {' '.join(f'{n[:6]:<8}' for n in names)}")
    for i, center in enumerate(kmeans.cluster_centers_):
        print(f"{i:<8} {' '.join(f'{v:<8.4f}' for v in center)}")


def main():
    """Run all examples or specific ones"""
    print("\n" + "="*70)
    print("Neural Network Feature Extraction - Complete Examples")
    print("="*70)
    
    examples = {
        '1': ('Basic Extraction', example_1_basic_extraction),
        '2': ('Feature Statistics', example_2_statistics),
        '3': ('PyTorch Training', example_3_pytorch_training),
        '4': ('TensorFlow Training', example_4_tensorflow_training),
        '5': ('Save and Load', example_5_save_and_load),
        '6': ('Clustering', example_6_clustering),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}: {name}")
    print(f"  0: Run all examples")
    print(f"  q: Quit")
    
    while True:
        choice = input("\nSelect example (0-6, q): ").strip().lower()
        
        if choice == 'q':
            print("Exiting...")
            break
        elif choice == '0':
            for key in ['1', '2', '3', '4', '5', '6']:
                _, func = examples[key]
                try:
                    func()
                except Exception as e:
                    print(f"Error in example: {e}")
            print("\n✓ All examples completed!")
            break
        elif choice in examples:
            _, func = examples[choice]
            try:
                func()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific example from command line
        example_num = sys.argv[1]
        examples = {
            '1': example_1_basic_extraction,
            '2': example_2_statistics,
            '3': example_3_pytorch_training,
            '4': example_4_tensorflow_training,
            '5': example_5_save_and_load,
            '6': example_6_clustering,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Invalid example: {example_num}")
            print(f"Available: {', '.join(examples.keys())}")
    else:
        # Interactive mode
        main()

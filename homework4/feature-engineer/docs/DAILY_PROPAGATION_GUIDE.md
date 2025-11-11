# Daily Radio Wave Propagation Analysis

## Overview

For analyzing **daily radio wave propagation patterns**, this guide explains how to use aggregated daily features instead of individual spot features.

## Why Daily Aggregation?

Radio wave propagation changes throughout the day based on:
- **Solar radiation** (affects ionosphere)
- **Time of day** (different bands active at different times)
- **Day of week** (weather patterns, human activity)
- **Season** (solar cycle effects)

By aggregating all spots from a single day into statistical features, you capture:
- **Overall propagation conditions** for that day
- **Activity patterns** across all bands
- **Signal quality trends** throughout the day
- **Band usage patterns** for that specific day

## The 10 Daily Features

| # | Feature | Description | Range | Neural Network Use |
|---|---------|-------------|-------|-------------------|
| 1 | **avg_frequency_mhz** | Average frequency of all spots | 0-54 MHz | Indicates which bands were active |
| 2 | **num_bands_active** | Count of different bands (6m-40m) | 0-7 | Band diversity for the day |
| 3 | **total_spots** | Total number of radio spots | 0-1000s | Activity level intensity |
| 4 | **avg_signal_quality** | Average signal report (5-9 scale) | 0-99 | Propagation quality |
| 5 | **signal_quality_std** | Std deviation of signal quality | 0-X | Consistency of propagation |
| 6 | **cw_percentage** | Percent of spots using CW mode | 0-100 % | Operating mode preference |
| 7 | **ssb_percentage** | Percent of spots using SSB mode | 0-100 % | Operating mode preference |
| 8 | **activity_hours_count** | Number of hours with activity (0-24) | 0-24 | Hours of propagation |
| 9 | **peak_hour** | UTC hour with most activity | 0-23 | Best propagation hour |
| 10 | **40m_band_percentage** | Percent on 40m band (lowest frequency) | 0-100 % | Lower-band activity |

**Note**: Equipment operates on 6m, 10m, 12m, 15m, 17m, 20m, and 40m bands only (80m and 160m excluded)

## Example Output

### Raw Daily Features (before normalization)

```csv
date,avg_frequency_mhz,num_bands_active,total_spots,avg_signal_quality,signal_quality_std,cw_percentage,ssb_percentage,activity_hours_count,peak_hour,40m_band_percentage
2025-11-07,21145.600,7,145,57.300,2.140,15.200,42.100,22,16,28.300
2025-11-06,20890.450,7,189,58.100,1.890,12.600,48.700,23,15,32.100
2025-11-05,19234.500,6,112,55.900,3.200,18.900,39.400,20,17,25.600
```

### Normalized Daily Features (for neural networks)

```csv
date,avg_frequency_mhz,num_bands_active,total_spots,avg_signal_quality,signal_quality_std,cw_percentage,ssb_percentage,activity_hours_count,peak_hour,40m_band_percentage
2025-11-07,0.5234,0.7500,0.6843,0.5730,0.4521,0.3890,0.5321,0.9167,0.6957,0.4200
2025-11-06,0.5123,0.8571,0.8945,0.6100,0.3980,0.2890,0.6120,1.0000,0.6522,0.4750
2025-11-05,0.4756,0.5714,0.5289,0.4900,0.6700,0.4320,0.4980,0.8333,0.7391,0.3780
```

## Quick Start

### Using the Daily Extractor

```python
from daily_extractor import DailyFeatureExtractor

# Create extractor
extractor = DailyFeatureExtractor()

# Fetch data from API (this will contain multiple days)
spots = extractor.fetch_data(limit=1000)  # Get 1000 recent spots (multiple days)

# Group by date
daily_data = extractor.group_by_date(spots)

# Extract daily features
daily_features = extractor.extract_daily_features()

# Normalize to [0, 1]
normalized = extractor.normalize_features()

# Now use normalized features in your model
# Each row = one day of propagation data
# Each column = one propagation metric
```

### Structure of Normalized Data

```python
normalized = [
    ["2025-11-07", 0.5234, 0.7500, 0.6843, 0.5730, 0.4521, 0.3890, 0.5321, 0.9167, 0.6957, 0.4200],
    ["2025-11-06", 0.5123, 1.0000, 0.8945, 0.6100, 0.3980, 0.2890, 0.6120, 1.0000, 0.6522, 0.4750],
    ["2025-11-05", 0.4756, 0.6250, 0.5289, 0.4900, 0.6700, 0.4320, 0.4980, 0.8333, 0.7391, 0.3780],
    # ... more days
]

# For neural network input, use columns 1-10 (exclude date column 0)
X = normalized[:, 1:]  # Shape: (n_days, 10 features)

# Each day is one training sample
# Perfect for: LSTM, GRU, CNN, or regular Dense networks
```

## Using with Neural Networks

### PyTorch - Sequential Model

```python
import torch
import torch.nn as nn

from daily_extractor import DailyFeatureExtractor

# Extract daily features
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=1000)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Convert to tensor (skip date column, use numeric features only)
X = torch.tensor(
    [[float(v) for v in vec[1:]] for vec in normalized],  # Skip date
    dtype=torch.float32
)

# Create model: 10 input features -> predict propagation quality
model = nn.Sequential(
    nn.Linear(10, 32),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(32, 16),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(16, 1)  # Output: single propagation quality score
)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(100):
    optimizer.zero_grad()
    outputs = model(X)
    # Example: predict avg signal quality from other features
    target = X[:, 3:4]  # Column 3 is avg_signal_quality
    loss = criterion(outputs, target)
    loss.backward()
    optimizer.step()
```

### TensorFlow - LSTM for Time Series

```python
import tensorflow as tf
import numpy as np

from daily_extractor import DailyFeatureExtractor

# Extract daily features
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=2000)  # Get more data
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Convert to numpy (skip date column)
X = np.array([[float(v) for v in vec[1:]] for vec in normalized])

# Create sequences for LSTM (e.g., 7-day windows)
def create_sequences(data, seq_len=7):
    X_seq, y_seq = [], []
    for i in range(len(data) - seq_len):
        X_seq.append(data[i:i+seq_len])
        y_seq.append(data[i+seq_len, 3])  # Predict signal quality
    return np.array(X_seq), np.array(y_seq)

X_seq, y_seq = create_sequences(X, seq_len=7)

# LSTM model for forecasting daily propagation
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(32, input_shape=(7, 10), return_sequences=True),
    tf.keras.layers.LSTM(16),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model.fit(X_seq, y_seq, epochs=50, batch_size=4, validation_split=0.2)

# Predict next day's signal quality
last_week = X[-7:].reshape(1, 7, 10)
prediction = model.predict(last_week)
```

### Scikit-Learn - Clustering Daily Patterns

```python
from sklearn.cluster import KMeans
from daily_extractor import DailyFeatureExtractor
import numpy as np

# Extract daily features
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=500)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Get dates and features
dates = [vec[0] for vec in normalized]
X = np.array([[float(v) for v in vec[1:]] for vec in normalized])

# Cluster similar propagation days
kmeans = KMeans(n_clusters=4, random_state=42)
clusters = kmeans.fit_predict(X)

# Analyze clusters
for cluster_id in range(4):
    cluster_days = [dates[i] for i in range(len(clusters)) if clusters[i] == cluster_id]
    print(f"Cluster {cluster_id}: {len(cluster_days)} days")
    print(f"  Days: {', '.join(cluster_days[:5])}{'...' if len(cluster_days) > 5 else ''}")
```

## Feature Engineering from Daily Data

### Additional Features You Can Create

```python
import numpy as np

# Given: normalized daily features matrix X (n_days, 10)

# 1. Daily propagation quality score
propagation_quality = (X[:, 3] + X[:, 4]) / 2  # avg signal, low std

# 2. Band activity diversity
band_diversity = X[:, 1] / 9.0  # num_bands / total_bands

# 3. Operating mode distribution
voice_percentage = X[:, 6] + X[:, 7]  # cw + ssb percentage

# 4. Activity intensity
activity_intensity = X[:, 2] * X[:, 8] / 24  # total_spots * hours / 24

# 5. 40m band preference
band_preference = X[:, 9] - (1 - X[:, 9])  # 40m_band_percentage - other_bands

# Combine into extended feature set
X_extended = np.column_stack([
    X,
    propagation_quality,
    band_diversity,
    voice_percentage,
    activity_intensity,
    band_bias
])
```

## Tips for Daily Propagation Models

1. **Sequence Length**: Use 7-30 day windows for LSTM models to capture weekly patterns
2. **Seasonality**: Consider date features (day_of_year % 365) for solar cycle effects
3. **Validation**: Use time-series split (not random) to respect temporal dependencies
4. **Features to Predict**:
   - Next day's signal quality
   - Band activity distribution
   - Peak hour timing
5. **Preprocessing**: Features are already normalized [0,1], good for most models

## Sample Code - Complete Example

```python
from daily_extractor import DailyFeatureExtractor
import numpy as np

# Step 1: Extract daily features
print("Extracting daily propagation features...")
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=500)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Step 2: Prepare for neural network
X = np.array([[float(v) for v in vec[1:]] for vec in normalized])
dates = np.array([vec[0] for vec in normalized])

print(f"\nDaily Feature Matrix:")
print(f"  Shape: {X.shape} (days × features)")
print(f"  Date range: {dates[0]} to {dates[-1]}")
print(f"  All values in [0, 1]: {np.all((X >= 0) & (X <= 1))}")

# Step 3: Use in your model
print(f"\nReady for propagation analysis models!")
print(f"  PyTorch: X = torch.tensor(X, dtype=torch.float32)")
print(f"  TensorFlow: X = X (already numpy array)")
print(f"  Scikit-Learn: model.fit(X, y)")
```

## Key Differences: Individual vs Daily Features

### Individual Features (simple_extractor.py)
- **One vector per radio spot**
- **6 features per spot**
- **Real-time data points**
- **Use case**: Individual signal analysis, spot classification

### Daily Features (daily_extractor.py)
- **One vector per day**
- **10 aggregated features per day**
- **Statistical summaries**
- **Use case**: Propagation forecasting, daily trend analysis

**For radio wave propagation analysis → Use daily_extractor.py**

## Running the Daily Extractor

```bash
python daily_extractor.py
```

Output:
- Console display of daily statistics
- `daily_radio_features.csv` file with all data

Each row = one day of propagation data
Each column = one propagation metric
Perfect for your neural network models!

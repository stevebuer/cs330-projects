# Neural Network Integration Guide

Quick reference for using the extracted feature vectors with popular neural network frameworks.

## Quick Reference

**Feature Vector**: 6 normalized values in range [0, 1]

```python
[frequency_mhz, band_id, hour_of_day, day_of_week, signal_report, mode_id]
```

---

## PyTorch

### Basic Setup

```python
import torch
import torch.nn as nn
from simple_extractor import SimpleFeatureExtractor

# Extract features
extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
raw_features = extractor.extract_features(spots)
normalized_features = extractor.normalize_features()

# Convert to PyTorch tensor
X = torch.tensor(normalized_features, dtype=torch.float32)

# Create dataset and loader
from torch.utils.data import TensorDataset, DataLoader
dataset = TensorDataset(X)
loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Simple Neural Network

```python
class RadioNet(nn.Module):
    def __init__(self, input_size=6, output_size=1):
        super(RadioNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, output_size)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

# Initialize model
model = RadioNet(input_size=6, output_size=1)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(100):
    for batch_X, in loader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_X[:, :1])  # Example: predict frequency
        loss.backward()
        optimizer.step()
```

### Advanced: Convolutional Approach

```python
class RadioCNN(nn.Module):
    def __init__(self):
        super(RadioCNN, self).__init__()
        # Reshape (batch, 6) -> (batch, 1, 6) for conv1d
        self.conv1 = nn.Conv1d(1, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(96, 64)  # 32 * 3
        self.fc2 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = x.unsqueeze(1)  # Add channel dimension
        x = self.relu(self.conv1(x))
        x = self.pool(x)
        x = self.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x
```

---

## TensorFlow/Keras

### Basic Setup

```python
import tensorflow as tf
import numpy as np
from simple_extractor import SimpleFeatureExtractor

# Extract features
extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
raw_features = extractor.extract_features(spots)
normalized_features = extractor.normalize_features()

X = np.array(normalized_features)
```

### Simple Sequential Model

```python
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(6,)),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(
    optimizer='adam',
    loss='mse',
    metrics=['mae']
)

# Training
history = model.fit(X, X[:, :1], epochs=50, batch_size=32, validation_split=0.2)
```

### CNN Model

```python
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(6,)),
    tf.keras.layers.Reshape((6, 1)),
    tf.keras.layers.Conv1D(16, 3, activation='relu', padding='same'),
    tf.keras.layers.MaxPooling1D(2),
    tf.keras.layers.Conv1D(32, 3, activation='relu', padding='same'),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model.fit(X, X[:, :1], epochs=50, batch_size=32)
```

### LSTM for Sequence Prediction

```python
# Prepare sequences from time series data
def create_sequences(data, seq_length=10):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

X_seq, y_seq = create_sequences(X, seq_length=10)

model = tf.keras.Sequential([
    tf.keras.layers.LSTM(32, input_shape=(10, 6), return_sequences=True),
    tf.keras.layers.LSTM(16),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model.fit(X_seq, y_seq, epochs=50, batch_size=16)
```

---

## Scikit-Learn

### Clustering

```python
from sklearn.cluster import KMeans
from simple_extractor import SimpleFeatureExtractor

extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
raw_features = extractor.extract_features(spots)
normalized_features = extractor.normalize_features()

# K-Means clustering
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(normalized_features)
```

### Dimensionality Reduction

```python
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# PCA
pca = PCA(n_components=3)
X_pca = pca.fit_transform(normalized_features)

# t-SNE
tsne = TSNE(n_components=2)
X_tsne = tsne.fit_transform(normalized_features)
```

### Classification

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Create synthetic labels (e.g., high activity vs low)
y = (X[:, 4] > 0.5).astype(int)  # Based on signal report

X_train, X_test, y_train, y_test = train_test_split(
    normalized_features, y, test_size=0.2, random_state=42
)

# Train classifier
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Predict
accuracy = clf.score(X_test, y_test)
print(f"Accuracy: {accuracy:.4f}")
```

---

## JAX

```python
import jax
import jax.numpy as jnp
from jax import grad, jit
from simple_extractor import SimpleFeatureExtractor

# Extract features
extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
raw_features = extractor.extract_features(spots)
X = jnp.array(extractor.normalize_features())

# Neural network using JAX
def init_params(key, input_size, hidden_size, output_size):
    key1, key2 = jax.random.split(key)
    W1 = jax.random.normal(key1, (input_size, hidden_size)) * 0.01
    b1 = jnp.zeros(hidden_size)
    W2 = jax.random.normal(key2, (hidden_size, output_size)) * 0.01
    b2 = jnp.zeros(output_size)
    return {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}

def forward(params, x):
    x = jnp.dot(x, params['W1']) + params['b1']
    x = jax.nn.relu(x)
    x = jnp.dot(x, params['W2']) + params['b2']
    return x

def loss_fn(params, x):
    predictions = forward(params, x)
    return jnp.mean((predictions - x[:, :1])**2)

# Train
key = jax.random.PRNGKey(0)
params = init_params(key, 6, 32, 1)
grad_fn = jax.grad(loss_fn)

for _ in range(100):
    grads = grad_fn(params, X)
    params = jax.tree_map(lambda p, g: p - 0.001 * g, params, grads)
```

---

## Feature Engineering Tips

### 1. Feature Scaling

The features are already normalized to [0, 1]. For some models, you might want to standardize:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_standardized = scaler.fit_transform(X)
```

### 2. Feature Interaction

Create interaction terms:

```python
X_with_interactions = np.concatenate([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # frequency * band
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # hour * day_of_week
], axis=1)
```

### 3. Polynomial Features

```python
from sklearn.preprocessing import PolynomialFeatures

poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
```

### 4. Time-Based Features

If you have sequences over time:

```python
# Create sliding windows
def create_windows(X, window_size=5):
    windows = []
    for i in range(len(X) - window_size):
        windows.append(X[i:i+window_size].flatten())
    return np.array(windows)

X_windowed = create_windows(X, window_size=5)
```

---

## Performance Optimization

### Batch Processing

```python
def process_in_batches(api_limit, batch_size=100):
    all_features = []
    for offset in range(0, api_limit, batch_size):
        extractor = SimpleFeatureExtractor()
        spots = extractor.fetch_data(limit=batch_size)
        features = extractor.extract_features(spots)
        normalized = extractor.normalize_features()
        all_features.extend(normalized)
    return np.array(all_features)
```

### GPU Acceleration (PyTorch)

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
X = torch.tensor(normalized_features, dtype=torch.float32).to(device)
model = model.to(device)
```

### GPU Acceleration (TensorFlow)

```python
import tensorflow as tf

# Automatic GPU usage
print(tf.config.list_physical_devices('GPU'))

with tf.device('/GPU:0'):
    model.fit(X, y, epochs=50)
```

---

## Example Use Cases

### 1. Signal Quality Prediction
Predict signal strength based on other features.
```python
# Target: signal_report (index 4)
# Features: all others
```

### 2. Activity Pattern Recognition
Identify when and where radio activity peaks.
```python
# Clustering on hour_of_day and day_of_week
# Visualize active hours
```

### 3. Band Selection
Predict optimal band based on time of day.
```python
# Classification: predict band from hour/day
```

### 4. Anomaly Detection
Identify unusual radio activity patterns.
```python
# Unsupervised learning on all features
```

---

## Troubleshooting

**Issue**: "Shape mismatch" in model
- **Solution**: Ensure X has shape (n_samples, 6)

**Issue**: Values outside [0, 1]
- **Solution**: Verify normalization completed successfully

**Issue**: Poor model performance
- **Solution**: 
  - Try feature engineering (interactions, polynomials)
  - Increase model capacity
  - Collect more data
  - Use data augmentation

**Issue**: Memory errors with large datasets
- **Solution**:
  - Use batch processing
  - Reduce batch size
  - Use generators instead of loading all data at once

---

## Resources

- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)
- [Scikit-Learn Documentation](https://scikit-learn.org/stable/documentation.html)
- [Normalization and Standardization](https://scikit-learn.org/stable/modules/preprocessing.html)

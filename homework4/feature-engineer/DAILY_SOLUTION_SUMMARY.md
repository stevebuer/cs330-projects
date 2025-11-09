# Daily Radio Propagation Feature Extraction - Summary

## 🎯 Updated Solution for Daily Analysis

You now have **two complementary tools** for extracting features from the ham radio spotting API:

## Tool Comparison

| Aspect | Individual Spots | Daily Aggregation |
|--------|-----------------|-------------------|
| **File** | `simple_extractor.py` | `daily_extractor.py` |
| **Vectors per** | Single radio spot | Single day |
| **Features** | 6 per spot | 10 per day |
| **Time range** | Real-time | 24 hours aggregated |
| **Use case** | Signal classification | Propagation forecasting |
| **Best for** | Immediate analysis | Your propagation models ⭐ |

## 10 Daily Propagation Features

Each day gets a vector with these 10 features (normalized to [0,1]):

```python
[
    1. avg_frequency_mhz,           # Average frequency of all spots
    2. num_bands_active,            # Different bands active today
    3. total_spots,                 # Total radio spots detected
    4. avg_signal_quality,          # Average signal strength
    5. signal_quality_std,          # Consistency of signals
    6. cw_percentage,               # % using CW mode
    7. ssb_percentage,              # % using SSB mode
    8. activity_hours_count,        # Hours with activity (0-24)
    9. peak_hour,                   # Best hour for activity
    10. 40m_band_percentage         # % on 40m band
]
```

## Quick Start - Daily Extraction

### Command Line
```bash
python daily_extractor.py
```

**Output**: 
- `daily_radio_features.csv` with one row per day
- Console display of daily statistics

### In Your Code
```python
from daily_extractor import DailyFeatureExtractor
import numpy as np

# Extract daily features
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=500)  # Gets multiple days
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# X is now (num_days, 10) ready for your model
X = np.array([[float(v) for v in vec[1:]] for vec in normalized])
```

## Example Daily Data

### Raw Features (before normalization)
```
Date        Freq   Bands  Spots  AvgSig StdSig  CW%   SSB%   Hours  Peak  LW%
2025-11-07  21145  7      145    57.3   2.1     15.2  42.1   22     16    28.3
2025-11-06  20890  8      189    58.1   1.9     12.6  48.7   23     15    32.1
2025-11-05  19234  6      112    55.9   3.2     18.9  39.4   20     17    25.6
```

### Normalized Features (for neural networks)
```
Date        Freq   Bands  Spots  AvgSig StdSig  CW%   SSB%   Hours  Peak  LW%
2025-11-07  0.523  0.750  0.684  0.573  0.452   0.389 0.532  0.917  0.696 0.420
2025-11-06  0.512  1.000  0.895  0.610  0.398   0.289 0.612  1.000  0.652 0.475
2025-11-05  0.476  0.625  0.529  0.490  0.670   0.432 0.498  0.833  0.739 0.378
```

## Using with Neural Networks

### PyTorch LSTM (Time Series Forecasting)
```python
import torch
import torch.nn as nn
from daily_extractor import DailyFeatureExtractor

# Extract daily data
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=1000)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Prepare sequences (7-day windows)
X = torch.tensor(
    [[float(v) for v in vec[1:]] for vec in normalized],
    dtype=torch.float32
)

# Create LSTM model to predict next day's signal quality
model = nn.Sequential(
    nn.LSTM(10, 32, batch_first=True),
    nn.LSTM(32, 16, batch_first=True),
    nn.Linear(16, 1)  # Output: signal quality
)
```

See `DAILY_PROPAGATION_GUIDE.md` for complete code examples.

### TensorFlow LSTM
```python
import tensorflow as tf
import numpy as np
from daily_extractor import DailyFeatureExtractor

extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=1000)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

X = np.array([[float(v) for v in vec[1:]] for vec in normalized])

# 7-day sequences for LSTM
X_seq = []
y_seq = []
for i in range(len(X) - 7):
    X_seq.append(X[i:i+7])
    y_seq.append(X[i+7, 3])  # Predict signal quality

model = tf.keras.Sequential([
    tf.keras.layers.LSTM(32, input_shape=(7, 10)),
    tf.keras.layers.Dense(1)
])

model.fit(X_seq, y_seq, epochs=50)
```

## Files Included

### New Files
- ✅ **`daily_extractor.py`** - Daily feature extraction (replaces simple_extractor for daily analysis)
- ✅ **`daily_examples.py`** - 5 complete working examples
- ✅ **`DAILY_PROPAGATION_GUIDE.md`** - Comprehensive daily analysis guide

### Existing Files (Still Useful)
- ✅ **`simple_extractor.py`** - For individual spot analysis
- ✅ **`feature_extractor.py`** - Advanced individual spot analysis
- ✅ **`feature_extraction_notebook.ipynb`** - Interactive notebook
- ✅ **`NEURAL_NETWORK_GUIDE.md`** - Framework integration

## Running Examples

### Extract Daily Features
```bash
python daily_extractor.py
```

### Try Different Analysis Techniques
```bash
python daily_examples.py
```

Interactive menu shows:
1. Extract and view daily features
2. PyTorch LSTM forecasting
3. TensorFlow LSTM forecasting
4. Clustering similar propagation days
5. Daily statistics

## Recommended Workflow

### For Propagation Analysis

```
1. Run daily extraction:
   python daily_extractor.py

2. Load daily features:
   from daily_extractor import DailyFeatureExtractor
   extractor = DailyFeatureExtractor()
   spots = extractor.fetch_data(limit=500)
   extractor.group_by_date(spots)
   normalized = extractor.normalize_features()

3. Build your model:
   # LSTM for time series forecasting
   # CNN for pattern recognition
   # Dense network for classification

4. Train and evaluate:
   model.fit(X_train, y_train)
   predictions = model.predict(X_test)
```

## Key Advantages of Daily Features

✅ **Captures propagation conditions** for entire day  
✅ **Reduces noise** from individual spot variations  
✅ **Enables forecasting** of next day's conditions  
✅ **Aggregated statistics** (mean, std, etc.)  
✅ **Normalized [0, 1]** ready for neural networks  
✅ **Time-series ready** for LSTM/GRU models  
✅ **Identifies patterns** across multiple days  

## Example Predictions You Can Make

1. **Tomorrow's signal quality** - Using today's daily vector
2. **Peak propagation hour** - Which UTC hour will have best activity
3. **Number of active bands** - How many bands will be in use
4. **Activity level** - How many spots expected tomorrow
5. **Mode distribution** - Will it be mostly CW or voice?

## Data Flow

```
API Endpoint (139,000+ spots)
    ↓
Group by date (YYYY-MM-DD)
    ↓
Daily aggregation for each day:
  - Calculate statistics
  - Count modes
  - Identify bands
  - Find peak hours
    ↓
10 features per day
    ↓
Min-Max normalization [0,1]
    ↓
Ready for neural networks!
    ↓
Each row = one day of propagation data
```

## Integration Example

```python
from daily_extractor import DailyFeatureExtractor
import numpy as np
import torch
import torch.nn as nn

# Step 1: Extract daily features
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(limit=1000)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Step 2: Prepare for PyTorch
X = torch.tensor(
    [[float(v) for v in vec[1:]] for vec in normalized],
    dtype=torch.float32
)

# Step 3: Your neural network
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 32),
    nn.ReLU(),
    nn.Linear(32, 1)  # Predict signal quality
)

# Step 4: Train
optimizer = torch.optim.Adam(model.parameters())
for epoch in range(100):
    # ... training code ...
    pass

# Step 5: Use for propagation analysis
print("✓ Ready for propagation forecasting!")
```

## File Structure

```
c:\STEVE\DEV\api-extract\
├── daily_extractor.py           ⭐ Main tool for daily analysis
├── daily_examples.py            ⭐ Examples (PyTorch, TensorFlow, etc.)
├── DAILY_PROPAGATION_GUIDE.md   ⭐ Complete guide
├── simple_extractor.py          (Individual spots)
├── feature_extractor.py         (Advanced spots)
├── NEURAL_NETWORK_GUIDE.md      (Framework integration)
├── feature_extraction_notebook.ipynb  (Interactive)
└── [other documentation files]
```

## Status

✅ **Complete and Ready**

- ✅ Daily feature extraction implemented
- ✅ 10 propagation metrics per day
- ✅ Normalization for neural networks
- ✅ Multiple example implementations
- ✅ PyTorch examples included
- ✅ TensorFlow examples included
- ✅ Scikit-learn examples included
- ✅ Full documentation

## Next Steps

1. **Run the daily extractor**: `python daily_extractor.py`
2. **Review daily features**: Open `daily_radio_features.csv`
3. **See examples**: `python daily_examples.py`
4. **Read guide**: Open `DAILY_PROPAGATION_GUIDE.md`
5. **Build your model**: Use the examples as templates

---

**Ready to analyze daily radio wave propagation patterns!**

Each day's feature vector captures the complete propagation picture for that date.
Perfect for forecasting, pattern recognition, and trend analysis.

# Historical Data Extraction Guide

**Updated**: November 7, 2025  
**Feature**: Filter to extract only historical/past data (exclude today and future)

---

## Overview

The `daily_extractor.py` has been updated to support extracting **only historical data** from previous days, which is crucial for machine learning workflows where:
- **Training data**: Past days (N-1 days prior)
- **Prediction target**: Today or future dates

This ensures proper separation between training history and prediction targets, preventing data leakage and unrealistic model performance.

---

## Updated `fetch_data()` Parameters

### Method Signature
```python
def fetch_data(self, limit: int = None, exclude_today: bool = True, days_back: int = None):
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | None | Maximum number of spots to fetch (None = fetch all) |
| `exclude_today` | bool | True | If True, excludes today's date from extraction |
| `days_back` | int | None | If set, only includes data from N days ago or earlier |

### Return Value
```python
List[Dict]  # Filtered list of spot dictionaries from historical dates
```

---

## Usage Examples

### Example 1: Extract Yesterday and Earlier (Default Behavior)
```python
from daily_extractor import DailyFeatureExtractor

extractor = DailyFeatureExtractor()
spots = extractor.fetch_data()  # Automatically excludes today
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Result: Only data from previous days, no today
```

### Example 2: Explicitly Exclude Today
```python
# Same as default behavior
spots = extractor.fetch_data(exclude_today=True)
```

### Example 3: Include Today (Not Recommended for Training)
```python
# Include today if you want current data (not for model training)
spots = extractor.fetch_data(exclude_today=False)
```

### Example 4: Get Last 30 Days Only
```python
# Extract data from last 30 days (30 days ago to yesterday)
spots = extractor.fetch_data(exclude_today=True, days_back=30)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Result: 30 vectors, one per day, for training
```

### Example 5: Get Last 7 Days (Weekly Window)
```python
# Extract last week's data for weekly forecasting model
spots = extractor.fetch_data(exclude_today=True, days_back=7)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
normalized = extractor.normalize_features()

# Result: ~7 vectors for training
```

### Example 6: Limit Spots AND Dates
```python
# Get max 500 spots from last 14 days (no today)
spots = extractor.fetch_data(
    limit=500,
    exclude_today=True,
    days_back=14
)
```

---

## Practical Workflow: Training vs Prediction

### Scenario: Daily Propagation Forecasting

**Goal**: Predict tomorrow's signal quality based on historical patterns

```python
from daily_extractor import DailyFeatureExtractor
import numpy as np

# [1] Extract Historical Data for Training
# =========================================
extractor = DailyFeatureExtractor()

# Get last 60 days (exclude today, use for training)
spots_train = extractor.fetch_data(
    exclude_today=True,
    days_back=60
)

extractor.group_by_date(spots_train)
daily_features = extractor.extract_daily_features()
X_train = np.array(extractor.normalize_features())  # 60 vectors

print(f"Training data shape: {X_train.shape}")  # (60, 10)

# [2] Optional: Get Today's Data for Features (but NOT for training)
# ===================================================================
# If you wanted to make features from today for prediction input,
# you would NOT train on this data
extractor_predict = DailyFeatureExtractor()
spots_today = extractor_predict.fetch_data(exclude_today=False)

# Filter only today's data
today_date = datetime.now().strftime("%Y-%m-%d")
today_spots = [s for s in spots_today if today_date in s.get("timestamp", "")]

# Extract today as prediction features
# (NOT added to training set)
extractor_predict.raw_spots = today_spots
extractor_predict.group_by_date(today_spots)
today_features = extractor_predict.extract_daily_features()
X_predict = np.array(extractor_predict.normalize_features())  # (1, 10)

print(f"Prediction input shape: {X_predict.shape}")  # (1, 10)

# [3] Train Neural Network
# =========================
import torch

model = torch.nn.Sequential(
    torch.nn.Linear(10, 32),
    torch.nn.ReLU(),
    torch.nn.Linear(32, 16),
    torch.nn.ReLU(),
    torch.nn.Linear(16, 1)  # Predict signal quality
)

# Train ONLY on historical data (X_train)
# Do NOT include today in training set
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
# ... training loop ...

# [4] Predict Tomorrow
# ====================
X_predict_tensor = torch.tensor(X_predict, dtype=torch.float32)
prediction = model(X_predict_tensor)
print(f"Tomorrow's predicted signal quality: {prediction.item()}")
```

---

## Data Date Flow Diagram

```
Timeline:
  60 days ago ← [Training Window] → Yesterday
       ↓            ↓                   ↓
  Oct 8, 2025   Oct 9 - Nov 6    November 6, 2025
  
    │ Training Data │        │ Today (Nov 7) │ Future │
    └──────────────┬────────┘      └─────┬──────────┘
    Extracted with      NOT extracted    NOT extracted
    exclude_today=True  (reserved for     (not available
    days_back=60        prediction)       yet)
                        
Purpose:
  ✓ Training data: 60 historical days
  ✓ Prediction input: Today's extracted features
  ✗ Training on today: Would be data leakage
  ✗ Training on future: Impossible
```

---

## Why This Matters: Preventing Data Leakage

### ❌ WRONG: Training with Today's Data
```python
# BAD PRACTICE - Data Leakage!
spots = extractor.fetch_data(exclude_today=False)  # Includes today
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()

# Train on data including today
X = np.array(extractor.normalize_features())
model.fit(X, y)  # Today's features are in training set

# Try to predict today - CHEATING!
prediction = model.predict(today_features)  # Model saw this data during training!
# Result: Unrealistically high accuracy, fails in production
```

### ✅ CORRECT: Training with Only Historical Data
```python
# GOOD PRACTICE - No Data Leakage
spots = extractor.fetch_data(exclude_today=True)  # Only past days
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()

# Train ONLY on historical data
X_train = np.array(extractor.normalize_features())
model.fit(X_train, y_train)  # No today in training

# Predict today - Model has never seen this data
prediction = model.predict(today_features)  # Fresh data for prediction
# Result: Realistic accuracy that transfers to production
```

---

## Configuration Guide

### For Different Prediction Scenarios

#### Scenario 1: 24-Hour Forecasting (Predict Tomorrow)
```python
# Extract last 30 days for training, predict tomorrow
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(exclude_today=True, days_back=30)
extractor.group_by_date(spots)
daily_features = extractor.extract_daily_features()
X_train = np.array(extractor.normalize_features())  # 30 days

# Make prediction for tomorrow using today's data
# (extracted separately with exclude_today=False and filtered to today only)
```

#### Scenario 2: Weekly Forecasting (Predict Next Week)
```python
# Extract last 90 days (3 months), group by week
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(exclude_today=True, days_back=90)
extractor.group_by_date(spots)

# Could aggregate to weekly features for next week prediction
```

#### Scenario 3: Real-time Anomaly Detection
```python
# Build baseline from historical data
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data(exclude_today=True, days_back=90)
extractor.group_by_date(spots)
X_baseline = np.array(extractor.normalize_features())

# Calculate statistics
baseline_mean = X_baseline.mean(axis=0)
baseline_std = X_baseline.std(axis=0)

# Get today's data
extractor_today = DailyFeatureExtractor()
spots_today = extractor_today.fetch_data(exclude_today=False)  # Include today
# ... extract today's features ...
today_features = np.array(extractor_today.normalize_features())

# Detect anomalies vs baseline
z_scores = (today_features - baseline_mean) / baseline_std
anomalies = np.abs(z_scores) > 3  # 3-sigma rule
```

---

## Default Behavior (Recommended)

```python
# Simplest usage - SAFE for training
extractor = DailyFeatureExtractor()
spots = extractor.fetch_data()  # Defaults: exclude_today=True, days_back=None

# This will:
# ✓ Exclude today automatically
# ✓ Include all available historical data
# ✓ Prevent accidentally training on today's data
```

---

## API Filter Output

When you call fetch_data with filters, you'll see status messages:

```
✓ Fetched 2500 spots from API (historical data)
  Note: Excluded today (2025-11-07) - using only previous days
  Note: Limited to 30 days back (since 2025-10-08)
```

---

## Summary of Changes

### What Changed in `daily_extractor.py`

1. **fetch_data()** now accepts two new optional parameters:
   - `exclude_today` (bool, default True) - Removes current date
   - `days_back` (int, default None) - Limits to N days prior

2. **Date filtering logic** added to filter spots by:
   - Excluding today if `exclude_today=True`
   - Only including data from N days ago if `days_back` is set

3. **Informative output** shows what filtering was applied

4. **Backward compatible** - Existing code still works, new behavior is automatic

---

## Best Practices

### ✅ DO:

1. **Always use `exclude_today=True` for training**
   ```python
   spots = extractor.fetch_data(exclude_today=True)
   ```

2. **Use `days_back` to control training window size**
   ```python
   spots = extractor.fetch_data(exclude_today=True, days_back=60)
   ```

3. **Keep training and prediction data separate**
   ```python
   X_train = extractor.fetch_data(exclude_today=True)
   X_predict = extractor.fetch_data(exclude_today=False)
   ```

4. **Document your date cutoffs**
   ```python
   # Training on 30 days of historical data (excluding today)
   spots = extractor.fetch_data(exclude_today=True, days_back=30)
   ```

### ❌ DON'T:

1. **Train on today's data**
   ```python
   # BAD - Data leakage
   spots = extractor.fetch_data(exclude_today=False)  # Includes today!
   ```

2. **Include future dates (when available)**
   ```python
   # If API ever includes future data, filter it out
   spots = extractor.fetch_data(exclude_today=True)
   ```

3. **Forget about your date range when evaluating**
   ```python
   # Remember: model trained on days 1-60, evaluate on day 61+
   ```

4. **Mix training and test data**
   ```python
   # WRONG: Using overlapping dates for train/test split
   X_train = fetch_data(days_back=30)
   X_test = fetch_data(days_back=40)  # Overlaps with train!
   ```

---

## Testing Your Setup

```python
from daily_extractor import DailyFeatureExtractor
from datetime import datetime

extractor = DailyFeatureExtractor()

# Test 1: Exclude today
print("Test 1: Excluding today")
spots_excl = extractor.fetch_data(exclude_today=True, limit=100)
print(f"  Fetched {len(spots_excl)} spots\n")

# Test 2: Include today
print("Test 2: Including today")
spots_incl = extractor.fetch_data(exclude_today=False, limit=100)
print(f"  Fetched {len(spots_incl)} spots\n")

# Test 3: Last 7 days
print("Test 3: Last 7 days only")
spots_week = extractor.fetch_data(exclude_today=True, days_back=7, limit=100)
print(f"  Fetched {len(spots_week)} spots\n")

# Verify the difference
print(f"Difference (exclude_today effect): {len(spots_incl) - len(spots_excl)} spots")
```

---

## Questions?

**Q: Should I always use exclude_today=True?**  
A: Yes, unless you specifically need today's data for feature extraction (and won't use it for training).

**Q: What if I want to predict multiple days ahead?**  
A: Extract with exclude_today=True, train the model, then predict multiple days ahead using appropriate input features.

**Q: Can I use today's data for validation?**  
A: Yes, if you've trained only on historical data and want to validate on today. But keep them separate during development.

**Q: What about hourly or real-time prediction?**  
A: The principle stays the same: never train on data you're trying to predict.

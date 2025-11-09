# Quick Reference: Historical Data Extraction

**One-page cheat sheet for date filtering in daily_extractor.py**

---

## The Goal

Train on **historical/past days only** ← **TODAY** → Predict **tomorrow/future**

```
Previous Days (Training) │ Today (Prediction)
                         ↑
                    Your Model
```

---

## Quick Examples

### Example 1: Default (Recommended)
```python
spots = extractor.fetch_data()  # Automatically excludes today
```

### Example 2: Explicitly Exclude Today
```python
spots = extractor.fetch_data(exclude_today=True)
```

### Example 3: Last 30 Days Only
```python
spots = extractor.fetch_data(exclude_today=True, days_back=30)
```

### Example 4: Last 7 Days Only
```python
spots = extractor.fetch_data(exclude_today=True, days_back=7)
```

### Example 5: Include Today (Use Carefully!)
```python
spots = extractor.fetch_data(exclude_today=False)  # ⚠️ For extraction only, not training
```

---

## Key Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `exclude_today` | `True` | ✅ Don't train on today |
| `exclude_today` | `False` | ⚠️ Include today (for prediction features only) |
| `days_back` | `30` | Only use last 30 days |
| `days_back` | `None` | Use all available history |
| `limit` | `500` | Max spots to fetch |

---

## The Right Way (✅)

### Training on Historical Data
```python
# Extract only past days
spots = extractor.fetch_data(exclude_today=True, days_back=60)

# Extract features
extractor.group_by_date(spots)
X_train = extractor.extract_daily_features()

# Train your model
model.fit(X_train, y_train)
```

### Predicting Tomorrow
```python
# Get today's features (separate extraction)
extractor_today = DailyFeatureExtractor()
spots_today = extractor_today.fetch_data(exclude_today=False)
# ... extract features from today only ...
X_today = extractor_today.extract_daily_features()

# Make prediction
prediction = model.predict(X_today)
```

---

## The Wrong Way (❌)

### DON'T: Train on Today's Data
```python
# BAD! Data leakage
spots = extractor.fetch_data(exclude_today=False)  # Includes today!
X = extractor.extract_daily_features()
model.fit(X, y)  # Today is in training data

# Now prediction fails because model saw the answer
prediction = model.predict(today)  # Cheating!
```

---

## Common Scenarios

### Daily Forecasting (Predict Tomorrow)
```python
# Train on 60 previous days, predict tomorrow
spots = extractor.fetch_data(exclude_today=True, days_back=60)
```

### Weekly Pattern Analysis
```python
# Last 4 weeks for pattern detection
spots = extractor.fetch_data(exclude_today=True, days_back=28)
```

### Monthly Forecasting
```python
# 90 days of historical data
spots = extractor.fetch_data(exclude_today=True, days_back=90)
```

### Real-time Anomaly Detection
```python
# Baseline from 60 historical days
baseline = extractor.fetch_data(exclude_today=True, days_back=60)
# Compare today to baseline (extract separately)
today = extractor.fetch_data(exclude_today=False)
```

---

## Status Messages You'll See

```
✓ Fetched 2500 spots from API (historical data)
  Note: Excluded today (2025-11-07) - using only previous days
```

means: ✅ Code worked correctly, today was excluded

```
✓ Fetched 1200 spots from API (historical data)
  Note: Excluded today (2025-11-07) - using only previous days
  Note: Limited to 30 days back (since 2025-10-08)
```

means: ✅ Code worked, today excluded, 30-day window applied

---

## Why This Matters

**Data Leakage** = When model trains on data it's supposed to predict

```
Problem: Model trained on today's data
  → Can't really predict tomorrow (it's not in training)
  → Fails when you try to use it
  → Looks great in tests, terrible in production

Solution: Train ONLY on past data
  → Model learns to forecast from history
  → Realistic accuracy in testing
  → Works in production
```

---

## Default Behavior

```python
# OLD CODE (before update)
spots = extractor.fetch_data()
# Included all data, including today ⚠️

# NEW CODE (recommended)
spots = extractor.fetch_data()
# Now excludes today by default ✅
# Safer for machine learning workflows
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No data returned | Try removing `days_back` limit |
| Getting today's data | Check `exclude_today` is `True` |
| Not enough training data | Increase `days_back` value |
| Need today for features | Use separate call with `exclude_today=False` |

---

## One-Liner Reference

```python
# Daily forecasting (safe)
fetch_data(exclude_today=True, days_back=30)

# All history (safe)
fetch_data(exclude_today=True)

# Include today (careful!)
fetch_data(exclude_today=False)

# Last week only
fetch_data(exclude_today=True, days_back=7)
```

---

## Remember

✅ **Always use `exclude_today=True` for training**

❌ **Never train on the data you want to predict**

---

See `HISTORICAL_DATA_EXTRACTION.md` for detailed documentation.

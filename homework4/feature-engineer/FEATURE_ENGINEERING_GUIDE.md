# Feature Engineering Guide

## What is Feature Engineering?

Feature engineering is the process of selecting, transforming, and creating features (input variables) from raw data to improve machine learning model performance. It bridges the gap between raw data and what algorithms can learn from effectively.

In essence: **Garbage in, garbage out** — the quality of your features directly determines the quality of your model's predictions.

---

## Core Components of Feature Engineering

### 1. Feature Selection
**Definition**: Choosing which features are relevant and removing irrelevant or redundant ones.

**Why it matters**:
- Reduces noise in the model
- Improves computational efficiency
- Prevents overfitting
- Increases interpretability

**Example from our project**:
```
Original bands: 6m, 10m, 12m, 15m, 17m, 20m, 40m, 80m, 160m (9 bands)
Equipment bands: 6m, 10m, 12m, 15m, 17m, 20m, 40m (7 bands)
Decision: Remove 80m and 160m (not relevant to equipment)
Result: Cleaner input, less noise for neural network
```

### 2. Feature Extraction
**Definition**: Deriving meaningful features from raw data through aggregation, transformation, or calculation.

**Why it matters**:
- Converts unstructured/sparse raw data into dense, meaningful representations
- Captures important patterns and relationships
- Reduces dimensionality while preserving information

**Example from our project**:
```
Raw data: 100+ individual radio spots per day
  - Each spot: frequency, band, signal quality, mode, time

Extracted features per day:
  1. average_frequency_mhz - Central tendency of activity
  2. num_bands_active - Diversity of propagation
  3. total_spots - Activity level
  4. avg_signal_quality - Propagation conditions
  5. signal_quality_std - Consistency/variability
  6. cw_percentage - Mode preference
  7. ssb_percentage - Mode preference
  8. activity_hours_count - Duration of activity
  9. peak_hour - Best propagation window
  10. 40m_band_percentage - Band-specific activity

Result: One 10-dimensional vector per day instead of 100+ raw spots
```

### 3. Feature Transformation
**Definition**: Converting features into forms more suitable for machine learning algorithms.

**Common transformations**:

#### Normalization (Min-Max Scaling)
Scales features to a fixed range [0, 1]:
```
x_normalized = (x - x_min) / (x_max - x_min)
```

**Why use it**:
- Ensures features have equal influence (no single feature dominates due to scale)
- Required by some algorithms (neural networks, distance-based methods)
- Improves convergence speed during training

**Example from our project**:
```
Raw: num_bands_active ranges 0-7
Normalized: 0 bands → 0.0, 7 bands → 1.0

Raw: activity_hours_count ranges 0-24
Normalized: 0 hours → 0.0, 24 hours → 1.0

Result: All 10 features now in [0, 1] range, equal footing
```

#### Standardization (Z-score)
Converts features to have mean=0 and std=1:
```
x_standardized = (x - x_mean) / x_std
```

#### Encoding
Converts categorical data to numeric:
- One-hot encoding: `CW → [1,0]`, `SSB → [0,1]`
- Label encoding: `CW → 0`, `SSB → 1`

### 4. Feature Creation
**Definition**: Generating new features by combining or deriving from existing ones.

**Techniques**:

#### Domain Knowledge Combination
```python
# From our DAILY_PROPAGATION_GUIDE.md:
propagation_quality = (X[:, 3] - X[:, 4]) / 10  # signal_quality - variability
activity_intensity = X[:, 2] * X[:, 8] / 24     # total_spots * hours / max_hours
band_preference = X[:, 9] - (1 - X[:, 9])       # 40m bias vs other bands
```

#### Time-based Features
- Hour of day, day of week, month, season
- Time since last activity
- Moving averages, trends

#### Statistical Features
- Mean, median, standard deviation
- Min, max, range
- Percentiles, quartiles

#### Interaction Features
- Product of two features: `frequency * signal_quality`
- Ratio: `cw_percentage / ssb_percentage`
- Difference: `peak_hour - average_hour`

### 5. Feature Deletion
**Definition**: Removing features that don't contribute to model performance.

**Reasons to delete features**:
- Not relevant to the problem domain
- Highly correlated with other features (redundancy)
- Sparse (mostly missing or zero values)
- Constant or near-constant values
- Introduce data leakage

**Example from our project**:
```
Before: Tracked 80m and 160m bands in feature 10 (long_wave_percentage)
After: Track only 40m band in feature 10 (40m_band_percentage)

Why? Equipment can't use 80m/160m, so:
✗ They're irrelevant noise
✗ They don't represent actual equipment capability
✗ They distract the model from meaningful patterns
✓ Removing them improves signal-to-noise ratio
```

---

## Feature Engineering Workflow

```
Raw Data
   ↓
[1] Exploratory Analysis
    - Understand data distributions
    - Identify outliers
    - Find missing values
    - Explore relationships
   ↓
[2] Feature Selection
    - Remove irrelevant features
    - Identify redundant features
    - Domain-driven filtering
   ↓
[3] Feature Extraction
    - Aggregate raw data
    - Derive meaningful metrics
    - Create composite features
   ↓
[4] Feature Transformation
    - Normalization/Standardization
    - Encoding categorical data
    - Handle outliers
   ↓
[5] Feature Creation
    - Domain-driven combinations
    - Interaction terms
    - Time-based features
   ↓
[6] Feature Engineering Validation
    - Statistical analysis
    - Correlation analysis
    - Feature importance scores
   ↓
Machine Learning Model
   ↓
[7] Model Performance Feedback
    (May reveal need for more features)
```

---

## Feature Engineering Best Practices

### ✅ DO:

1. **Understand your domain**
   - Know what the features represent
   - Incorporate domain expertise
   - Example: Knowing ham radio propagation means we focus on bands and times

2. **Start simple**
   - Begin with obvious features
   - Add complexity only if needed
   - Example: Start with basic frequency averages before complex interactions

3. **Document your choices**
   - Record why you selected each feature
   - Note transformations applied
   - Example: Our DAILY_PROPAGATION_GUIDE.md explains each of 10 features

4. **Validate independently**
   - Use train/test splits before feature engineering
   - Test feature contribution separately
   - Example: Run daily_extractor on different date ranges

5. **Handle missing data thoughtfully**
   - Don't just delete rows
   - Consider imputation strategies
   - Understand the impact

6. **Scale appropriately**
   - Different algorithms need different scaling
   - Neural networks: normalization [0,1] or [-1,1]
   - Tree-based: often no scaling needed

### ❌ DON'T:

1. **Include features you don't understand**
   - If you can't explain why it matters, it probably doesn't
   - Example: Don't include 80m/160m data if your equipment can't use it

2. **Over-engineer**
   - More features ≠ better model
   - Creates overfitting and computational waste
   - Example: We use 10 features per day, not 100+

3. **Leak information from test set**
   - Calculate normalization parameters from training data only
   - Example: Min-Max scaling should use training set min/max

4. **Ignore feature correlations**
   - Highly correlated features provide redundant information
   - Example: If `avg_signal_quality` and `signal_quality_std` are perfectly correlated, keep only one

5. **Forget about business logic**
   - Features must align with real-world constraints
   - Example: Equipment operating bands, propagation physics

6. **Neglect feature scaling in neural networks**
   - Unnormalized features can cause training instability
   - Example: Frequency in MHz (6-7) vs. band count (0-7) would create imbalance

---

## Feature Engineering in Our Project

### The Ham Radio Feature Engineering Challenge

**Raw Input**: API returns individual radio spot records
```
{
  "callsign": "K1ABC",
  "band": "40m",
  "frequency": 7.150,
  "signal_quality": 7,
  "mode": "SSB",
  "time": "2025-11-07T14:30:00Z"
}
```

**Problem**: 100+ records per day, inconsistent timing, no clear structure
**Goal**: Create daily neural network input vectors

### Our Feature Engineering Decisions

1. **Selection**: Keep bands 6m-40m, discard 80m-160m
   - Rationale: Equipment constraint
   - Impact: Reduced noise, improved focus

2. **Extraction**: Convert 100+ spots → 10 daily metrics
   - Aggregation: Total spots, average frequency, hours active
   - Statistics: Mean/std of signal quality
   - Percentages: Mode distribution, band distribution
   - Peak detection: Best hour for activity

3. **Transformation**: Normalize all features to [0,1]
   - Min-Max scaling using full data range
   - Equal feature influence in neural network
   - Faster convergence during training

4. **Structure**: One vector per day
   - Aligned with propagation analysis workflow
   - Temporal independence (can predict next day)
   - Regular time intervals (no gaps)

### Results

```
Before Feature Engineering:
- 100+ unstructured spot records
- Inconsistent information density
- No clear temporal organization
- Difficult to feed into neural network

After Feature Engineering:
- 1 vector per day
- 10 normalized features [0,1]
- Clear temporal structure (YYYY-MM-DD)
- Ready for LSTM, clustering, forecasting
```

---

## Tools and Techniques for Feature Engineering

### Python Libraries

| Library | Purpose | Use Case |
|---------|---------|----------|
| **pandas** | Data manipulation | Aggregation, grouping, transformation |
| **numpy** | Numerical operations | Calculations, normalization, statistics |
| **scikit-learn** | ML preprocessing | Scaling, encoding, feature selection |
| **scipy** | Scientific computing | Statistical analysis, distributions |
| **statsmodels** | Statistical modeling | Correlation, regression analysis |

### Feature Engineering Techniques in scikit-learn

```python
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.decomposition import PCA

# Normalization
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)

# Feature selection
selector = SelectKBest(k=5)
X_selected = selector.fit_transform(X, y)

# Dimensionality reduction
pca = PCA(n_components=5)
X_reduced = pca.fit_transform(X)
```

---

## Common Feature Engineering Mistakes

### 1. Not Understanding the Data Distribution
**Problem**: Using inappropriate transformations
```
Example: Linear scaling on highly skewed data
Result: Outliers distort the normalized range
```

**Solution**: Analyze distributions first with histograms, box plots, quartiles

### 2. Data Leakage
**Problem**: Using information from test set to create features
```
Example: Normalizing with min/max from entire dataset (training + test)
Result: Model appears better than it actually is
```

**Solution**: Calculate statistics from training set only

### 3. Creating Correlated Features
**Problem**: Redundant information wastes model capacity
```
Example: Including both average_frequency and total_active_bands
Result: Model might struggle to learn independent relationships
```

**Solution**: Calculate correlation matrix, remove highly correlated pairs

### 4. Ignoring Domain Knowledge
**Problem**: Features don't make sense in real-world context
```
Example: Including 80m/160m band data for equipment that can't use those bands
Result: Noise confuses the model, poor real-world predictions
```

**Solution**: Validate features with domain experts (or your own expertise!)

### 5. Forgetting About Test Set Purity
**Problem**: Features that only work in training data
```
Example: Creating features based on future information
Result: Can't predict forward in time
```

**Solution**: Design features using only past information

---

## Feature Engineering Metrics

### Correlation Analysis
```python
import pandas as pd

# Find highly correlated features
correlation_matrix = df.corr()
# Remove features with |correlation| > 0.95 with other features
```

### Feature Importance (Tree-based Models)
```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor()
model.fit(X, y)
importances = model.feature_importances_
# High importance = feature helps model predictions
```

### Variance Inflation Factor (VIF)
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Measure multicollinearity
vif = [variance_inflation_factor(X, i) for i in range(X.shape[1])]
# VIF > 5 indicates problematic multicollinearity
```

---

## Feature Engineering Checklist

- [ ] **Understand the problem**: What are you trying to predict?
- [ ] **Explore the data**: Distributions, outliers, missing values
- [ ] **Identify irrelevant features**: Remove based on domain knowledge
- [ ] **Extract meaningful features**: Aggregate and derive from raw data
- [ ] **Handle missing data**: Imputation or removal strategy
- [ ] **Check for correlations**: Remove redundant features
- [ ] **Transform appropriately**: Normalize, standardize, encode as needed
- [ ] **Create interaction features**: If domain-relevant
- [ ] **Validate on test set**: Ensure features work on unseen data
- [ ] **Document decisions**: Record why each feature is included
- [ ] **Monitor performance**: Validate that engineering improved results

---

## References and Further Reading

### Key Concepts
- **Andrew Ng**: "Feature engineering is the difference between good ML and great ML"
- **Kaggle**: Feature engineering competitions showcase advanced techniques
- **Feature Scaling**: Critical for distance-based algorithms (KNN, K-means) and gradient descent

### Related Topics to Study
- Data preprocessing and cleaning
- Dimensionality reduction (PCA, t-SNE)
- Automated feature engineering (AutoML)
- Time series feature engineering
- Domain-specific feature engineering (vision, NLP, audio)

### In Your Project
- **DAILY_PROPAGATION_GUIDE.md**: Details on each of your 10 features
- **daily_extractor.py**: Implementation of feature extraction
- **daily_examples.py**: Real-world usage examples with PyTorch/TensorFlow

---

## Summary

Feature engineering is both **art and science**:
- **Science**: Statistical analysis, correlation, information theory
- **Art**: Domain knowledge, intuition, creative problem-solving

Your ham radio project exemplifies good feature engineering:
✅ Domain expertise (understanding radio propagation and equipment limits)
✅ Thoughtful selection (removing irrelevant 80m/160m bands)
✅ Appropriate extraction (daily aggregation matches analysis workflow)
✅ Proper transformation (normalization for neural networks)
✅ Clear documentation (explaining each of 10 features)

The goal is always the same: **Convert raw data into features that help your model learn meaningful patterns for the problem you're solving.**

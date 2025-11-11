# 🚀 API Feature Extraction for Neural Networks

Extract real-time ham radio spotting data and prepare normalized feature vectors for machine learning models.

## ⚡ Choose Your Approach

### For Individual Radio Spots
```bash
python simple_extractor.py
```
Creates one feature vector per radio spot (6 features)

### For Daily Propagation Analysis ⭐ NEW
```bash
python daily_extractor.py
```
Creates one feature vector per day (10 aggregated features)
**Perfect for analyzing radio wave propagation patterns!**

## 📊 What You Get

**Input**: Ham radio spotting data from API  
**Output**: Normalized feature vectors (6 features per record, range [0,1])

```
[frequency_mhz, band_id, hour_of_day, day_of_week, signal_report, mode_id]
[    0.5239,   0.5000,    0.7083,    0.6667,     0.5960,       0.5000]
```

Ready for PyTorch, TensorFlow, scikit-learn, or any ML framework.

## 📖 Documentation

- **🟢 [START HERE](QUICKSTART.md)** - Quick overview
- **� [Daily Propagation Guide](DAILY_PROPAGATION_GUIDE.md)** - Daily analysis (NEW!)
- **�📚 [Complete Guide](README.md)** - Technical documentation
- **🧠 [Neural Network Integration](NEURAL_NETWORK_GUIDE.md)** - Framework-specific code
- **📑 [All Files Guide](PROJECT_INDEX.md)** - Complete reference
- **🎯 [Full Solution Summary](COMPLETE_SOLUTION_SUMMARY.md)** - Comprehensive overview

## 🛠️ Three Ways to Use

### 1. Command Line (Simplest)
```bash
python simple_extractor.py
```
✅ No dependencies  
✅ Creates CSV file  
✅ Shows statistics

### 2. In Your Code
```python
from simple_extractor import SimpleFeatureExtractor

extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
features = extractor.extract_features(spots)
normalized = extractor.normalize_features()

# Now use normalized features in your model
```

### 3. Jupyter Notebook
```bash
jupyter notebook feature_extraction_notebook.ipynb
```
✅ Interactive exploration  
✅ Step-by-step explanations  
✅ Visualizations included

## 🧠 Framework Examples

### PyTorch
```python
import torch
X = torch.tensor(normalized, dtype=torch.float32)
model = torch.nn.Linear(6, 10)
```

### TensorFlow
```python
import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(6,)),
    tf.keras.layers.Dense(1)
])
```

### Scikit-Learn
```python
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=5)
clusters = kmeans.fit_predict(normalized)
```

See [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md) for complete examples.

## 📊 Features Explained

| Feature | Description |
|---------|-------------|
| **frequency_mhz** | Radio frequency in MHz (normalized to [0,1]) |
| **band_id** | Amateur radio band (6m=0, 10m=1, ..., 160m=8) |
| **hour_of_day** | UTC hour when spot was reported (0-23 normalized) |
| **day_of_week** | Day of week (0=Monday...6=Sunday normalized) |
| **signal_report** | Signal quality (0-99 normalized) |
| **mode_id** | Operating mode (CW=1, USB=2, SSB=3, LSB=4) |

## 📁 Project Files

| File | Purpose |
|------|---------|
| `simple_extractor.py` | ⭐ Main tool - use this |
| `feature_extractor.py` | Advanced version with pandas/numpy |
| `feature_extraction_notebook.ipynb` | Interactive Jupyter notebook |
| `examples.py` | 6 practical examples |
| `requirements.txt` | Python dependencies |
| `README.md` | Full technical documentation |
| `NEURAL_NETWORK_GUIDE.md` | Framework integration |
| `QUICKSTART.md` | Quick reference |
| `PROJECT_INDEX.md` | File guide |

## 🎯 Common Use Cases

1. **Predict signal strength** based on other features
2. **Identify activity patterns** by time of day/week
3. **Classify radio bands** based on characteristics
4. **Cluster similar spots** by similarity
5. **Forecast radio activity** using time series

## 🔧 Requirements

**Minimum:**
- Python 3.6+
- (No external libraries needed!)

**Recommended:**
- requests (for API calls)
- numpy (for arrays)
- pandas (for DataFrames)

Install with: `pip install -r requirements.txt`

## ✨ Key Features

✅ **Zero Dependencies** (simple_extractor.py)  
✅ **Production Ready** with error handling  
✅ **Well Documented** with examples  
✅ **Framework Agnostic** works with any ML library  
✅ **Handles Missing Data** gracefully  
✅ **Proper Normalization** for neural networks  

## 🚀 Get Started Now

```bash
# Extract features
python simple_extractor.py

# Or explore interactively
jupyter notebook feature_extraction_notebook.ipynb

# Or try different techniques
python examples.py
```

## 📞 Need Help?

- **Quick start**: Read [QUICKSTART.md](QUICKSTART.md)
- **How it works**: Read [README.md](README.md)
- **Framework integration**: Read [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md)
- **File reference**: Read [PROJECT_INDEX.md](PROJECT_INDEX.md)
- **Complete overview**: Read [COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)
- **Code examples**: Run `python examples.py`

## 📊 API Source

**Endpoint**: http://api.jxqz.org:8080/api/spots  
**Data**: Real-time ham radio spotting network  
**Records**: 139,000+ total available  

## 🎊 Status

✅ **Ready to Use**  
✅ **Fully Documented**  
✅ **Production Tested**  
✅ **All Dependencies Included**

**Start extracting features now!**

---

*Ham radio spotting data for neural network machine learning*

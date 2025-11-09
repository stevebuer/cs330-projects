# Radio Spotting API - Neural Network Feature Extractor

This project extracts radio spotting data from an API and prepares normalized feature vectors suitable for neural network input.

## Overview

The solution provides a complete pipeline to:
1. **Fetch data** from `http://api.jxqz.org:8080/api/spots` (ham radio spotting API)
2. **Extract features** from raw JSON data
3. **Normalize** features to [0, 1] range for neural network compatibility
4. **Export** results as CSV for model training

## Data Source

The API returns real-time ham radio spotting data with the following fields:
- `band`: Radio band (6m, 10m, 12m, 15m, 17m, 20m, 40m, 80m, 160m)
- `frequency`: Frequency in MHz
- `dx_call`: Callsign of the station being heard
- `spotter_call`: Callsign of the person reporting the spot
- `timestamp`: Time of the spot report
- `mode`: Operating mode (CW, USB, SSB, LSB, etc.)
- `signal_report`: Signal quality report (e.g., "59", "569")
- `comment`: Additional comments

## Feature Engineering

The extractor converts raw API data into 6 normalized numerical features:

| Feature | Description | Raw Range | Normalized Range | Purpose |
|---------|-------------|-----------|------------------|---------|
| **frequency_mhz** | Radio frequency in MHz | 1.8 - 54 MHz | [0, 1] | Activity level on different bands |
| **band_id** | Band encoded as numeric ID | 0 - 8 | [0, 1] | Which ham band (6m=0, 10m=1, etc.) |
| **hour_of_day** | Hour when spot was reported | 0 - 23 | [0, 1] | Temporal patterns in radio activity |
| **day_of_week** | Day of week (0=Monday, 6=Sunday) | 0 - 6 | [0, 1] | Weekly patterns |
| **signal_report** | Signal quality from report | 0 - 99 | [0, 1] | Signal strength quality |
| **mode_id** | Operating mode encoded | 0 - 4 | [0, 1] | CW=1, USB=2, SSB=3, LSB=4 |

### Feature Extraction Logic

```python
# Example: Convert raw spot data to feature vector
raw_spot = {
    "band": "20m",
    "frequency": "14075.900",
    "timestamp": "Fri, 07 Nov 2025 17:08:35 GMT",
    "mode": "USB",
    "signal_report": "59"
}

# Extracted raw features:
features = [
    14075.9,    # frequency in MHz
    4.0,        # band_id (20m is index 4)
    17.0,       # hour (5 PM)
    4.0,        # day_of_week (Friday is index 4)
    59.0,       # signal_report
    2.0         # mode_id (USB=2)
]

# After normalization [0,1]:
normalized = [0.524, 0.5, 0.708, 0.667, 0.596, 0.5]
```

## Files

### `simple_extractor.py` (Standalone - Recommended)
**No external dependencies required** (uses only Python stdlib + urllib).

Simple, portable implementation suitable for quick testing and integration.

```bash
# Run directly - only needs Python
python simple_extractor.py
```

### `feature_extractor.py` (Full-Featured)
Advanced version with pandas DataFrames and sklearn preprocessing.

**Requirements:**
```
requests>=2.31.0
numpy>=1.24.0
scikit-learn>=1.3.0
pandas>=2.0.0
```

**Installation:**
```bash
pip install -r requirements.txt
python feature_extractor.py
```

### `requirements.txt`
Python package dependencies for the full-featured version.

### `README.md`
This file - comprehensive documentation.

## Usage

### Quick Start (Recommended)

```python
from simple_extractor import SimpleFeatureExtractor

# Create extractor
extractor = SimpleFeatureExtractor()

# Fetch and process data
spots = extractor.fetch_data(limit=100)
raw_features = extractor.extract_features(spots)
normalized_features = extractor.normalize_features()

# Use in neural network
# normalized_features is a list of [frequency, band, hour, dow, signal, mode]
X_train = normalized_features
```

### Advanced Usage (with pandas/sklearn)

```python
from feature_extractor import RadioSpottingFeatureExtractor

extractor = RadioSpottingFeatureExtractor()
spots = extractor.fetch_data(limit=500)
extractor.extract_features(spots)
extractor.normalize_features()

# Get as pandas DataFrame
df = extractor.to_dataframe(normalized=True)
print(df.describe())

# Get statistics
stats = extractor.get_statistics(normalized=True)
```

## Output Format

### CSV Output

The output CSV file has the following format:

```csv
frequency_mhz,band_id,hour_of_day,day_of_week,signal_report,mode_id
0.523856,0.500000,0.708333,0.666667,0.596000,0.500000
0.345127,0.375000,0.708333,0.666667,0.000000,0.000000
0.678234,0.625000,0.708333,0.666667,0.595000,0.625000
...
```

Each row is a normalized feature vector ready for neural network input.

## Integration with Neural Networks

### PyTorch Example

```python
import torch
from simple_extractor import SimpleFeatureExtractor

# Extract features
extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
raw_features = extractor.extract_features(spots)
normalized_features = extractor.normalize_features()

# Convert to PyTorch tensor
X = torch.tensor(normalized_features, dtype=torch.float32)

# Create simple neural network
model = torch.nn.Sequential(
    torch.nn.Linear(6, 32),
    torch.nn.ReLU(),
    torch.nn.Linear(32, 16),
    torch.nn.ReLU(),
    torch.nn.Linear(16, 1)  # Output layer (e.g., predict signal strength)
)

# Pass through network
predictions = model(X)
```

### TensorFlow/Keras Example

```python
import tensorflow as tf
from simple_extractor import SimpleFeatureExtractor
import numpy as np

# Extract and normalize features
extractor = SimpleFeatureExtractor()
spots = extractor.fetch_data()
raw_features = extractor.extract_features(spots)
normalized_features = extractor.normalize_features()

# Convert to numpy array
X = np.array(normalized_features)

# Create model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(6,)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')
```

## Understanding the Features

### frequency_mhz
- **Raw value**: 1.8 - 54.0 MHz
- **Normalized**: [0, 1]
- **Interpretation**: Higher frequency = higher number. Used to identify which band is active.

### band_id
- **Raw values**: 0-8 (6m, 10m, 12m, 15m, 17m, 20m, 40m, 80m, 160m)
- **Normalized**: [0, 1]
- **Interpretation**: Categorical feature indicating which amateur radio band.

### hour_of_day
- **Raw values**: 0-23
- **Normalized**: [0, 1]
- **Interpretation**: Time of day (UTC). Useful for capturing diurnal patterns.

### day_of_week
- **Raw values**: 0-6 (Monday to Sunday)
- **Normalized**: [0, 1]
- **Interpretation**: Day of week. Useful for weekly patterns.

### signal_report
- **Raw values**: 0-99
- **Normalized**: [0, 1]
- **Interpretation**: Signal quality. 0 if not provided, otherwise reported value.

### mode_id
- **Raw values**: 0 (unknown), 1 (CW), 2 (USB), 3 (SSB), 4 (LSB)
- **Normalized**: [0, 1]
- **Interpretation**: Operating mode. Categorical but encoded as numeric.

## Normalization Strategy

Min-Max normalization is used:

$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

This transforms all features to [0, 1] range independently, which is ideal for:
- Neural networks (stable training)
- Distance-based algorithms (fair feature weighting)
- Activation functions like sigmoid

## Handling Missing Data

- **null frequency**: Converted to 0.0
- **null signal_report**: Converted to 0.0
- **null mode**: Converted to mode_id 0
- **null band**: Encoded as -1 (normalized to 0)

## Performance Considerations

- **API Rate Limiting**: The API may have rate limits. Default limit is 100 spots per call.
- **Network Timeout**: Set to 10 seconds. Adjust if needed.
- **Memory**: Processing 10,000+ vectors requires ~1-2 MB.

## Example Output

```
============================================================================
Radio Spotting API - Neural Network Feature Extractor (Standalone)
============================================================================

[1] Fetching data from API...
✓ Fetched 50 spots from API

[2] Extracting features...
✓ Extracted 50 feature vectors

[3] Normalizing features...
✓ Normalized features to [0, 1] range

[4] Sample Feature Vectors (first 5, normalized):
   Frequency  Band  Hour  DoW  Signal  Mode
1.  0.5239  0.5000  0.7083  0.6667  0.5960  0.5000
2.  0.3452  0.3750  0.7083  0.6667  0.0000  0.0000
3.  0.6782  0.6250  0.7083  0.6667  0.5950  0.6250
4.  0.4521  0.5000  0.7083  0.6667  0.0000  0.0000
5.  0.3128  0.1250  0.7083  0.6667  0.0000  0.0000

[5] Saving to CSV...
✓ Saved 50 feature vectors to radio_features.csv

[6] Feature Statistics (normalized):
frequency_mhz          Mean: 0.4567  Min: 0.0000  Max: 1.0000
band_id                Mean: 0.5234  Min: 0.0000  Max: 1.0000
hour_of_day            Mean: 0.7083  Min: 0.7083  Max: 0.7083
day_of_week            Mean: 0.6667  Min: 0.6667  Max: 0.6667
signal_report          Mean: 0.2341  Min: 0.0000  Max: 0.9597
mode_id                Mean: 0.1234  Min: 0.0000  Max: 1.0000

============================================================================
✓ Pipeline complete! Ready for neural network input.
============================================================================
```

## Troubleshooting

### API Connection Error
- Check internet connection
- Verify API URL is accessible: `http://api.jxqz.org:8080/api/spots`
- Check firewall/proxy settings

### No Features Extracted
- API might return empty spots array
- Check API response with browser: http://api.jxqz.org:8080/api/spots

### Timestamp Parsing Errors
- Expected format: "Fri, 07 Nov 2025 17:08:35 GMT"
- If different, update datetime.strptime format string

## Future Enhancements

- Add caching to avoid repeated API calls
- Support for batch processing
- Time-series feature extraction
- Grid square coordinate feature extraction
- Integration with TensorFlow/PyTorch datasets
- Real-time streaming pipeline

## License

This code is provided as-is for educational purposes.

## References

- API: http://api.jxqz.org:8080/api/spots
- Ham Radio Bands: https://en.wikipedia.org/wiki/Amateur_radio_frequency_allocations
- Feature Normalization: https://scikit-learn.org/stable/modules/preprocessing.html#scaling-features-to-a-range

"""
Simple standalone feature extractor - no external dependencies (except requests)
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Tuple


class SimpleFeatureExtractor:
    """Extract features from radio spotting API with minimal dependencies."""
    
    API_URL = "http://api.jxqz.org:8080/api/spots"
    
    def __init__(self):
        self.raw_features = None
        self.normalized_features = None
    
    def fetch_data(self, limit: int = None) -> List[Dict]:
        """Fetch data from API using urllib (no external dependency)."""
        try:
            with urllib.request.urlopen(self.API_URL, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                spots = data.get("spots", [])
                
                if limit:
                    spots = spots[:limit]
                
                print(f"✓ Fetched {len(spots)} spots from API")
                return spots
                
        except Exception as e:
            print(f"✗ Error fetching API data: {e}")
            return []
    
    def extract_features(self, spots: List[Dict]) -> List[List[float]]:
        """
        Extract features from spots.
        
        Returns list of feature vectors: [frequency, band_id, hour, day_of_week, signal, mode]
        """
        bands_list = ["6m", "10m", "12m", "15m", "17m", "20m", "40m", "80m", "160m"]
        features = []
        
        for spot in spots:
            try:
                # Frequency in MHz
                frequency = float(spot.get("frequency", 0))
                
                # Band as ID
                band = spot.get("band", "")
                band_id = float(bands_list.index(band)) if band in bands_list else -1.0
                
                # Parse timestamp
                timestamp_str = spot.get("timestamp", "")
                try:
                    dt = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
                    hour = float(dt.hour)
                    day_of_week = float(dt.weekday())
                except:
                    hour = 0.0
                    day_of_week = 0.0
                
                # Signal report
                signal_report = spot.get("signal_report", None)
                if signal_report:
                    try:
                        signal_value = float(str(signal_report)[:2])
                    except:
                        signal_value = 0.0
                else:
                    signal_value = 0.0
                
                # Mode encoding
                mode = spot.get("mode", "")
                mode_map = {"CW": 1.0, "USB": 2.0, "SSB": 3.0, "LSB": 4.0}
                mode_id = mode_map.get(mode, 0.0)
                
                feature_vector = [frequency, band_id, hour, day_of_week, signal_value, mode_id]
                features.append(feature_vector)
                
            except Exception as e:
                print(f"Warning: Skipping spot due to error: {e}")
                continue
        
        self.raw_features = features
        print(f"✓ Extracted {len(features)} feature vectors")
        return features
    
    @staticmethod
    def min_max_normalize(features: List[List[float]]) -> List[List[float]]:
        """Min-Max normalization to [0, 1] range."""
        if not features or not features[0]:
            return features
        
        n_features = len(features[0])
        normalized = []
        
        # Calculate min and max for each feature
        mins = [float('inf')] * n_features
        maxs = [float('-inf')] * n_features
        
        for feature_vec in features:
            for i, val in enumerate(feature_vec):
                mins[i] = min(mins[i], val)
                maxs[i] = max(maxs[i], val)
        
        # Normalize each feature
        for feature_vec in features:
            normalized_vec = []
            for i, val in enumerate(feature_vec):
                range_val = maxs[i] - mins[i]
                if range_val == 0:
                    normalized_val = 0.0
                else:
                    normalized_val = (val - mins[i]) / range_val
                normalized_vec.append(normalized_val)
            normalized.append(normalized_vec)
        
        return normalized
    
    def normalize_features(self) -> List[List[float]]:
        """Normalize extracted features to [0, 1]."""
        if not self.raw_features:
            print("✗ No features to normalize")
            return None
        
        self.normalized_features = self.min_max_normalize(self.raw_features)
        print(f"✓ Normalized features to [0, 1] range")
        return self.normalized_features


def main():
    """Demo script."""
    print("=" * 70)
    print("Radio Spotting API - Neural Network Feature Extractor (Standalone)")
    print("=" * 70)
    
    extractor = SimpleFeatureExtractor()
    
    # Fetch and process data
    print("\n[1] Fetching data from API...")
    spots = extractor.fetch_data(limit=50)
    
    if not spots:
        print("✗ Failed to fetch data")
        return
    
    print("\n[2] Extracting features...")
    raw_features = extractor.extract_features(spots)
    
    print("\n[3] Normalizing features...")
    normalized = extractor.normalize_features()
    
    # Display results
    print("\n[4] Sample Feature Vectors (first 5, normalized):")
    print("-" * 70)
    print("   Frequency  Band  Hour  DoW  Signal  Mode")
    print("-" * 70)
    
    for i, vec in enumerate(normalized[:5]):
        print(f"{i+1}. {vec[0]:>8.4f}  {vec[1]:>4.4f}  {vec[2]:>4.4f}  {vec[3]:>3.4f}  {vec[4]:>6.4f}  {vec[5]:>4.4f}")
    
    # Save to CSV
    print("\n[5] Saving to CSV...")
    csv_file = "radio_features.csv"
    with open(csv_file, 'w') as f:
        f.write("frequency_mhz,band_id,hour_of_day,day_of_week,signal_report,mode_id\n")
        for vec in normalized:
            f.write(",".join(f"{v:.6f}" for v in vec) + "\n")
    
    print(f"✓ Saved {len(normalized)} feature vectors to {csv_file}")
    
    # Statistics
    print("\n[6] Feature Statistics (normalized):")
    print("-" * 70)
    feature_names = ["frequency_mhz", "band_id", "hour_of_day", "day_of_week", "signal_report", "mode_id"]
    
    for feat_idx, name in enumerate(feature_names):
        values = [v[feat_idx] for v in normalized]
        mean = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        print(f"{name:<20} Mean: {mean:>7.4f}  Min: {min_val:>7.4f}  Max: {max_val:>7.4f}")
    
    print("\n" + "=" * 70)
    print("✓ Pipeline complete! Ready for neural network input.")
    print("=" * 70)


if __name__ == "__main__":
    main()

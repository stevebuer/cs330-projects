"""
Feature extraction and normalization from radio spotting API.
Prepares data for neural network input.
"""

import requests
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
from sklearn.preprocessing import MinMaxScaler
import pandas as pd


class RadioSpottingFeatureExtractor:
    """Extract and normalize features from radio spotting API."""
    
    API_URL = "http://api.jxqz.org:8080/api/spots"
    
    # Define band frequency ranges (in MHz)
    BAND_FREQUENCIES = {
        "6m": (50.0, 54.0),
        "10m": (28.0, 29.7),
        "12m": (24.89, 24.99),
        "15m": (21.0, 21.45),
        "17m": (18.068, 18.168),
        "20m": (14.0, 14.35),
        "40m": (7.0, 7.3),
        "80m": (3.5, 4.0),
        "160m": (1.8, 2.0),
    }
    
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.raw_features = None
        self.normalized_features = None
    
    def fetch_data(self, limit: int = None) -> List[Dict]:
        """
        Fetch radio spotting data from API.
        
        Args:
            limit: Maximum number of spots to fetch. None for all.
            
        Returns:
            List of spot dictionaries from API response.
        """
        try:
            response = requests.get(self.API_URL)
            response.raise_for_status()
            data = response.json()
            spots = data.get("spots", [])
            
            if limit:
                spots = spots[:limit]
            
            print(f"✓ Fetched {len(spots)} spots from API")
            return spots
            
        except requests.RequestException as e:
            print(f"✗ Error fetching API data: {e}")
            return []
    
    def extract_features(self, spots: List[Dict]) -> np.ndarray:
        """
        Extract numeric features from raw spot data.
        
        Features extracted:
        1. Frequency (MHz)
        2. Band encoded as numeric (6m=0, 10m=1, ..., 160m=8)
        3. Hour of timestamp (0-23)
        4. Day of week (0-6, where 0=Monday)
        5. Signal report (0-99, or 0 if null)
        6. Mode encoded (CW=1, USB=2, SSB=3, LSB=4, other=0)
        
        Args:
            spots: List of spot dictionaries from API.
            
        Returns:
            numpy array of shape (n_spots, n_features) with raw feature values.
        """
        features = []
        band_list = list(self.BAND_FREQUENCIES.keys())
        
        for spot in spots:
            try:
                # Extract frequency
                frequency = float(spot.get("frequency", 0))
                
                # Encode band
                band = spot.get("band", "")
                band_encoded = band_list.index(band) if band in band_list else -1
                
                # Parse timestamp
                timestamp_str = spot.get("timestamp", "")
                try:
                    # Example: "Fri, 07 Nov 2025 17:08:35 GMT"
                    dt = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
                    hour = dt.hour
                    day_of_week = dt.weekday()
                except:
                    hour = 0
                    day_of_week = 0
                
                # Extract signal report
                signal_report = spot.get("signal_report", None)
                if signal_report:
                    try:
                        # Signal report format can be "59", "569", etc.
                        signal_value = float(str(signal_report)[:2])
                    except:
                        signal_value = 0
                else:
                    signal_value = 0
                
                # Encode mode
                mode = spot.get("mode", "")
                mode_map = {"CW": 1, "USB": 2, "SSB": 3, "LSB": 4}
                mode_encoded = mode_map.get(mode, 0)
                
                # Compile feature vector
                feature_vector = [
                    frequency,
                    band_encoded,
                    hour,
                    day_of_week,
                    signal_value,
                    mode_encoded,
                ]
                
                features.append(feature_vector)
                
            except Exception as e:
                print(f"Warning: Could not extract features from spot: {e}")
                continue
        
        self.raw_features = np.array(features)
        print(f"✓ Extracted {len(features)} feature vectors ({len(features[0])} features each)")
        return self.raw_features
    
    def normalize_features(self, features: np.ndarray = None) -> np.ndarray:
        """
        Normalize features to [0, 1] range using MinMaxScaler.
        
        Args:
            features: Feature array. If None, uses self.raw_features.
            
        Returns:
            Normalized numpy array of same shape.
        """
        if features is None:
            features = self.raw_features
        
        if features is None or len(features) == 0:
            print("✗ No features to normalize")
            return None
        
        # Apply normalization
        normalized = self.scaler.fit_transform(features)
        self.normalized_features = normalized
        
        print(f"✓ Normalized features to [0, 1] range")
        return normalized
    
    def get_feature_names(self) -> List[str]:
        """Return names of extracted features."""
        return [
            "frequency_mhz",
            "band_encoded",
            "hour_of_day",
            "day_of_week",
            "signal_report",
            "mode_encoded"
        ]
    
    def to_dataframe(self, normalized: bool = True) -> pd.DataFrame:
        """
        Convert features to pandas DataFrame.
        
        Args:
            normalized: If True, use normalized features; else raw features.
            
        Returns:
            DataFrame with feature columns.
        """
        features = self.normalized_features if normalized else self.raw_features
        
        if features is None:
            return None
        
        df = pd.DataFrame(
            features,
            columns=self.get_feature_names()
        )
        return df
    
    def get_statistics(self, normalized: bool = True) -> Dict:
        """
        Get statistics about extracted features.
        
        Args:
            normalized: If True, analyze normalized features; else raw.
            
        Returns:
            Dictionary with statistics.
        """
        features = self.normalized_features if normalized else self.raw_features
        
        if features is None:
            return {}
        
        stats = {
            "n_samples": features.shape[0],
            "n_features": features.shape[1],
            "mean": np.mean(features, axis=0),
            "std": np.std(features, axis=0),
            "min": np.min(features, axis=0),
            "max": np.max(features, axis=0),
        }
        return stats


def main():
    """Demo script showing the full pipeline."""
    print("=" * 60)
    print("Radio Spotting API - Neural Network Feature Extractor")
    print("=" * 60)
    
    # Initialize extractor
    extractor = RadioSpottingFeatureExtractor()
    
    # Fetch data from API
    print("\n[1] Fetching data from API...")
    spots = extractor.fetch_data(limit=100)  # Limit to 100 for demo
    
    if not spots:
        print("✗ Failed to fetch data")
        return
    
    # Extract features
    print("\n[2] Extracting features...")
    raw_features = extractor.extract_features(spots)
    
    # Normalize features
    print("\n[3] Normalizing features...")
    normalized_features = extractor.normalize_features()
    
    # Display statistics
    print("\n[4] Feature Statistics:")
    print("-" * 60)
    stats = extractor.get_statistics(normalized=True)
    
    feature_names = extractor.get_feature_names()
    print(f"{'Feature':<20} {'Mean':<12} {'Std':<12} {'Min':<12} {'Max':<12}")
    print("-" * 60)
    
    for i, name in enumerate(feature_names):
        print(
            f"{name:<20} "
            f"{stats['mean'][i]:<12.4f} "
            f"{stats['std'][i]:<12.4f} "
            f"{stats['min'][i]:<12.4f} "
            f"{stats['max'][i]:<12.4f}"
        )
    
    # Display sample feature vectors
    print("\n[5] Sample Normalized Feature Vectors (first 5):")
    print("-" * 60)
    df = extractor.to_dataframe(normalized=True)
    print(df.head(5).to_string(index=False))
    
    # Save to CSV
    output_file = "radio_spotting_features.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ Features saved to {output_file}")
    
    print("\n" + "=" * 60)
    print("✓ Pipeline complete! Ready for neural network input.")
    print("=" * 60)


if __name__ == "__main__":
    main()

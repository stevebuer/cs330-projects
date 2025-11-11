"""
Feature extraction and normalization from radio spotting API.
Prepares data for neural network input.
"""

import requests
import numpy as np
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import sys


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
    
    def fetch_data(self, target_date: str = None, limit: int = None) -> List[Dict]:
        """
        Fetch radio spotting data from API for a specific completed day.
        
        Args:
            target_date: Date string in format YYYY-MM-DD. Defaults to yesterday.
            limit: Maximum number of spots to fetch. None for all.
            
        Returns:
            List of spot dictionaries from API response for the specified date.
        """
        if target_date is None:
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            # Parse target date
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            
            # Create ISO format timestamps for full day
            start_dt = target_dt.replace(tzinfo=timezone.utc)
            end_dt = (target_dt + timedelta(days=1)).replace(tzinfo=timezone.utc)
            
            since_param = start_dt.isoformat().replace('+00:00', 'Z')
            until_param = end_dt.isoformat().replace('+00:00', 'Z')
            
            url = self.API_URL
            page_size = 500
            offset = 0
            all_spots = []
            
            while True:
                params = {
                    'since': since_param,
                    'until': until_param,
                    'limit': page_size,
                    'offset': offset
                }
                
                query_string = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
                full_url = f"{url}?{query_string}"
                
                with urllib.request.urlopen(full_url, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    spots = data.get("spots", [])
                    pagination = data.get("pagination", {})
                    
                    if not spots:
                        break
                    
                    all_spots.extend(spots)
                    
                    has_more = pagination.get("has_more", False)
                    if not has_more:
                        break
                    
                    offset += len(spots)
            
            if limit:
                all_spots = all_spots[:limit]
            
            print(f"✓ Fetched {len(all_spots)} spots from API for {target_date}")
            return all_spots
            
        except urllib.error.HTTPError as e:
            print(f"✗ API Error: {e.code} - {e.reason}")
            return []
        except ValueError as e:
            print(f"✗ Invalid date format: {e}. Use YYYY-MM-DD")
            return []
        except Exception as e:
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
    # Parse command-line arguments
    target_date = None
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        # Validate date format
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            print(f"✗ Invalid date format: {target_date}. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"ℹ No date specified. Using yesterday's date: {target_date}")
    
    print("=" * 60)
    print("Radio Spotting API - Neural Network Feature Extractor")
    print(f"Target Date: {target_date}")
    print("=" * 60)
    
    # Initialize extractor
    extractor = RadioSpottingFeatureExtractor()
    
    # Fetch data from API for specified date
    print("\n[1] Fetching data from API...")
    spots = extractor.fetch_data(target_date=target_date)
    
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
    
    # Save to CSV with date in filename
    output_file = f"radio_spotting_features_{target_date}.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ Features saved to {output_file}")
    
    print("\n" + "=" * 60)
    print("✓ Pipeline complete! Ready for neural network input.")
    print("=" * 60)


if __name__ == "__main__":
    main()

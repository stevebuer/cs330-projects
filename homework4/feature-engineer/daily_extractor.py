"""
Daily Radio Wave Propagation Feature Extractor
Extracts daily aggregated features suitable for propagation analysis models.
Groups all radio spots by date and creates statistical features for each day.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict


class DailyFeatureExtractor:
    """Extract daily aggregated features from radio spotting data."""
    
    API_URL = "http://api.jxqz.org:8080/api/spots"
    
    BANDS_LIST = ["6m", "10m", "12m", "15m", "17m", "20m", "40m"]  # Excluding 80m and 160m
    
    def __init__(self):
        self.raw_spots = None
        self.daily_data = None
        self.daily_features = None
        self.normalized_features = None
    
    def fetch_data(self, limit: int = None, exclude_today: bool = True, days_back: int = None) -> List[Dict]:
        """
        Fetch data from API.
        
        Args:
            limit: Maximum number of spots to fetch (None for all)
            exclude_today: If True, exclude today's data (keep only historical data for training)
            days_back: If set, only include data from N days ago or earlier (relative to today)
        
        Returns:
            List of spot dictionaries
        """
        try:
            with urllib.request.urlopen(self.API_URL, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                spots = data.get("spots", [])
                
                if limit:
                    spots = spots[:limit]
                
                # Filter by date constraints
                filtered_spots = []
                today = datetime.now().date()
                cutoff_date = None
                
                if days_back is not None:
                    cutoff_date = today - timedelta(days=days_back)
                
                for spot in spots:
                    timestamp_str = spot.get("timestamp", "")
                    try:
                        dt = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
                        spot_date = dt.date()
                        
                        # Skip today if exclude_today is True
                        if exclude_today and spot_date >= today:
                            continue
                        
                        # Skip if before cutoff date
                        if cutoff_date and spot_date < cutoff_date:
                            continue
                        
                        filtered_spots.append(spot)
                    except:
                        continue
                
                print(f"✓ Fetched {len(filtered_spots)} spots from API (historical data)")
                if exclude_today:
                    print(f"  Note: Excluded today ({today}) - using only previous days")
                if days_back:
                    print(f"  Note: Limited to {days_back} days back (since {cutoff_date})")
                
                self.raw_spots = filtered_spots
                return filtered_spots
                
        except Exception as e:
            print(f"✗ Error fetching API data: {e}")
            return []
    
    def group_by_date(self, spots: List[Dict]) -> Dict[str, List[Dict]]:
        """Group spots by date (YYYY-MM-DD)."""
        grouped = defaultdict(list)
        
        for spot in spots:
            timestamp_str = spot.get("timestamp", "")
            try:
                dt = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
                date_key = dt.strftime("%Y-%m-%d")
                grouped[date_key].append(spot)
            except:
                continue
        
        # Sort by date
        self.daily_data = dict(sorted(grouped.items()))
        print(f"✓ Grouped {len(spots)} spots into {len(self.daily_data)} days")
        
        return self.daily_data
    
    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict:
        """Calculate basic statistics for a list of values."""
        if not values:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "count": 0}
        
        values = [v for v in values if v is not None]
        if not values:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "count": 0}
        
        count = len(values)
        mean = sum(values) / count
        variance = sum((v - mean) ** 2 for v in values) / count if count > 1 else 0
        std = variance ** 0.5
        
        return {
            "mean": mean,
            "std": std,
            "min": min(values),
            "max": max(values),
            "count": count
        }
    
    def extract_daily_features(self, daily_data: Dict[str, List[Dict]] = None) -> List[List[float]]:
        """
        Extract daily aggregated features for radio wave propagation analysis.
        
        Features per day:
        1. avg_frequency - Average frequency of all spots
        2. num_bands_active - Number of different bands with activity
        3. num_spots - Total number of spots for the day
        4. avg_signal_quality - Average signal report quality
        5. signal_quality_std - Standard deviation of signal quality
        6. cw_percentage - Percentage of spots in CW mode
        7. ssb_percentage - Percentage of spots in SSB mode
        8. activity_spread - Hours with activity (0-24)
        9. peak_hour - Hour with most activity
        10. long_wave_activity - Percentage of 40m band activity (lowest frequency in use)
        
        Note: Equipment operates on 6m-40m bands only (80m and 160m excluded)
        
        Returns:
            List of daily feature vectors: [date, feature1, feature2, ...]
        """
        if daily_data is None:
            daily_data = self.daily_data
        
        if not daily_data:
            print("✗ No daily data to extract features from")
            return []
        
        daily_features = []
        
        for date_str in sorted(daily_data.keys()):
            spots = daily_data[date_str]
            
            # Extract raw values
            frequencies = []
            signal_qualities = []
            modes = []
            bands = []
            hours = []
            
            for spot in spots:
                try:
                    # Frequency
                    freq = float(spot.get("frequency", 0))
                    if freq > 0:
                        frequencies.append(freq)
                    
                    # Signal quality
                    signal_report = spot.get("signal_report", None)
                    if signal_report:
                        try:
                            sq = float(str(signal_report)[:2])
                            signal_qualities.append(sq)
                        except:
                            pass
                    
                    # Mode
                    mode = spot.get("mode", "")
                    if mode:
                        modes.append(mode)
                    
                    # Band
                    band = spot.get("band", "")
                    if band:
                        bands.append(band)
                    
                    # Hour
                    timestamp_str = spot.get("timestamp", "")
                    try:
                        dt = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
                        hours.append(dt.hour)
                    except:
                        pass
                
                except Exception as e:
                    continue
            
            # Calculate features
            features = [date_str]  # First element is the date
            
            # 1. Average frequency
            freq_stats = self.calculate_statistics(frequencies)
            features.append(freq_stats["mean"])
            
            # 2. Number of bands active
            unique_bands = len(set(bands))
            features.append(float(unique_bands))
            
            # 3. Total number of spots
            features.append(float(len(spots)))
            
            # 4. Average signal quality
            sig_stats = self.calculate_statistics(signal_qualities)
            features.append(sig_stats["mean"])
            
            # 5. Signal quality std deviation
            features.append(sig_stats["std"])
            
            # 6. CW percentage
            cw_count = sum(1 for m in modes if m == "CW")
            cw_pct = (cw_count / len(modes) * 100) if modes else 0
            features.append(float(cw_pct))
            
            # 7. SSB percentage
            ssb_count = sum(1 for m in modes if m == "SSB")
            ssb_pct = (ssb_count / len(modes) * 100) if modes else 0
            features.append(float(ssb_pct))
            
            # 8. Activity spread (hours with at least one spot)
            unique_hours = len(set(hours))
            features.append(float(unique_hours))
            
            # 9. Peak hour
            if hours:
                hour_counts = defaultdict(int)
                for h in hours:
                    hour_counts[h] += 1
                peak_hour = max(hour_counts, key=hour_counts.get)
                features.append(float(peak_hour))
            else:
                features.append(0.0)
            
            # 10. Long-wave activity percentage (40m band - lowest frequency in use)
            long_wave_bands = {"40m"}
            long_wave_count = sum(1 for b in bands if b in long_wave_bands)
            long_wave_pct = (long_wave_count / len(bands) * 100) if bands else 0
            features.append(float(long_wave_pct))
            
            daily_features.append(features)
        
        self.daily_features = daily_features
        print(f"✓ Extracted features for {len(daily_features)} days")
        return daily_features
    
    @staticmethod
    def min_max_normalize(features: List[List[float]], exclude_columns: set = None) -> List[List[float]]:
        """
        Min-Max normalization to [0, 1] range, excluding date column and others if specified.
        
        Args:
            features: List of daily feature vectors (first element is date string)
            exclude_columns: Set of column indices to exclude from normalization
        
        Returns:
            Normalized features with dates preserved
        """
        if not features or not features[0]:
            return features
        
        if exclude_columns is None:
            exclude_columns = {0}  # Exclude date column by default
        
        # First element is date, so start from index 1
        n_features = len(features[0])
        normalized = []
        
        # Calculate min and max for each numeric feature
        mins = [float('inf')] * n_features
        maxs = [float('-inf')] * n_features
        
        for feature_vec in features:
            for i, val in enumerate(feature_vec):
                if i not in exclude_columns and isinstance(val, (int, float)):
                    mins[i] = min(mins[i], val)
                    maxs[i] = max(maxs[i], val)
        
        # Normalize each feature
        for feature_vec in features:
            normalized_vec = []
            for i, val in enumerate(feature_vec):
                if i in exclude_columns:
                    # Keep date and other excluded columns as-is
                    normalized_vec.append(val)
                else:
                    # Normalize numeric values
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
        if not self.daily_features:
            print("✗ No features to normalize")
            return None
        
        self.normalized_features = self.min_max_normalize(self.daily_features)
        print(f"✓ Normalized {len(self.normalized_features)} daily feature vectors")
        return self.normalized_features
    
    def get_feature_names(self) -> List[str]:
        """Get names of features (excluding date). Covers 6m-40m bands only."""
        return [
            "date",
            "avg_frequency_mhz",
            "num_bands_active",
            "total_spots",
            "avg_signal_quality",
            "signal_quality_std",
            "cw_percentage",
            "ssb_percentage",
            "activity_hours_count",
            "peak_hour",
            "40m_band_percentage"  # Lowest frequency band in use
        ]


def main():
    """Demo script for daily feature extraction."""
    print("=" * 70)
    print("Daily Radio Wave Propagation Feature Extractor")
    print("=" * 70)
    
    extractor = DailyFeatureExtractor()
    
    # Fetch data
    print("\n[1] Fetching data from API...")
    spots = extractor.fetch_data(limit=500)  # Fetch more to get multiple days
    
    if not spots:
        print("✗ Failed to fetch data")
        return
    
    # Group by date
    print("\n[2] Grouping spots by date...")
    daily_data = extractor.group_by_date(spots)
    
    # Extract daily features
    print("\n[3] Extracting daily features...")
    daily_features = extractor.extract_daily_features()
    
    # Normalize
    print("\n[4] Normalizing features...")
    normalized = extractor.normalize_features()
    
    # Display results
    print("\n[5] Daily Feature Vectors (normalized):")
    print("-" * 90)
    
    feature_names = extractor.get_feature_names()
    header = f"{'Date':<12} " + " ".join(f"{name[:10]:>10}" for name in feature_names[1:])
    print(header)
    print("-" * 90)
    
    for i, vec in enumerate(normalized[:10]):  # Show first 10 days
        date_str = vec[0]
        numeric_vals = " ".join(f"{v:>10.4f}" for v in vec[1:])
        print(f"{date_str:<12} {numeric_vals}")
    
    if len(normalized) > 10:
        print(f"... and {len(normalized) - 10} more days")
    
    # Save to CSV
    print("\n[6] Saving to CSV...")
    csv_file = "daily_radio_features.csv"
    with open(csv_file, 'w') as f:
        f.write(",".join(feature_names) + "\n")
        for vec in normalized:
            # Date stays as string, numbers get formatted
            line = f"{vec[0]}," + ",".join(f"{v:.6f}" for v in vec[1:])
            f.write(line + "\n")
    
    print(f"✓ Saved {len(normalized)} daily feature vectors to {csv_file}")
    
    # Statistics
    print("\n[7] Summary Statistics:")
    print("-" * 70)
    print(f"Total days with data: {len(normalized)}")
    print(f"Total spots analyzed: {sum(int(float(v[3])) for v in daily_features)}")
    print(f"Date range: {normalized[0][0]} to {normalized[-1][0]}")
    
    print("\n[8] Feature Ranges (after normalization):")
    print("-" * 70)
    feature_names_numeric = feature_names[1:]
    for feat_idx, name in enumerate(feature_names_numeric, start=1):
        values = [v[feat_idx] for v in normalized]
        min_val = min(values)
        max_val = max(values)
        mean_val = sum(values) / len(values)
        print(f"{name:<25} Min: {min_val:>7.4f}  Max: {max_val:>7.4f}  Mean: {mean_val:>7.4f}")
    
    print("\n" + "=" * 70)
    print("✓ Daily feature extraction complete!")
    print("Each row represents one day of radio wave propagation data.")
    print("=" * 70)


if __name__ == "__main__":
    main()

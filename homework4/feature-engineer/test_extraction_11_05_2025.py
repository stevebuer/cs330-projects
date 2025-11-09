from daily_extractor import DailyFeatureExtractor
from datetime import datetime
import numpy as np

extractor = DailyFeatureExtractor()

# Fetch all available data (no date restrictions)
print("=" * 70)
print("Testing extraction for 11/5/2025")
print("=" * 70)

print("\n[1] Fetching all available data...")
spots_all = extractor.fetch_data(limit=1000, exclude_today=False)

# Look for spots from 11/5/2025
target_date = '2025-11-05'
target_spots = [s for s in spots_all if target_date in s.get('timestamp', '')]

print(f"\nTotal spots in API: {len(spots_all)}")
print(f"Spots from 2025-11-05: {len(target_spots)}")

# Show available dates
if target_spots:
    print(f"\n[2] Found {len(target_spots)} spots from 11/5/2025!")
    print("\nSample spots from that date:")
    for i, spot in enumerate(target_spots[:3]):
        print(f"\n  Spot {i+1}:")
        print(f"    Band: {spot.get('band')}")
        print(f"    Frequency: {spot.get('frequency')} MHz")
        print(f"    Mode: {spot.get('mode')}")
        print(f"    Signal: {spot.get('signal_report')}")
        print(f"    Time: {spot.get('timestamp')}")
    
    # Now extract features for that day
    print("\n[3] Extracting daily features for 11/5/2025...")
    extractor.raw_spots = target_spots
    extractor.group_by_date(target_spots)
    daily_features = extractor.extract_daily_features()
    normalized = extractor.normalize_features()
    
    print(f"\n[4] Extracted Features for 2025-11-05:")
    print("-" * 70)
    feature_names = extractor.get_feature_names()
    
    for vec in normalized:
        date = vec[0]
        features = vec[1:]
        print(f"\nDate: {date}")
        print(f"{'Feature':<30} {'Raw Value':<15} {'Normalized':<15}")
        print("-" * 60)
        for name, val in zip(feature_names, features):
            print(f"{name:<30} {val:<15.4f} {val:<15.4f}")
    
    # Save to CSV
    print(f"\n[5] Saving to CSV...")
    with open('daily_radio_features_11_05_2025.csv', 'w') as f:
        f.write(','.join(feature_names) + '\n')
        for vec in normalized:
            f.write(','.join(str(v) for v in vec) + '\n')
    print("✓ Saved to daily_radio_features_11_05_2025.csv")
    
else:
    print("\n✗ No spots found for 2025-11-05")
    print("\nAvailable dates in API response:")
    dates = {}
    for spot in spots_all:
        ts = spot.get('timestamp', '')
        if ts:
            # Extract date
            parts = ts.split()
            date = f"{parts[2]} {parts[1]} {parts[3]}"
            dates[date] = dates.get(date, 0) + 1
    
    for date in sorted(dates.keys())[:15]:
        print(f"  {date}: {dates[date]} spots")

print("\n" + "=" * 70)

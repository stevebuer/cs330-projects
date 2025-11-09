from daily_extractor import DailyFeatureExtractor
import numpy as np

print("=" * 70)
print("Testing Daily Extraction with Available Data")
print("=" * 70)

extractor = DailyFeatureExtractor()

# Fetch today's data (it's the only data available in real-time API)
print("\n[1] Fetching real-time data from API...")
spots = extractor.fetch_data(limit=200, exclude_today=False)

print(f"\nTotal spots fetched: {len(spots)}")

if len(spots) > 0:
    # Show sample data
    print("\n[2] Sample spots from API:")
    print("-" * 70)
    for i, spot in enumerate(spots[:3]):
        print(f"\nSpot {i+1}:")
        print(f"  Band: {spot.get('band')}")
        print(f"  Frequency: {spot.get('frequency')} MHz")
        print(f"  Mode: {spot.get('mode')}")
        print(f"  Signal: {spot.get('signal_report')}")
        print(f"  Callsign: {spot.get('dx_call')}")
        print(f"  Spotter: {spot.get('spotter_call')}")
        print(f"  Time: {spot.get('timestamp')}")
    
    # Extract daily features
    print("\n[3] Grouping by date...")
    extractor.group_by_date(spots)
    
    print("\n[4] Extracting daily features...")
    daily_features = extractor.extract_daily_features()
    
    print("\n[5] Normalizing features to [0,1]...")
    normalized = extractor.normalize_features()
    
    # Display results
    print("\n" + "=" * 70)
    print("EXTRACTED DAILY FEATURES")
    print("=" * 70)
    
    feature_names = extractor.get_feature_names()
    
    for vec in normalized:
        date = vec[0]
        features = [float(v) for v in vec[1:]]
        
        print(f"\nDate: {date}")
        print("-" * 70)
        print(f"{'Feature Name':<35} {'Normalized [0,1]':<20} {'Description':<15}")
        print("-" * 70)
        
        descriptions = [
            "Avg freq (MHz)",
            "Active bands",
            "Total spots",
            "Avg signal",
            "Signal std",
            "CW %",
            "SSB %",
            "Active hours",
            "Peak hour",
            "40m %"
        ]
        
        for name, val, desc in zip(feature_names, features, descriptions):
            print(f"{name:<35} {val:<20.6f} {desc:<15}")
    
    # Save to CSV
    print("\n" + "=" * 70)
    print("SAVING TO CSV")
    print("=" * 70)
    
    csv_file = 'daily_radio_features_test.csv'
    with open(csv_file, 'w') as f:
        # Write header
        f.write(','.join(feature_names) + '\n')
        # Write data rows
        for vec in normalized:
            row = ','.join(str(v) for v in vec)
            f.write(row + '\n')
    
    print(f"\n✓ Saved {len(normalized)} daily feature vector(s) to {csv_file}")
    
    # Display CSV content
    print("\nCSV Content:")
    print("-" * 70)
    with open(csv_file, 'r') as f:
        for line in f:
            print(line.rstrip())
    
    # Statistics
    print("\n" + "=" * 70)
    print("FEATURE STATISTICS")
    print("=" * 70)
    
    feature_array = np.array(features).reshape(1, -1)
    print(f"\nStatistics (all normalized to [0,1]):")
    print(f"  Mean:   {feature_array.mean():.4f}")
    print(f"  Std:    {feature_array.std():.4f}")
    print(f"  Min:    {feature_array.min():.4f}")
    print(f"  Max:    {feature_array.max():.4f}")
    
    print("\n" + "=" * 70)
    print("✓ Extraction test complete!")
    print("=" * 70)

else:
    print("\n✗ No data available from API")

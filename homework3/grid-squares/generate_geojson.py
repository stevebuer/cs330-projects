#!/usr/bin/env python3
"""
Generate GeoJSON data for DX propagation paths using grid squares
Can be imported into mapping libraries like Leaflet, Mapbox, or GIS software
"""

import json
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (km)"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return c * 6371  # Earth radius in km

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2 (degrees)"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    return (bearing + 360) % 360

def create_geojson_features(grid_pairs, grid_data):
    """
    Create GeoJSON features for grid squares and propagation paths

    Args:
        grid_pairs: List of (source_grid, dest_grid) tuples
        grid_data: Dictionary of grid -> (lat, lon) coordinates

    Returns:
        dict: GeoJSON FeatureCollection
    """
    features = []

    # Track added grid squares to avoid duplicates
    added_grids = {}

    # Colors for different paths
    colors = ['#FF0000', '#0000FF', '#00FF00', '#800080', '#FFA500',
              '#8B0000', '#FF6347', '#F5F5DC', '#00008B', '#006400']

    for i, (source_grid, dest_grid) in enumerate(grid_pairs):
        source_coords = grid_data.get(source_grid.upper())
        dest_coords = grid_data.get(dest_grid.upper())

        if not source_coords or not dest_coords:
            continue

        # Add source grid square marker
        if source_grid not in added_grids:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [source_coords[1], source_coords[0]]  # GeoJSON: [lon, lat]
                },
                "properties": {
                    "grid": source_grid,
                    "type": "source",
                    "latitude": source_coords[0],
                    "longitude": source_coords[1]
                }
            })
            added_grids[source_grid] = True

        # Add destination grid square marker
        if dest_grid not in added_grids:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [dest_coords[1], dest_coords[0]]
                },
                "properties": {
                    "grid": dest_grid,
                    "type": "destination",
                    "latitude": dest_coords[0],
                    "longitude": dest_coords[1]
                }
            })
            added_grids[dest_grid] = True

        # Calculate path properties
        distance = calculate_distance(source_coords[0], source_coords[1],
                                    dest_coords[0], dest_coords[1])
        bearing = calculate_bearing(source_coords[0], source_coords[1],
                                  dest_coords[0], dest_coords[1])

        # Add propagation path
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [source_coords[1], source_coords[0]],
                    [dest_coords[1], dest_coords[0]]
                ]
            },
            "properties": {
                "source_grid": source_grid,
                "dest_grid": dest_grid,
                "distance_km": round(distance, 1),
                "bearing_deg": round(bearing, 1),
                "type": "propagation_path",
                "color": colors[i % len(colors)]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

def generate_propagation_geojson(grid_pairs, output_file='dx_propagation_paths.geojson'):
    """
    Generate GeoJSON file with DX propagation paths

    Args:
        grid_pairs: List of (source_grid, dest_grid) tuples
        output_file: Output filename
    """
    # Load grid square data
    try:
        with open('grid_squares.json', 'r') as f:
            grid_data = json.load(f)
    except FileNotFoundError:
        print("Error: grid_squares.json not found. Run grid_utils.py first.")
        return

    print(f"Generating GeoJSON for {len(grid_pairs)} propagation paths...")

    # Create GeoJSON features
    geojson_data = create_geojson_features(grid_pairs, grid_data)

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(geojson_data, f, indent=2)

    print(f"GeoJSON saved to {output_file}")
    print(f"Contains {len(geojson_data['features'])} features")

    return geojson_data

def demo_geojson():
    """Create demo GeoJSON with sample propagation paths"""
    # Sample grid square pairs
    sample_pairs = [
        ('FN42', 'EM12'),  # Boston -> Dallas
        ('CN87', 'DM04'),  # Seattle -> San Diego
        ('FN42', 'CN87'),  # Boston -> Seattle
        ('EM12', 'DM04'),  # Dallas -> San Diego
        ('FN42', 'DM04'),  # Boston -> San Diego
    ]

    print("Creating demo propagation GeoJSON...")
    geojson = generate_propagation_geojson(sample_pairs, 'demo_propagation_paths.geojson')

    # Print summary
    points = [f for f in geojson['features'] if f['geometry']['type'] == 'Point']
    lines = [f for f in geojson['features'] if f['geometry']['type'] == 'LineString']

    print(f"Generated {len(points)} grid square markers")
    print(f"Generated {len(lines)} propagation paths")

    print("\nSample path data:")
    for line in lines[:3]:  # Show first 3 paths
        props = line['properties']
        print(f"  {props['source_grid']} → {props['dest_grid']}: "
              f"{props['distance_km']} km, {props['bearing_deg']}° bearing")

if __name__ == '__main__':
    demo_geojson()
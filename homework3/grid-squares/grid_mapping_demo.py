#!/usr/bin/env python3
"""
Example: Load grid square data and demonstrate usage for mapping
"""

import json
import sys
import os

def load_grid_data(filename='grid_squares.json'):
    """Load grid square coordinate data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Run grid_utils.py first to generate it.")
        return None

def get_grid_coords(grid_square, grid_data=None):
    """Get latitude/longitude for a grid square"""
    if grid_data is None:
        grid_data = load_grid_data()
        if grid_data is None:
            return None

    grid_square = grid_square.upper()
    return grid_data.get(grid_square)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance between two points using Haversine formula"""
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers
    r = 6371
    return c * r

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    return bearing

def demo_grid_mapping():
    """Demonstrate grid square mapping functionality"""
    print("Grid Square Mapping Demo")
    print("=" * 40)

    # Load grid data
    grid_data = load_grid_data()
    if not grid_data:
        return

    # Example grid squares
    examples = [
        ('FN42', 'Boston, MA area'),
        ('EM12', 'Dallas, TX area'),
        ('DM04', 'San Diego, CA area'),
        ('CN87', 'Seattle, WA area')
    ]

    print("Grid Square Coordinates:")
    for grid, location in examples:
        coords = get_grid_coords(grid, grid_data)
        if coords:
            print(f"{grid} ({location}): {coords[0]:.1f}°N, {coords[1]:.1f}°E" if coords[1] >= 0 else f"{grid} ({location}): {coords[0]:.1f}°N, {coords[1]:.1f}°W")
        else:
            print(f"{grid}: Not found")

    print("\nDistance and Bearing Examples:")
    # Calculate distance between two grids
    grid1, grid2 = 'FN42', 'EM12'
    coords1 = get_grid_coords(grid1, grid_data)
    coords2 = get_grid_coords(grid2, grid_data)

    if coords1 and coords2:
        distance = calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
        bearing = calculate_bearing(coords1[0], coords1[1], coords2[0], coords2[1])
        print(f"Distance from {grid1} to {grid2}: {distance:.0f} km")
        print(f"Bearing from {grid1} to {grid2}: {bearing:.0f}°")

    print("\nJSON Structure for Mapping:")
    print("Each grid square maps to [latitude, longitude] coordinates")
    print("Perfect for plotting on maps like Folium, Plotly, or Matplotlib")

if __name__ == '__main__':
    import math  # Import here to avoid circular import issues
    demo_grid_mapping()
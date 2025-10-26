#!/usr/bin/env python3
"""
Create an interactive map showing DX propagation paths using grid squares
"""

import json
import folium
from folium import plugins
import sys

def create_dx_map(grid_pairs, output_file='dx_propagation_map.html'):
    """
    Create an interactive map showing DX propagation paths

    Args:
        grid_pairs: List of (source_grid, dest_grid) tuples
        output_file: Output HTML filename
    """
    # Load grid square data
    try:
        with open('grid_squares.json', 'r') as f:
            grid_data = json.load(f)
    except FileNotFoundError:
        print("Error: grid_squares.json not found. Run grid_utils.py first.")
        return

    # Create base map centered on North America
    m = folium.Map(location=[40, -95], zoom_start=4,
                   tiles='OpenStreetMap')

    # Add grid squares layer
    grid_layer = folium.FeatureGroup(name='Grid Squares', show=False)

    # Keep track of added grids to avoid duplicates
    added_grids = set()

    # Add propagation paths
    path_layer = folium.FeatureGroup(name='Propagation Paths')

    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
              'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
              'gray', 'black', 'lightgray']

    for i, (source_grid, dest_grid) in enumerate(grid_pairs):
        source_coords = grid_data.get(source_grid.upper())
        dest_coords = grid_data.get(dest_grid.upper())

        if source_coords and dest_coords:
            # Add markers for grid squares
            if source_grid not in added_grids:
                folium.CircleMarker(
                    location=source_coords,
                    radius=8,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.7,
                    popup=f'Source: {source_grid}'
                ).add_to(grid_layer)
                added_grids.add(source_grid)

            if dest_grid not in added_grids:
                folium.CircleMarker(
                    location=dest_coords,
                    radius=8,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.7,
                    popup=f'Dest: {dest_grid}'
                ).add_to(grid_layer)
                added_grids.add(dest_grid)

            # Add propagation path
            color = colors[i % len(colors)]
            folium.PolyLine(
                locations=[source_coords, dest_coords],
                color=color,
                weight=3,
                opacity=0.8,
                popup=f'{source_grid} → {dest_grid}'
            ).add_to(path_layer)

    # Add layers to map
    grid_layer.add_to(m)
    path_layer.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Save map
    m.save(output_file)
    print(f"Map saved to {output_file}")

    return m

def demo_map():
    """Create a demo map with sample propagation paths"""
    # Sample grid square pairs (source -> destination)
    sample_pairs = [
        ('FN42', 'EM12'),  # Boston -> Dallas
        ('CN87', 'DM04'),  # Seattle -> San Diego
        ('FN42', 'CN87'),  # Boston -> Seattle
        ('EM12', 'DM04'),  # Dallas -> San Diego
    ]

    print("Creating demo propagation map...")
    create_dx_map(sample_pairs, 'demo_propagation_map.html')
    print("Demo map created! Open demo_propagation_map.html in your browser.")

if __name__ == '__main__':
    # Check if folium is available
    try:
        import folium
    except ImportError:
        print("Folium not installed. Install with: pip install folium")
        sys.exit(1)

    demo_map()
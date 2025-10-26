#!/usr/bin/env python3
"""
Maidenhead Grid Square Utilities
Convert Maidenhead locator codes to latitude/longitude coordinates
"""

import json
import math

def grid_to_latlon(grid_square):
    """
    Convert a Maidenhead grid square to center latitude and longitude

    Args:
        grid_square (str): Maidenhead locator (4 or 6 characters)

    Returns:
        tuple: (latitude, longitude) in decimal degrees, or None if invalid
    """
    if not grid_square or len(grid_square) not in [4, 6]:
        return None

    grid_square = grid_square.upper()

    try:
        # Field (2 letters): 20° x 10°
        field_lon = ord(grid_square[0]) - ord('A')
        field_lat = ord(grid_square[1]) - ord('A')

        if not (0 <= field_lon <= 17 and 0 <= field_lat <= 17):
            return None

        # Square (2 digits): 1° x 1°
        square_lon = int(grid_square[2])
        square_lat = int(grid_square[3])

        if not (0 <= square_lon <= 9 and 0 <= square_lat <= 9):
            return None

        # Calculate base coordinates
        lon = field_lon * 20 - 180
        lat = field_lat * 10 - 90

        lon += square_lon * 2
        lat += square_lat * 1

        # Subsquare (2 letters, optional): 2.5' x 2.5' (0.04167° x 0.04167°)
        if len(grid_square) == 6:
            subsquare_lon = ord(grid_square[4].lower()) - ord('a')
            subsquare_lat = ord(grid_square[5].lower()) - ord('a')

            if not (0 <= subsquare_lon <= 23 and 0 <= subsquare_lat <= 23):
                return None

            lon += subsquare_lon * (2 / 24)  # 2° / 24 = 0.08333°
            lat += subsquare_lat * (1 / 24)  # 1° / 24 = 0.04167°

        # Add 0.5 to get center of the grid square
        lon += 1 if len(grid_square) == 4 else (2 / 24) / 2
        lat += 0.5 if len(grid_square) == 4 else (1 / 24) / 2

        return (lat, lon)

    except (ValueError, IndexError):
        return None

def generate_grid_data(max_precision=4):
    """
    Generate a dictionary of all valid grid squares with their coordinates

    Args:
        max_precision (int): Maximum grid precision (4 or 6)

    Returns:
        dict: Grid square -> (lat, lon) mapping
    """
    grid_data = {}

    if max_precision >= 4:
        # Generate 4-character grids
        for field1 in range(18):  # A-R
            for field2 in range(18):  # A-R
                for square1 in range(10):  # 0-9
                    for square2 in range(10):  # 0-9
                        grid = f"{chr(ord('A')+field1)}{chr(ord('A')+field2)}{square1}{square2}"
                        coords = grid_to_latlon(grid)
                        if coords:
                            grid_data[grid] = coords

    if max_precision >= 6:
        # Generate 6-character grids (warning: 32,400 * 24 * 24 = ~18.8 million entries!)
        for field1 in range(18):
            for field2 in range(18):
                for square1 in range(10):
                    for square2 in range(10):
                        for sub1 in range(24):  # a-x
                            for sub2 in range(24):  # a-x
                                grid = f"{chr(ord('A')+field1)}{chr(ord('A')+field2)}{square1}{square2}{chr(ord('a')+sub1)}{chr(ord('b')+sub2)}"
                                coords = grid_to_latlon(grid)
                                if coords:
                                    grid_data[grid] = coords

    return grid_data

def save_grid_data(filename, max_precision=4):
    """
    Generate and save grid square data to a JSON file

    Args:
        filename (str): Output filename
        max_precision (int): Maximum grid precision (4 or 6)
    """
    print(f"Generating grid square data (precision: {max_precision})...")
    grid_data = generate_grid_data(max_precision)

    print(f"Saving {len(grid_data)} grid squares to {filename}...")
    with open(filename, 'w') as f:
        json.dump(grid_data, f, indent=2)

    print("Done!")

if __name__ == '__main__':
    # Example usage
    test_grids = ['FN42', 'EM12', 'AA00', 'RR99', 'FN42aa', 'FN42xx']

    print("Testing grid square conversions:")
    for grid in test_grids:
        coords = grid_to_latlon(grid)
        if coords:
            print(f"{grid}: {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print(f"{grid}: Invalid")

    # Generate data file
    save_grid_data('grid_squares.json', max_precision=4)
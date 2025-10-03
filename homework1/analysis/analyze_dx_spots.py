#!/usr/bin/env python3
"""
Analyze DX cluster spots stored in the SQLite database and print/save insights.

Usage:
  python analyze_dx_spots.py [--db DB_PATH] [--top N] [--plots] [--outdir DIR]

The script prints summary statistics and top-N lists. If pandas/matplotlib
are installed it will also generate and save a few plots to the output
directory (default: ./analysis_outputs).
"""
import sqlite3
import argparse
from datetime import datetime
import os
import sys

try:
    import pandas as pd
except Exception:
    pd = None

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    try:
        import geopandas as gpd
    except Exception:
        gpd = None
except Exception:
    plt = None
    sns = None
    gpd = None

DB_DEFAULT = 'dxcluster.db'


def load_tables(db_path):
    """Load dx_spots and callsigns tables into pandas DataFrames if pandas
    is available, otherwise return lists of dicts via sqlite3 cursor."""
    conn = sqlite3.connect(db_path)
    if pd is not None:
        df_spots = pd.read_sql_query('SELECT * FROM dx_spots', conn, parse_dates=['timestamp'])
        df_calls = pd.read_sql_query('SELECT * FROM callsigns', conn, parse_dates=['first_seen','last_seen'])
        conn.close()
        return df_spots, df_calls

    cur = conn.cursor()
    cur.execute('SELECT * FROM dx_spots')
    cols = [d[0] for d in cur.description]
    spots = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.execute('SELECT * FROM callsigns')
    cols = [d[0] for d in cur.description]
    calls = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()
    return spots, calls


def print_basic_stats(df_spots, df_calls):
    print('\n=== Basic dataset summary ===')
    if pd is not None and isinstance(df_spots, pd.DataFrame):
        total_spots = len(df_spots)
        unique_dx = df_spots['dx_call'].nunique()
        unique_spotters = df_spots['spotter_call'].nunique()
        times = pd.to_datetime(df_spots['timestamp'])
        first = times.min()
        last = times.max()
        days = (last - first).days or 1
        spots_per_day = total_spots / (days if days else 1)

        print(f'Total spots: {total_spots}')
        print(f'Unique DX calls seen: {unique_dx}')
        print(f'Unique spotter calls: {unique_spotters}')
        print(f'Time range: {first} -> {last} ({days} days)')
        print(f'Average spots per day: {spots_per_day:.2f}')
    else:
        print('Pandas not available. Basic statistics not computed.')


def top_n_by_count(df_spots, column, n=10):
    if pd is None:
        return []
    s = df_spots[column].value_counts().head(n)
    return list(s.items())


def band_distribution(df_spots):
    if pd is None:
        return {}
    return df_spots['band'].value_counts(dropna=True)


def mode_distribution(df_spots):
    if pd is None:
        return {}
    return df_spots['mode'].value_counts(dropna=True)


def busiest_hour(df_spots):
    if pd is None:
        return None
    hours = pd.to_datetime(df_spots['timestamp']).dt.hour
    return hours.value_counts().idxmax(), hours.value_counts().max()


def save_simple_plots(df_spots, outdir):
    if pd is None or plt is None:
        print('Plotting dependencies not available; skipping plot generation.')
        return

    os.makedirs(outdir, exist_ok=True)
    sns.set(style='whitegrid')

    # Spots per day
    df_spots['date'] = pd.to_datetime(df_spots['timestamp']).dt.date
    per_day = df_spots.groupby('date').size()
    plt.figure(figsize=(10,4))
    per_day.plot(kind='line')
    plt.title('Spots per day')
    plt.ylabel('Count')
    plt.tight_layout()
    path = os.path.join(outdir, 'spots_per_day.png')
    plt.savefig(path)
    plt.close()
    print(f'Saved plot: {path}')

    # Band distribution
    band_counts = df_spots['band'].value_counts(dropna=True)
    plt.figure(figsize=(8,5))
    sns.barplot(x=band_counts.index, y=band_counts.values)
    plt.title('Band distribution')
    plt.ylabel('Count')
    plt.xlabel('Band')
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.join(outdir, 'band_distribution.png')
    plt.savefig(path)
    plt.close()
    print(f'Saved plot: {path}')

    # Top DX calls
    top_calls = df_spots['dx_call'].value_counts().head(20)
    plt.figure(figsize=(8,6))
    sns.barplot(y=top_calls.index, x=top_calls.values, orient='h')
    plt.title('Top DX Calls')
    plt.xlabel('Spots')
    plt.tight_layout()
    path = os.path.join(outdir, 'top_dx_calls.png')
    plt.savefig(path)
    plt.close()
    print(f'Saved plot: {path}')

    # Heatmap (hour vs band)
    try:
        generate_heatmap(df_spots, outdir)
    except Exception as e:
        print(f'Failed to generate heatmap: {e}')

    # Grid-square mapping
    try:
        generate_grid_map(df_spots, outdir)
    except Exception as e:
        print(f'Failed to generate grid map: {e}')


def main():
    parser = argparse.ArgumentParser(description='Analyze DX cluster SQLite database')
    parser.add_argument('--db', '-d', default=DB_DEFAULT, help='Path to sqlite DB')
    parser.add_argument('--top', '-t', type=int, default=10, help='Top-N to show')
    parser.add_argument('--plots', action='store_true', help='Save plots (requires matplotlib/seaborn/pandas)')
    parser.add_argument('--outdir', default='analysis_outputs', help='Output directory for plots')
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f'Database file not found: {args.db}', file=sys.stderr)
        sys.exit(1)

    df_spots, df_calls = load_tables(args.db)

    print_basic_stats(df_spots, df_calls)

    print('\n=== Top spotted DX calls ===')
    for call, cnt in top_n_by_count(df_spots, 'dx_call', args.top):
        print(f'{call:12}  {cnt}')

    print('\n=== Top spotter calls ===')
    for call, cnt in top_n_by_count(df_spots, 'spotter_call', args.top):
        print(f'{call:12}  {cnt}')

    print('\n=== Band distribution (top) ===')
    if pd is not None:
        print(band_distribution(df_spots).head(10).to_string())
    else:
        print('Pandas not available')

    print('\n=== Mode distribution (top) ===')
    if pd is not None:
        print(mode_distribution(df_spots).head(10).to_string())
    else:
        print('Pandas not available')

    bh = busiest_hour(df_spots)
    if bh:
        print(f'\nBusiest hour (UTC): {bh[0]}:00 with {bh[1]} spots')

    if args.plots:
        save_simple_plots(df_spots, args.outdir)


def generate_heatmap(df_spots, outdir):
    """Generate and save a heatmap of hour (UTC) vs band activity counts."""
    if pd is None or plt is None or sns is None:
        print('Plotting dependencies not available; skipping heatmap.')
        return

    os.makedirs(outdir, exist_ok=True)
    df_spots = df_spots.copy()
    df_spots['hour'] = pd.to_datetime(df_spots['timestamp']).dt.hour
    pivot = df_spots.pivot_table(index='hour', columns='band', values='id', aggfunc='count', fill_value=0)
    pivot = pivot.reindex(range(24), fill_value=0)
    plt.figure(figsize=(12,6))
    sns.heatmap(pivot, cmap='viridis', linewidths=0.5, linecolor='gray')
    plt.title('Heatmap: Hour (UTC) vs Band (activity count)')
    plt.ylabel('Hour (UTC)')
    plt.xlabel('Band')
    plt.tight_layout()
    path = os.path.join(outdir, 'heatmap_hour_band.png')
    plt.savefig(path)
    plt.close()
    print(f'Saved plot: {path}')


def maiden_to_latlon(grid):
    """Convert Maidenhead grid (4 or 6 chars) to approximate (lat, lon) center."""
    if not isinstance(grid, str):
        return None
    g = grid.strip().upper()
    if len(g) < 4:
        return None
    try:
        A = ord('A')
        lon = (ord(g[0]) - A) * 20 - 180
        lat = (ord(g[1]) - A) * 10 - 90
        lon += int(g[2]) * 2
        lat += int(g[3]) * 1
        if len(g) >= 6:
            lon += (ord(g[4]) - A) * (5.0/60.0)
            lat += (ord(g[5]) - A) * (2.5/60.0)
            # center of subsquare
            lon += (5.0/60.0) / 2
            lat += (2.5/60.0) / 2
        else:
            # center of 4-char square
            lon += 1.0
            lat += 0.5
        return (lat, lon)
    except Exception:
        return None


def generate_grid_map(df_spots, outdir):
    """Aggregate grid squares, convert to lat/lon and save a map (uses geopandas if available)."""
    if pd is None or plt is None:
        print('Plotting dependencies not available; skipping grid map.')
        return

    os.makedirs(outdir, exist_ok=True)
    df_grid = df_spots.dropna(subset=['grid_square']).copy()
    if df_grid.empty:
        print('No grid_square data found in dataset; skipping grid map.')
        return

    df_grid['grid'] = df_grid['grid_square'].str.strip()
    df_grid['latlon'] = df_grid['grid'].apply(maiden_to_latlon)
    df_grid = df_grid.dropna(subset=['latlon']).copy()
    if df_grid.empty:
        print('No valid grid_square conversions; skipping grid map.')
        return
    df_grid['lat'] = df_grid['latlon'].apply(lambda x: x[0])
    df_grid['lon'] = df_grid['latlon'].apply(lambda x: x[1])

    agg = df_grid.groupby('grid').agg(count=('id','size'), lat=('lat','mean'), lon=('lon','mean')).reset_index()
    agg = agg.sort_values('count', ascending=False)
    # Save aggregated CSV
    csv_path = os.path.join(outdir, 'grid_square_counts.csv')
    agg.to_csv(csv_path, index=False)
    print(f'Saved CSV: {csv_path}')

    # Plot
    try:
        if gpd is not None:
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            fig, ax = plt.subplots(figsize=(12,6))
            world.plot(ax=ax, color='lightgray', edgecolor='white')
            sc = ax.scatter(agg['lon'], agg['lat'], s=agg['count']*10, c=agg['count'], cmap='Reds', alpha=0.7, edgecolor='k')
            plt.colorbar(sc, ax=ax, label='Spot count')
            ax.set_title('Grid-square spot density (approx center)')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            plt.tight_layout()
            path = os.path.join(outdir, 'grid_square_map.png')
            plt.savefig(path)
            plt.close()
            print(f'Saved plot: {path}')
        else:
            plt.figure(figsize=(12,6))
            plt.scatter(agg['lon'], agg['lat'], s=agg['count']*10, c=agg['count'], cmap='Reds', alpha=0.7, edgecolor='k')
            plt.colorbar(label='Spot count')
            plt.title('Grid-square spot density (approx center)')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            path = os.path.join(outdir, 'grid_square_map.png')
            plt.savefig(path)
            plt.close()
            print(f'Saved plot: {path}')
    except Exception as e:
        print(f'Error plotting grid map: {e}')


if __name__ == '__main__':
    main()

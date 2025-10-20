#!/usr/bin/env python3
"""
DX Cluster Dashboard - API Client Version

Modified Dash application that uses the JSON API instead of direct database queries.
"""

import os
import requests
from datetime import datetime, timedelta
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime

# Load environment variables
load_dotenv()  # Load default .env
load_dotenv('/home/steve/GITHUB/cs330-projects/homework2/.env.local')  # Load local config

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def api_request(endpoint, params=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error for {endpoint}: {e}")
        return None

# Layout components
header = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("DX Cluster Monitor (API Version)", className="ms-2"),
        html.Span(f"API: {API_BASE_URL}", className="navbar-text me-2")
    ]),
    color="primary",
    dark=True,
)

# Real-time stats card
stats_card = dbc.Card([
    dbc.CardHeader("Real-time Statistics"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H5("Total Spots"),
                html.H3(id="total-spots", children="0")
            ], width=3),
            dbc.Col([
                html.H5("DX Stations"),
                html.H3(id="dx-stations", children="0")
            ], width=3),
            dbc.Col([
                html.H5("Spotters"),
                html.H3(id="spotters", children="0")
            ], width=3),
            dbc.Col([
                html.H5("Today's Spots"),
                html.H3(id="spots-today", children="0")
            ], width=3),
        ])
    ])
])

# Band activity card
band_activity_card = dbc.Card([
    dbc.CardHeader("Band Activity"),
    dbc.CardBody([
        dcc.Graph(id='band-activity-chart')
    ])
])

# Recent spots card
recent_spots_card = dbc.Card([
    dbc.CardHeader("Recent Spots (Last Hour)"),
    dbc.CardBody([
        html.Div(id="recent-spots-table")
    ])
])

# Frequency distribution card
freq_dist_card = dbc.Card([
    dbc.CardHeader("Frequency Distribution"),
    dbc.CardBody([
        dcc.Graph(id='frequency-histogram')
    ])
])

# Main layout
app.layout = html.Div([
    header,
    dbc.Container([
        html.Br(),
        dbc.Row([
            dbc.Col([stats_card], width=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='hourly-activity-graph'),
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # 30 seconds
                    n_intervals=0
                )
            ], width=8),
            dbc.Col([recent_spots_card], width=4)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([band_activity_card], width=6),
            dbc.Col([freq_dist_card], width=6)
        ])
    ], fluid=True)
])

# Callback for updating all components
@app.callback(
    [Output('total-spots', 'children'),
     Output('dx-stations', 'children'),
     Output('spotters', 'children'),
     Output('spots-today', 'children'),
     Output('hourly-activity-graph', 'figure'),
     Output('recent-spots-table', 'children'),
     Output('band-activity-chart', 'figure'),
     Output('frequency-histogram', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    try:
        # Get basic statistics
        stats_data = api_request('stats')
        if not stats_data:
            return generate_error_outputs("Failed to load statistics")
        
        total_spots = stats_data['total']['total_spots']
        dx_stations = stats_data['total']['unique_dx_stations'] 
        spotters = stats_data['total']['unique_spotters']
        spots_today = stats_data['today']['spots_today']
        
        # Get hourly activity
        activity_data = api_request('activity/hourly', {'hours': 24})
        hourly_figure = create_hourly_activity_chart(activity_data)
        
        # Get recent spots
        recent_data = api_request('spots/recent', {'hours': 1, 'limit': 10})
        recent_table = create_recent_spots_table(recent_data)
        
        # Get band activity
        bands_data = api_request('bands')
        band_figure = create_band_activity_chart(bands_data)
        
        # Get frequency histogram
        freq_data = api_request('frequency/histogram', {'bins': 30})
        freq_figure = create_frequency_histogram(freq_data)
        
        return (
            f"{total_spots:,}",
            f"{dx_stations:,}",
            f"{spotters:,}",
            f"{spots_today:,}",
            hourly_figure,
            recent_table,
            band_figure,
            freq_figure
        )
        
    except Exception as e:
        print(f"Dashboard update error: {e}")
        return generate_error_outputs(f"Dashboard error: {str(e)}")

def generate_error_outputs(error_msg):
    """Generate error outputs for all dashboard components"""
    error_figure = {
        'data': [],
        'layout': {
            'title': 'Error Loading Data',
            'template': 'plotly_dark',
            'annotations': [{
                'text': error_msg,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False
            }]
        }
    }
    
    error_table = html.Div([
        html.P(f"Error: {error_msg}", className="text-danger")
    ])
    
    return (
        "Error", "Error", "Error", "Error",
        error_figure, error_table, error_figure, error_figure
    )

def create_hourly_activity_chart(activity_data):
    """Create hourly activity chart from API data"""
    if not activity_data or 'activity' not in activity_data:
        return create_demo_hourly_chart()
    
    activity = activity_data['activity']
    if not activity:
        return create_demo_hourly_chart()
    
    hours = [item['hour'] for item in activity]
    spot_counts = [item['spot_count'] for item in activity]
    
    return {
        'data': [{
            'x': hours,
            'y': spot_counts,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Spots per Hour',
            'line': {'color': '#1f77b4', 'width': 2},
            'marker': {'size': 6}
        }],
        'layout': {
            'title': 'DX Spots Over Last 24 Hours',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Number of Spots'},
            'template': 'plotly_dark',
            'height': 400
        }
    }

def create_demo_hourly_chart():
    """Create demo chart when no data available"""
    import random
    demo_hours = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                              end=datetime.now(), freq='H')
    demo_counts = [random.randint(5, 25) for _ in demo_hours]
    
    return {
        'data': [{
            'x': demo_hours,
            'y': demo_counts,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Demo Data'
        }],
        'layout': {
            'title': 'DX Spots Over Last 24 Hours (Demo Mode)',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Number of Spots'},
            'template': 'plotly_dark',
            'height': 400
        }
    }

def create_recent_spots_table(recent_data):
    """Create recent spots table from API data"""
    if not recent_data or 'spots' not in recent_data:
        return html.P("No recent spots available", className="text-muted")
    
    spots = recent_data['spots']
    if not spots:
        return html.P("No spots in the last hour", className="text-muted")
    
    table_rows = []
    for spot in spots[:10]:  # Limit to 10 spots
        try:
            # Parse RFC format timestamp: "Mon, 20 Oct 2025 17:56:58 GMT"
            timestamp = parsedate_to_datetime(spot['timestamp'])
            time_str = timestamp.strftime('%H:%M:%S')
        except (ValueError, TypeError) as e:
            print(f"Error parsing timestamp '{spot['timestamp']}': {e}")
            time_str = "N/A"
        
        freq_str = f"{float(spot['frequency']):.1f}"
        
        row = html.Tr([
            html.Td(time_str, className="font-monospace small"),
            html.Td(spot['dx_call'], className="fw-bold"),
            html.Td(freq_str, className="font-monospace"),
            html.Td(spot['spotter_call']),
        ])
        table_rows.append(row)
    
    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Time"),
                    html.Th("DX"),
                    html.Th("Freq"),
                    html.Th("Spotter")
                ])
            ], className="table-dark"),
            html.Tbody(table_rows)
        ], className="table table-sm table-hover")
    ])

def create_band_activity_chart(bands_data):
    """Create band activity chart from API data"""
    if not bands_data or 'bands' not in bands_data:
        return create_demo_band_chart()
    
    bands = bands_data['bands']
    if not bands:
        return create_demo_band_chart()
    
    # Sort by spot count and take top 10
    bands = sorted(bands, key=lambda x: x['spot_count'], reverse=True)[:10]
    
    band_names = [band['band'] for band in bands]
    spot_counts = [band['spot_count'] for band in bands]
    
    return {
        'data': [{
            'x': spot_counts,
            'y': band_names,
            'type': 'bar',
            'orientation': 'h',
            'marker': {'color': '#2ca02c'}
        }],
        'layout': {
            'title': 'Spots by Band',
            'xaxis': {'title': 'Number of Spots'},
            'yaxis': {'title': 'Band'},
            'template': 'plotly_dark',
            'height': 400
        }
    }

def create_demo_band_chart():
    """Create demo band chart when no data available"""
    demo_bands = ['20m', '40m', '80m', '15m', '10m', '17m']
    demo_counts = [150, 120, 80, 75, 60, 45]
    
    return {
        'data': [{
            'x': demo_counts,
            'y': demo_bands,
            'type': 'bar',
            'orientation': 'h',
            'marker': {'color': '#2ca02c'}
        }],
        'layout': {
            'title': 'Spots by Band (Demo Mode)',
            'xaxis': {'title': 'Number of Spots'},
            'yaxis': {'title': 'Band'},
            'template': 'plotly_dark',
            'height': 400
        }
    }

def create_frequency_histogram(freq_data):
    """Create frequency histogram from API data"""
    if not freq_data or 'histogram' not in freq_data:
        return create_demo_freq_chart()
    
    histogram = freq_data['histogram']
    if not histogram:
        return create_demo_freq_chart()
    
    # Calculate bin centers for x-axis
    bin_centers = []
    spot_counts = []
    
    for bin_data in histogram:
        bin_min = float(bin_data['bin_min_freq'])
        bin_max = float(bin_data['bin_max_freq'])
        bin_center = (bin_min + bin_max) / 2
        bin_centers.append(bin_center)
        spot_counts.append(bin_data['spot_count'])
    
    return {
        'data': [{
            'x': bin_centers,
            'y': spot_counts,
            'type': 'bar',
            'marker': {'color': '#ff7f0e'}
        }],
        'layout': {
            'title': 'Frequency Distribution',
            'xaxis': {'title': 'Frequency (kHz)'},
            'yaxis': {'title': 'Number of Spots'},
            'template': 'plotly_dark',
            'height': 400
        }
    }

def create_demo_freq_chart():
    """Create demo frequency chart when no data available"""
    import random
    demo_freqs = list(range(7000, 30000, 1000))
    demo_counts = [random.randint(10, 100) for _ in demo_freqs]
    
    return {
        'data': [{
            'x': demo_freqs,
            'y': demo_counts,
            'type': 'bar',
            'marker': {'color': '#ff7f0e'}
        }],
        'layout': {
            'title': 'Frequency Distribution (Demo Mode)',
            'xaxis': {'title': 'Frequency (kHz)'},
            'yaxis': {'title': 'Number of Spots'},
            'template': 'plotly_dark',
            'height': 400
        }
    }

if __name__ == '__main__':
    # Test API connection on startup
    health_data = api_request('health')
    if health_data:
        print(f"✓ API connection successful: {health_data}")
    else:
        print("⚠ Warning: Could not connect to API. Dashboard will run in demo mode.")
    
    print(f"Starting dashboard with API base URL: {API_BASE_URL}")
    app.run_server(debug=True, host='0.0.0.0', port=8051)
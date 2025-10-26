import os
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, timedelta
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Database connection function
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("PGHOST"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD")
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Layout components
header = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("DX Cluster Monitor", className="ms-2"),
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
                html.H5("Total Spots Today"),
                html.H3(id="total-spots", children="0")
            ], width=3),
            dbc.Col([
                html.H5("Active Stations"),
                html.H3(id="active-stations", children="0")
            ], width=3),
            dbc.Col([
                html.H5("Latest Update"),
                html.H3(id="latest-update", children="--:--")
            ], width=3),
            dbc.Col([
                html.H5("Total Records"),
                html.H3(id="total-records", children="0")
            ], width=3),
        ])
    ])
])

# Database statistics card
db_stats = dbc.Card([
    dbc.CardHeader("Database Statistics"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H5("Last 24 Hours"),
                html.Div(id="stats-24h")
            ], width=6),
            dbc.Col([
                html.H5("Last 7 Days"),
                html.Div(id="stats-7d")
            ], width=6)
        ])
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
            dbc.Col([db_stats], width=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='live-spots-graph'),
                dcc.Interval(
                    id='interval-component',
                    interval=10*1000,  # in milliseconds (10 seconds)
                    n_intervals=0
                )
            ])
        ])
    ], fluid=True)
])

# Callback for updating statistics
@app.callback(
    [Output('total-spots', 'children'),
     Output('active-stations', 'children'),
     Output('latest-update', 'children'),
     Output('total-records', 'children'),
     Output('live-spots-graph', 'figure'),
     Output('stats-24h', 'children'),
     Output('stats-7d', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_stats(n):
    try:
        conn = get_db_connection()
        if not conn:
            # Return demo data if no database connection
            import random
            demo_hours = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                     end=datetime.now(), freq='H')
            demo_counts = [random.randint(5, 25) for _ in demo_hours]
            
            graph_figure = {
                'data': [{
                    'x': demo_hours,
                    'y': demo_counts,
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': 'Spots per Hour (Demo Data)'
                }],
                'layout': {
                    'title': 'DX Spots Over Last 24 Hours (Demo Mode)',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Number of Spots'},
                    'template': 'plotly_dark'
                }
            }
            
            demo_24h_stats = html.Div([
                html.P([html.Strong("Total Spots: "), html.Span("250")]),
                html.P([html.Strong("Unique Spotters: "), html.Span("42")]),
                html.P([html.Strong("Unique DX Stations: "), html.Span("85")]),
            ])
            
            demo_7d_stats = html.Div([
                html.P([html.Strong("Total Spots: "), html.Span("1,750")]),
                html.P([html.Strong("Unique Spotters: "), html.Span("156")]),
                html.P([html.Strong("Unique DX Stations: "), html.Span("420")]),
            ])
            
            return (
                str(random.randint(100, 500)),  # Demo total spots today
                str(random.randint(20, 80)),    # Demo active stations
                datetime.now().strftime("%H:%M:%S"),
                str(random.randint(10000, 50000)),  # Demo total records
                graph_figure,
                demo_24h_stats,
                demo_7d_stats
            )
        
        cur = conn.cursor()
        
        # Get today's total spots
        cur.execute("""
            SELECT COUNT(*) 
            FROM dx_spots 
            WHERE DATE(timestamp) = CURRENT_DATE
        """)
        total_spots = cur.fetchone()[0]
        
        # Get active stations in last hour
        cur.execute("""
            SELECT COUNT(DISTINCT spotter_call) 
            FROM dx_spots 
            WHERE spot_time >= NOW() - INTERVAL '1 hour'
        """)
        active_stations = cur.fetchone()[0]
        
        # Get total records count
        cur.execute("SELECT COUNT(*) FROM dx_spots")
        total_records = cur.fetchone()[0]
        
        # Get spots by hour for graph
        cur.execute("""
            SELECT DATE_TRUNC('hour', spot_time) as hour,
                   COUNT(*) as spot_count
            FROM dx_spots
            WHERE spot_time >= NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour
        """)
        results = cur.fetchall()
        df = pd.DataFrame(results, columns=['hour', 'spot_count'])
        
        # Get 24h statistics
        cur.execute("""
            SELECT
                COUNT(*) as total_spots,
                COUNT(DISTINCT spotter_call) as unique_spotters,
                COUNT(DISTINCT dx_call) as unique_dx_stations
            FROM dx_spots
            WHERE spot_time >= NOW() - INTERVAL '24 hours'
        """)
        stats_24h = cur.fetchone()
        
        # Get 7d statistics
        cur.execute("""
            SELECT
                COUNT(*) as total_spots,
                COUNT(DISTINCT spotter_call) as unique_spotters,
                COUNT(DISTINCT dx_call) as unique_dx_stations
            FROM dx_spots
            WHERE spot_time >= NOW() - INTERVAL '7 days'
        """)
        stats_7d = cur.fetchone()
        
        cur.close()
        conn.close()
        
        # Create graph
        graph_figure = {
            'data': [{
                'x': df['hour'],
                'y': df['spot_count'],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Spots per Hour'
            }],
            'layout': {
                'title': 'DX Spots Over Last 24 Hours',
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': 'Number of Spots'},
                'template': 'plotly_dark'
            }
        }
        
        # Format statistics
        stats_24h_display = html.Div([
            html.P([html.Strong("Total Spots: "), html.Span(str(stats_24h[0]))]),
            html.P([html.Strong("Unique Spotters: "), html.Span(str(stats_24h[1]))]),
            html.P([html.Strong("Unique DX Stations: "), html.Span(str(stats_24h[2]))]),
        ])
        
        stats_7d_display = html.Div([
            html.P([html.Strong("Total Spots: "), html.Span(str(stats_7d[0]))]),
            html.P([html.Strong("Unique Spotters: "), html.Span(str(stats_7d[1]))]),
            html.P([html.Strong("Unique DX Stations: "), html.Span(str(stats_7d[2]))]),
        ])
        
        return (
            str(total_spots),
            str(active_stations),
            datetime.now().strftime("%H:%M:%S"),
            str(total_records),
            graph_figure,
            stats_24h_display,
            stats_7d_display
        )
        
    except Exception as e:
        print(f"Error updating stats: {e}")
        # Return demo data on error
        import random
        demo_hours = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                 end=datetime.now(), freq='H')
        demo_counts = [random.randint(5, 25) for _ in demo_hours]
        
        graph_figure = {
            'data': [{
                'x': demo_hours,
                'y': demo_counts,
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Spots per Hour (Demo Data)'
            }],
            'layout': {
                'title': 'DX Spots Over Last 24 Hours (Demo Mode - DB Error)',
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': 'Number of Spots'},
                'template': 'plotly_dark'
            }
        }
        
        error_24h_stats = html.Div([
            html.P([html.Strong("Total Spots: "), html.Span("Error")]),
            html.P([html.Strong("Unique Spotters: "), html.Span("Error")]),
            html.P([html.Strong("Unique DX Stations: "), html.Span("Error")]),
        ])
        
        error_7d_stats = html.Div([
            html.P([html.Strong("Total Spots: "), html.Span("Error")]),
            html.P([html.Strong("Unique Spotters: "), html.Span("Error")]),
            html.P([html.Strong("Unique DX Stations: "), html.Span("Error")]),
        ])
        
        return (
            "Error",
            "Error",
            datetime.now().strftime("%H:%M:%S"),
            "Error",
            graph_figure,
            error_24h_stats,
            error_7d_stats
        )

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
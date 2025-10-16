import os
from dash import Dash, html, dcc, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, timedelta
import pandas as pd
from scraper_control import scraper_manager

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

# Scraper control card
scraper_control = dbc.Card([
    dbc.CardHeader("Scraper Control"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Button("Start Scraper", id="start-scraper", color="success", className="me-2"),
                dbc.Button("Stop Scraper", id="stop-scraper", color="danger", className="me-2"),
                html.Div([
                    html.H5("Status: ", className="d-inline"),
                    html.Span(id="scraper-status", className="ms-2"),
                ], className="mt-3"),
                html.Div([
                    html.H5("Last Error: ", className="d-inline"),
                    html.Span(id="last-error", className="ms-2 text-danger"),
                ], className="mt-2"),
                html.Div([
                    html.H5("Running Since: ", className="d-inline"),
                    html.Span(id="start-time", className="ms-2"),
                ], className="mt-2"),
            ])
        ])
    ])
])

# Real-time stats card
stats_card = dbc.Card([
    dbc.CardHeader("Real-time Statistics"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H5("Total Spots Today"),
                html.H3(id="total-spots", children="0")
            ], width=4),
            dbc.Col([
                html.H5("Active Stations"),
                html.H3(id="active-stations", children="0")
            ], width=4),
            dbc.Col([
                html.H5("Latest Update"),
                html.H3(id="latest-update", children="--:--")
            ], width=4),
        ])
    ])
])

# Log display card
log_display = dbc.Card([
    dbc.CardHeader("Scraper Logs"),
    dbc.CardBody([
        html.Div(id="log-content", style={'height': '300px', 'overflowY': 'scroll', 'fontFamily': 'monospace'})
    ])
])

# Scraper statistics card
scraper_stats = dbc.Card([
    dbc.CardHeader("Scraper Statistics"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H5("Last 24 Hours"),
                html.Div(id="stats-24h")
            ])
        ])
    ])
])

# Main layout
app.layout = html.Div([
    header,
    dbc.Container([
        html.Br(),
        dbc.Row([
            dbc.Col([scraper_control], width=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([stats_card], width=6),
            dbc.Col([scraper_stats], width=6)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([log_display], width=12)
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
     Output('live-spots-graph', 'figure')],
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
            
            return (
                str(random.randint(100, 500)),  # Demo total spots
                str(random.randint(20, 80)),    # Demo active stations
                datetime.now().strftime("%H:%M:%S"),
                graph_figure
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
        
        return (
            str(total_spots),
            str(active_stations),
            datetime.now().strftime("%H:%M:%S"),
            graph_figure
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
        
        return (
            "Demo: 250",
            "Demo: 42",
            datetime.now().strftime("%H:%M:%S"),
            graph_figure
        )

# Callback for scraper control buttons
@app.callback(
    [Output("scraper-status", "children"),
     Output("last-error", "children"),
     Output("start-time", "children")],
    [Input("start-scraper", "n_clicks"),
     Input("stop-scraper", "n_clicks"),
     Input("interval-component", "n_intervals")],
    [State("scraper-status", "children")]
)
def control_scraper(start_clicks, stop_clicks, n_intervals, current_status):
    ctx = callback_context
    status = scraper_manager.get_status()
    
    if ctx.triggered and ctx.triggered[0]["prop_id"] != "interval-component.n_intervals":
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "start-scraper":
            scraper_manager.start_scraper()
        elif button_id == "stop-scraper":
            scraper_manager.stop_scraper()
    
    status_color = {
        "running": "text-success",
        "stopped": "text-warning",
        "error": "text-danger"
    }.get(status["status"], "")
    
    return (
        html.Span(status["status"].upper(), className=status_color),
        status["last_error"] or "None",
        status["start_time"] or "Not started"
    )

# Callback for updating log display
@app.callback(
    Output("log-content", "children"),
    Input("interval-component", "n_intervals")
)
def update_logs(n):
    status = scraper_manager.get_status()
    logs = status.get("recent_logs", [])
    return [html.Div(log, className="log-line") for log in logs]

# Callback for updating scraper statistics
@app.callback(
    Output("stats-24h", "children"),
    Input("interval-component", "n_intervals")
)
def update_scraper_stats(n):
    status = scraper_manager.get_status()
    stats = status.get("statistics", {})
    
    if not stats:
        return "No statistics available"
    
    return html.Div([
        html.P([
            html.Strong("Total Spots: "),
            html.Span(stats.get("last_24h_spots", 0))
        ]),
        html.P([
            html.Strong("Unique Spotters: "),
            html.Span(stats.get("last_24h_spotters", 0))
        ]),
        html.P([
            html.Strong("Unique DX Stations: "),
            html.Span(stats.get("last_24h_dx_stations", 0))
        ]),
        html.P([
            html.Strong("Last Spot: "),
            html.Span(stats.get("last_spot_time", "Never"))
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
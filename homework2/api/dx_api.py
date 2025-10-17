#!/usr/bin/env python3
"""
DX Cluster JSON API Server

A REST API for querying DX cluster spot data from PostgreSQL database.
Provides endpoints for statistics, spot data, and filtering capabilities.
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import json
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Database configuration
DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'database': os.getenv('PGDATABASE', 'dxcluster'),
    'user': os.getenv('PGUSER', 'dx_reader'),
    'password': os.getenv('PGPASSWORD'),
    'port': os.getenv('PGPORT', '5432')
}

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and decimal objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def validate_parameters(params, allowed_params):
    """Validate request parameters"""
    invalid_params = set(params.keys()) - set(allowed_params)
    if invalid_params:
        abort(400, description=f"Invalid parameters: {', '.join(invalid_params)}")

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error.description)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'Database or server error'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    else:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500

@app.route('/api/stats')
def get_stats():
    """Get basic statistics about the database"""
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get basic counts
        cur.execute("""
            SELECT 
                COUNT(*) as total_spots,
                COUNT(DISTINCT dx_call) as unique_dx_stations,
                COUNT(DISTINCT spotter_call) as unique_spotters,
                MIN(timestamp) as earliest_spot,
                MAX(timestamp) as latest_spot
            FROM dx_spots
        """)
        basic_stats = cur.fetchone()
        
        # Get today's stats
        cur.execute("""
            SELECT 
                COUNT(*) as spots_today,
                COUNT(DISTINCT dx_call) as dx_stations_today,
                COUNT(DISTINCT spotter_call) as spotters_today
            FROM dx_spots 
            WHERE DATE(timestamp) = CURRENT_DATE
        """)
        today_stats = cur.fetchone()
        
        # Get recent activity (last hour)
        cur.execute("""
            SELECT 
                COUNT(*) as spots_last_hour,
                COUNT(DISTINCT spotter_call) as active_spotters
            FROM dx_spots 
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
        """)
        recent_stats = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total': dict(basic_stats),
            'today': dict(today_stats),
            'recent': dict(recent_stats),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        abort(500, description="Error retrieving statistics")

@app.route('/api/spots')
def get_spots():
    """Get DX spots with optional filtering"""
    # Define allowed parameters
    allowed_params = {
        'limit', 'offset', 'dx_call', 'spotter_call', 'frequency_min', 'frequency_max',
        'band', 'mode', 'since', 'until', 'grid_square', 'comment_contains', 'order_by'
    }
    
    validate_parameters(request.args, allowed_params)
    
    # Parse parameters
    limit = min(int(request.args.get('limit', 100)), 1000)  # Max 1000 records
    offset = int(request.args.get('offset', 0))
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if request.args.get('dx_call'):
        where_conditions.append("dx_call ILIKE %s")
        params.append(f"%{request.args.get('dx_call')}%")
    
    if request.args.get('spotter_call'):
        where_conditions.append("spotter_call ILIKE %s")
        params.append(f"%{request.args.get('spotter_call')}%")
    
    if request.args.get('frequency_min'):
        where_conditions.append("frequency >= %s")
        params.append(float(request.args.get('frequency_min')))
    
    if request.args.get('frequency_max'):
        where_conditions.append("frequency <= %s")
        params.append(float(request.args.get('frequency_max')))
    
    if request.args.get('band'):
        where_conditions.append("band = %s")
        params.append(request.args.get('band'))
    
    if request.args.get('mode'):
        where_conditions.append("mode ILIKE %s")
        params.append(f"%{request.args.get('mode')}%")
    
    if request.args.get('since'):
        try:
            since_dt = datetime.fromisoformat(request.args.get('since').replace('Z', '+00:00'))
            where_conditions.append("timestamp >= %s")
            params.append(since_dt)
        except ValueError:
            abort(400, description="Invalid 'since' datetime format. Use ISO format.")
    
    if request.args.get('until'):
        try:
            until_dt = datetime.fromisoformat(request.args.get('until').replace('Z', '+00:00'))
            where_conditions.append("timestamp <= %s")
            params.append(until_dt)
        except ValueError:
            abort(400, description="Invalid 'until' datetime format. Use ISO format.")
    
    if request.args.get('grid_square'):
        where_conditions.append("grid_square ILIKE %s")
        params.append(f"%{request.args.get('grid_square')}%")
    
    if request.args.get('comment_contains'):
        where_conditions.append("comment ILIKE %s")
        params.append(f"%{request.args.get('comment_contains')}%")
    
    # Build ORDER BY clause
    order_by = request.args.get('order_by', 'timestamp DESC')
    allowed_order_fields = ['timestamp', 'frequency', 'dx_call', 'spotter_call']
    order_field = order_by.split()[0]
    if order_field not in allowed_order_fields:
        abort(400, description=f"Invalid order_by field. Allowed: {', '.join(allowed_order_fields)}")
    
    # Build the query
    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
    
    query = f"""
        SELECT 
            id, timestamp, dx_call, frequency, spotter_call, 
            comment, mode, signal_report, grid_square, band
        FROM dx_spots 
        {where_clause}
        ORDER BY {order_by}
        LIMIT %s OFFSET %s
    """
    
    params.extend([limit, offset])
    
    # Count query for pagination
    count_query = f"""
        SELECT COUNT(*) as total
        FROM dx_spots 
        {where_clause}
    """
    
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total count
        cur.execute(count_query, params[:-2])  # Exclude limit and offset
        total_count = cur.fetchone()['total']
        
        # Get spots
        cur.execute(query, params)
        spots = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'spots': [dict(spot) for spot in spots],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting spots: {e}")
        abort(500, description="Error retrieving spots")

@app.route('/api/spots/recent')
def get_recent_spots():
    """Get recent spots (last N hours)"""
    hours = min(int(request.args.get('hours', 24)), 168)  # Max 7 days
    limit = min(int(request.args.get('limit', 50)), 500)
    
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                id, timestamp, dx_call, frequency, spotter_call, 
                comment, mode, signal_report, grid_square, band
            FROM dx_spots 
            WHERE timestamp >= NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
            LIMIT %s
        """, (hours, limit))
        
        spots = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'spots': [dict(spot) for spot in spots],
            'hours': hours,
            'count': len(spots),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recent spots: {e}")
        abort(500, description="Error retrieving recent spots")

@app.route('/api/bands')
def get_bands():
    """Get list of active bands with spot counts"""
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                band,
                COUNT(*) as spot_count,
                COUNT(DISTINCT dx_call) as dx_stations,
                MIN(frequency) as min_freq,
                MAX(frequency) as max_freq,
                MAX(timestamp) as latest_spot
            FROM dx_spots 
            WHERE band IS NOT NULL
            GROUP BY band
            ORDER BY spot_count DESC
        """)
        
        bands = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'bands': [dict(band) for band in bands],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting bands: {e}")
        abort(500, description="Error retrieving band information")

@app.route('/api/frequency/histogram')
def get_frequency_histogram():
    """Get frequency distribution histogram"""
    bins = min(int(request.args.get('bins', 50)), 200)  # Max 200 bins
    
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                MIN(frequency) as min_freq,
                MAX(frequency) as max_freq,
                COUNT(*) as total_spots
            FROM dx_spots
        """)
        
        freq_range = cur.fetchone()
        
        if freq_range['total_spots'] == 0:
            return jsonify({
                'histogram': [],
                'bins': 0,
                'total_spots': 0,
                'timestamp': datetime.now().isoformat()
            })
        
        # Calculate bin width
        min_freq = float(freq_range['min_freq'])
        max_freq = float(freq_range['max_freq'])
        bin_width = (max_freq - min_freq) / bins
        
        cur.execute("""
            SELECT 
                FLOOR((frequency - %s) / %s) as bin_number,
                COUNT(*) as spot_count,
                MIN(frequency) as bin_min_freq,
                MAX(frequency) as bin_max_freq
            FROM dx_spots
            GROUP BY bin_number
            ORDER BY bin_number
        """, (min_freq, bin_width))
        
        histogram = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'histogram': [dict(bin_data) for bin_data in histogram],
            'bins': bins,
            'bin_width': bin_width,
            'frequency_range': {'min': min_freq, 'max': max_freq},
            'total_spots': freq_range['total_spots'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting frequency histogram: {e}")
        abort(500, description="Error retrieving frequency histogram")

@app.route('/api/activity/hourly')
def get_hourly_activity():
    """Get hourly activity statistics"""
    hours = min(int(request.args.get('hours', 24)), 168)  # Max 7 days
    
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as spot_count,
                COUNT(DISTINCT dx_call) as unique_dx_stations,
                COUNT(DISTINCT spotter_call) as unique_spotters
            FROM dx_spots
            WHERE timestamp >= NOW() - INTERVAL '%s hours'
            GROUP BY hour
            ORDER BY hour
        """, (hours,))
        
        activity = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'activity': [dict(hour_data) for hour_data in activity],
            'hours': hours,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting hourly activity: {e}")
        abort(500, description="Error retrieving hourly activity")

@app.route('/api/callsigns/top')
def get_top_callsigns():
    """Get top active callsigns (spotters and spotted)"""
    limit = min(int(request.args.get('limit', 20)), 100)
    category = request.args.get('category', 'both')  # 'spotters', 'spotted', or 'both'
    
    if category not in ['spotters', 'spotted', 'both']:
        abort(400, description="Invalid category. Use 'spotters', 'spotted', or 'both'")
    
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        result = {}
        
        if category in ['spotters', 'both']:
            cur.execute("""
                SELECT 
                    spotter_call as callsign,
                    COUNT(*) as spot_count,
                    COUNT(DISTINCT dx_call) as stations_spotted,
                    MAX(timestamp) as last_activity
                FROM dx_spots
                GROUP BY spotter_call
                ORDER BY spot_count DESC
                LIMIT %s
            """, (limit,))
            
            result['top_spotters'] = [dict(spotter) for spotter in cur.fetchall()]
        
        if category in ['spotted', 'both']:
            cur.execute("""
                SELECT 
                    dx_call as callsign,
                    COUNT(*) as times_spotted,
                    COUNT(DISTINCT spotter_call) as spotted_by,
                    MAX(timestamp) as last_spotted
                FROM dx_spots
                GROUP BY dx_call
                ORDER BY times_spotted DESC
                LIMIT %s
            """, (limit,))
            
            result['top_spotted'] = [dict(spotted) for spotted in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting top callsigns: {e}")
        abort(500, description="Error retrieving top callsigns")

@app.route('/')
def data_browser():
    """Serve the data browser HTML interface"""
    return send_from_directory('.', 'data_browser.html')

@app.route('/api')
def api_info():
    """API information and available endpoints"""
    endpoints = {
        'health': '/api/health - Health check',
        'stats': '/api/stats - Basic database statistics',
        'spots': '/api/spots - Get spots with filtering options',
        'recent_spots': '/api/spots/recent - Get recent spots',
        'bands': '/api/bands - Get band information',
        'frequency_histogram': '/api/frequency/histogram - Frequency distribution',
        'hourly_activity': '/api/activity/hourly - Hourly activity stats',
        'top_callsigns': '/api/callsigns/top - Top active callsigns',
        'data_browser': '/ - Interactive data browser interface'
    }
    
    return jsonify({
        'name': 'DX Cluster API',
        'version': '1.0.0',
        'description': 'REST API for DX cluster spot data',
        'endpoints': endpoints,
        'timestamp': datetime.now().isoformat()
    })

# Configure JSON encoder
app.json_encoder = DateTimeEncoder

if __name__ == '__main__':
    # Check database connection on startup
    if not get_db_connection():
        logger.error("Failed to connect to database on startup")
        sys.exit(1)
    
    logger.info("Starting DX Cluster API server")
    app.run(debug=True, host='0.0.0.0', port=5000)
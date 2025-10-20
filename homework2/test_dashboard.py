#!/usr/bin/env python3
"""
Test script to start the DX Cluster Dashboard locally
connecting to the cloud API server
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add the current directory to Python path for imports
sys.path.insert(0, '/home/steve/GITHUB/cs330-projects/homework2/api')

def test_api_connection(api_base_url):
    """Test connection to the API server"""
    try:
        print(f"Testing API connection to: {api_base_url}")
        
        # Test health endpoint
        health_url = f"{api_base_url}/health"
        response = requests.get(health_url, timeout=10)
        response.raise_for_status()
        
        health_data = response.json()
        print(f"✓ Health check passed: {health_data}")
        
        # Test stats endpoint
        stats_url = f"{api_base_url}/stats"
        response = requests.get(stats_url, timeout=10)
        response.raise_for_status()
        
        stats_data = response.json()
        print(f"✓ Stats endpoint working:")
        print(f"  - Total spots: {stats_data['total']['total_spots']:,}")
        print(f"  - Unique DX stations: {stats_data['total']['unique_dx_stations']:,}")
        print(f"  - Spots today: {stats_data['today']['spots_today']:,}")
        
        # Test recent spots
        recent_url = f"{api_base_url}/spots/recent"
        response = requests.get(recent_url, timeout=10, params={'limit': 5})
        response.raise_for_status()
        
        recent_data = response.json()
        print(f"✓ Recent spots endpoint working:")
        print(f"  - Retrieved {len(recent_data['spots'])} recent spots")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ API connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    print("=== DX Cluster Dashboard Test Startup ===")
    
    # Load local environment configuration
    env_file = '/home/steve/GITHUB/cs330-projects/homework2/.env.local'
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✓ Loaded environment from: {env_file}")
    else:
        print(f"⚠ Environment file not found: {env_file}")
        return 1
    
    # Get API configuration
    api_base_url = os.getenv('API_BASE_URL', 'http://dx.jxqz.org:8080/api')
    print(f"API Base URL: {api_base_url}")
    
    # Test API connection
    if not test_api_connection(api_base_url):
        print("\n⚠ API connection test failed. Dashboard may run in demo mode.")
        print("Check that your cloud API server is running and accessible.")
        
        # Ask if user wants to continue anyway
        response = input("\nContinue anyway? (y/n): ").lower().strip()
        if response != 'y':
            return 1
    
    print("\n✓ API connection successful!")
    print("\nStarting dashboard...")
    print("Dashboard will be available at: http://localhost:8051")
    print("Press Ctrl+C to stop")
    
    # Import and start the dashboard
    try:
        # Import the dashboard from the api directory
        api_dir = '/home/steve/GITHUB/cs330-projects/homework2/api'
        sys.path.insert(0, api_dir)
        from dashboard_client import app
        app.run_server(debug=True, host='127.0.0.1', port=8051)
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
    except Exception as e:
        print(f"\n✗ Error starting dashboard: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
#!/bin/bash
# DX Cluster Analytics Dashboard Startup Script
# This script starts the local dashboard connected to the cloud API

echo "=== Starting DX Cluster Analytics Dashboard ==="
echo "Connecting to cloud API: dx.jxqz.org:8080"
echo ""

# Navigate to the homework2 directory
cd /home/steve/GITHUB/cs330-projects/homework2

# Set the API endpoint to your cloud server
export API_BASE_URL=http://dx.jxqz.org:8080/api

# Start the dashboard
echo "Starting dashboard..."
echo "Dashboard will be available at: http://localhost:8051"
echo "Press Ctrl+C to stop the dashboard"
echo ""

/home/steve/GITHUB/cs330-projects/.venv/bin/python api/dashboard_client.py
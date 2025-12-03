#!/bin/bash
# Build script for DX Cluster Streamlit Dashboard

echo "Building DX Streamlit Dashboard container..."
docker build -f Dockerfile.streamlit -t dx-streamlit-dashboard:latest .

if [ $? -eq 0 ]; then
    echo "✓ Dashboard container built successfully!"
    echo ""
    echo "To run the dashboard:"
    echo "  docker run -d -p 8501:8501 -e API_URL=http://localhost:8080/api/spots?band=10m dx-streamlit-dashboard:latest"
else
    echo "✗ Build failed"
    exit 1
fi

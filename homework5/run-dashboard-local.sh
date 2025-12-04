#!/bin/bash
# Local development startup script for Streamlit Dashboard

# Change to the homework5 directory
cd "$(dirname "$0")"

echo "🚀 Starting DX Cluster Streamlit Dashboard (Local Development Mode)"
echo ""

# Activate virtual environment if it exists
if [ -d "$HOME/.venv" ]; then
    echo "📦 Activating virtual environment..."
    source "$HOME/.venv/bin/activate"
elif [ -d ".venv" ]; then
    echo "📦 Activating local virtual environment..."
    source ".venv/bin/activate"
fi

# Check if .env exists
if [ ! -f "streamlit/.env.local" ]; then
    echo "⚠️  Warning: streamlit/.env.local not found"
    echo "   Copy streamlit/.env.local to streamlit/.env and configure it"
    echo ""
fi

# Check if requirements are installed
echo "📦 Checking Python dependencies..."
pip list | grep -q streamlit
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r streamlit/requirements.txt
fi

echo ""
echo "📊 Dashboard will be available at: http://localhost:8501"
echo ""
echo "Configuration:"
echo "  - Database: ${PGHOST:-localhost}:${PGPORT:-5432}/${PGDATABASE:-dx_analysis}"
echo "  - API URL: ${API_BASE_URL:-http://api.jxqz.org:8080}"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Start Streamlit from the streamlit directory
cd streamlit

# Load environment variables if .env exists
if [ -f ".env.local" ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi

streamlit run main.py

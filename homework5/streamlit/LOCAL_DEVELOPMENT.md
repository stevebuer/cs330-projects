# Local Development Setup Guide

## Quick Start

### 1. Setup Environment Variables

Copy the template and configure your settings:

```bash
cd /home/steve/GITHUB/cs330-projects/homework5/streamlit
cp .env.local .env
```

Edit `.env` and set:
- **PGHOST**: Your local PostgreSQL host (default: localhost)
- **PGPORT**: PostgreSQL port (default: 5432)
- **PGDATABASE**: Database name (default: dx_analysis)
- **PGUSER**: Database user (default: dx_web_user)
- **PGPASSWORD**: Your database password
- **API_BASE_URL**: API endpoint (e.g., http://localhost:8080 or your remote API)

### 2. Setup Database

Ensure your local PostgreSQL database has the required table:

```bash
cd /home/steve/GITHUB/cs330-projects/homework5
psql -d dx_analysis -f db_migrations/002_dashboard_users.sql
```

### 3. Install Python Dependencies

```bash
cd /home/steve/GITHUB/cs330-projects/homework5/streamlit
pip install -r requirements.txt
```

### 4. Run the Dashboard

From the homework5 directory:

```bash
cd /home/steve/GITHUB/cs330-projects/homework5
./run-dashboard-local.sh
```

Or run directly from the streamlit directory:

```bash
cd /home/steve/GITHUB/cs330-projects/homework5/streamlit
source .env  # Load environment variables
streamlit run main.py
```

The dashboard will be available at: **http://localhost:8501**

---

## Architecture: Hybrid Approach

The dashboard uses a **hybrid architecture** for optimal flexibility:

### Local Database (User Configuration)
- Stores user profiles and preferences
- Connects directly to your local PostgreSQL instance
- Fast access for personalization features
- Module: `db_client.py`

### Remote API (Reports & Data)
- Fetches DX spot data and statistics
- Can connect to local API (http://localhost:8080) or remote production API
- Allows quick laptop development without full data stack
- Module: `api_client.py`

### Benefits
✅ Quick local development without copying production data  
✅ Direct database access for user settings (low latency)  
✅ API access for reports (production data or local testing)  
✅ Easy to switch between local and remote APIs

---

## File Structure

```
homework5/
├── streamlit/
│   ├── main.py                 # Main dashboard page
│   ├── api_client.py           # API client for reports (NEW)
│   ├── db_client.py            # Database client for user config (NEW)
│   ├── .env.local              # Environment template (NEW)
│   ├── .env                    # Your local config (create this)
│   ├── requirements.txt        # Python dependencies (updated)
│   └── pages/
│       ├── user_login.py       # User management (updated)
│       ├── band_analysis.py    # Band statistics
│       ├── propagation_trends.py
│       ├── raw_spots.py
│       └── top_stations.py
└── run-dashboard-local.sh      # Startup script (NEW)
```

---

## Development Workflow

### 1. Start Your API (Optional)
If testing with local API:
```bash
cd /home/steve/GITHUB/cs330-projects/homework5/api
# Configure .env with database settings
python dx_api.py
```

### 2. Start Dashboard
```bash
cd /home/steve/GITHUB/cs330-projects/homework5
./run-dashboard-local.sh
```

### 3. Development Tips

- **Hot reload**: Streamlit automatically reloads when you save files
- **Debug mode**: Check terminal for error messages
- **API testing**: Use curl or browser to test API endpoints
- **Database check**: Use psql to verify user data

---

## API Endpoints Used

The `api_client.py` module supports these endpoints:

- `GET /api/spots` - Fetch DX spots with filters
- `GET /api/stats/bands` - Band activity statistics
- `GET /api/stats/top-dx` - Most active DX stations
- `GET /api/stats/top-spotters` - Most active spotters
- `GET /api/stats/propagation` - Propagation summary
- `GET /api/health` - API health check

---

## Switching Between Local and Remote API

Edit `streamlit/.env`:

**Local API:**
```bash
API_BASE_URL=http://localhost:8080
```

**Remote API:**
```bash
API_BASE_URL=https://your-production-server.com
```

No code changes needed - just restart the dashboard!

---

## Troubleshooting

### Database Connection Failed
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env`
- Test connection: `psql -h localhost -U dx_web_user -d dx_analysis`

### API Connection Failed
- Check API is running (if using local)
- Verify API_BASE_URL in `.env`
- Test endpoint: `curl http://localhost:8080/api/health`

### Module Import Errors
- Ensure you're running from the `streamlit/` directory
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Stop existing Streamlit: `pkill -f streamlit`
- Or change port in `.env`: `STREAMLIT_SERVER_PORT=8502`

---

## Next Steps

1. **Test the setup**: Run `./run-dashboard-local.sh` and access http://localhost:8501
2. **Create a user**: Go to "User Login" page and register with your callsign
3. **Update pages**: Modify other dashboard pages to use `api_client` for data fetching
4. **Add features**: Implement custom reports using the API client
5. **Production build**: When ready, build container with `./build-dashboard.sh`

---

## Production Deployment

When ready to containerize:

```bash
# Build the container
./build-dashboard.sh

# Or use docker-compose
docker-compose up -d dx-dashboard
```

The same code works in both local development and production!

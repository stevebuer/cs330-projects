# DX Cluster JSON API

This directory contains a JSON REST API for querying DX cluster spot data, along with client applications that demonstrate its usage.

## Components

### 1. Core API Server (`dx_api.py`)
- **Purpose**: RESTful JSON API for DX cluster database
- **Framework**: Flask with CORS support
- **Database**: PostgreSQL with read-only access
- **Port**: 5000 (default)

### 2. Web Data Browser (`data_browser.html`)
- **Purpose**: Interactive web interface for browsing DX spots
- **Features**: Search, filter, pagination, real-time updates
- **Technology**: Bootstrap 5, vanilla JavaScript
- **API Client**: Consumes the JSON API

### 3. Dashboard Client (`dashboard_client.py`)
- **Purpose**: Modified Dash dashboard using API instead of direct DB
- **Framework**: Plotly Dash
- **Port**: 8051 (default)
- **Features**: Real-time charts, statistics, band activity

## API Endpoints

### Health & Info
- `GET /api/health` - API health check
- `GET /api` - API information and endpoint list

### Statistics
- `GET /api/stats` - Basic database statistics
- `GET /api/activity/hourly?hours=24` - Hourly activity data
- `GET /api/bands` - Band activity statistics

### Spot Data
- `GET /api/spots` - Search/filter spots with pagination
- `GET /api/spots/recent?hours=1` - Recent spots
- `GET /api/callsigns/top` - Top active callsigns

### Analysis
- `GET /api/frequency/histogram?bins=50` - Frequency distribution

## Setup Instructions

### 1. Install Dependencies
```bash
cd /home/steve/GITHUB/cs330-projects/homework2/api
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.template .env
# Edit .env with your database credentials
```

### 3. Database Setup
Ensure you have a read-only database user for the API:
```sql
-- Create read-only user for API
CREATE USER dx_reader WITH PASSWORD 'your_readonly_password';
GRANT CONNECT ON DATABASE dxcluster TO dx_reader;
GRANT USAGE ON SCHEMA public TO dx_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dx_reader;
```

### 4. Start the API Server
```bash
python dx_api.py
```

### 5. Access the Applications

#### Web Data Browser
Open `data_browser.html` in your web browser, or serve it via a web server:
```bash
python -m http.server 8080
# Then visit: http://localhost:8080/data_browser.html
```

#### Dashboard Client
```bash
python dashboard_client.py
# Visit: http://localhost:8051
```

## API Usage Examples

### Get Recent Spots
```bash
curl "http://localhost:5000/api/spots/recent?hours=1&limit=10"
```

### Search for Specific DX Station
```bash
curl "http://localhost:5000/api/spots?dx_call=JA1ABC&limit=50"
```

### Get 20m Band Activity
```bash
curl "http://localhost:5000/api/spots?band=20m&since=2025-10-15T00:00:00Z"
```

### Filter by Frequency Range
```bash
curl "http://localhost:5000/api/spots?frequency_min=14000&frequency_max=14350"
```

## Query Parameters

### Common Parameters
- `limit` - Maximum results (default: 100, max: 1000)
- `offset` - Pagination offset (default: 0)
- `since` - ISO datetime string for minimum timestamp
- `until` - ISO datetime string for maximum timestamp

### Spot Filtering
- `dx_call` - DX station callsign (partial match)
- `spotter_call` - Spotter callsign (partial match)
- `frequency_min` - Minimum frequency in kHz
- `frequency_max` - Maximum frequency in kHz
- `band` - Amateur radio band (e.g., "20m", "40m")
- `mode` - Operating mode (partial match)
- `grid_square` - Grid square (partial match)
- `comment_contains` - Text search in comments

## Architecture Benefits

### Separation of Concerns
- **API Layer**: Handles data access, validation, security
- **Client Applications**: Focus on presentation and user experience
- **Database**: Protected from direct client access

### Security
- Read-only database access
- Input validation and sanitization
- Rate limiting potential (can be added)
- SQL injection prevention via parameterized queries

### Scalability
- Multiple clients can share the same API
- API can be cached, load-balanced, or replicated
- Database queries optimized in one place

### Flexibility
- Easy to add new client applications
- API versioning support
- Different front-ends (web, mobile, desktop) can use same backend

## Development Notes

### Adding New Endpoints
1. Add new route function in `dx_api.py`
2. Include proper error handling and parameter validation
3. Add endpoint documentation to this README
4. Test with curl or update test clients

### Performance Considerations
- API implements pagination to prevent large result sets
- Database queries use appropriate indexes
- JSON responses are streamlined
- Consider adding Redis caching for frequently accessed data

### Error Handling
- Consistent JSON error responses
- HTTP status codes follow REST conventions
- Database connection failures handled gracefully
- Input validation with descriptive error messages

## Production Deployment

### Security Checklist
- [ ] Use environment variables for all secrets
- [ ] Configure firewall to restrict API access
- [ ] Enable HTTPS (add reverse proxy like nginx)
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Regular security updates

### Monitoring
- API health endpoint for monitoring systems
- Log API requests and errors
- Monitor database connection pool
- Track response times and error rates

### Apache/WSGI Deployment
The API can be deployed using mod_wsgi similar to your existing web applications:

```python
# wsgi.py
import sys
import os
sys.path.insert(0, '/path/to/api/directory')
from dx_api import app as application
```

This JSON API provides a clean, flexible foundation for all your DX cluster applications while maintaining security and performance.
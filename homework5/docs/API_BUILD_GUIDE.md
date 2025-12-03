# DX Cluster API - Build & Deployment Guide

This document explains how to build and deploy the DX Cluster API container to GitHub Container Registry (ghcr.io).

## Overview

The API container serves:
- REST API for DX cluster spot data on port 8080
- Interactive API documentation at `/docs`
- Data browser interface at `/`

## Files

- **Dockerfile.api** - Docker container definition
- **build-api-image.sh** - Build and push script for ghcr.io
- **docker-compose.yml** - Container orchestration
- **api/dx_api.py** - Flask API application
- **api/docs/** - Documentation files
  - `index.html` - Documentation home page
  - `API_DOCUMENTATION.md` - Complete API reference
  - `API_QUICKSTART.md` - Quick start guide
  - `openapi.yaml` - OpenAPI specification

## Building the Container

### Prerequisites

- Docker installed
- GitHub Container Registry (ghcr.io) access
- Docker login credentials: `docker login ghcr.io`

### Build Script Usage

```bash
# Build and push with default 'latest' tag
./build-api-image.sh

# Build and push with specific version tag
./build-api-image.sh v1.0.0

# Build and push with custom tag
./build-api-image.sh 2025-11-22
```

The script will:
1. Build the Docker image
2. Push to `ghcr.io/stevebuer/cs330-projects/dx-cluster-api:TAG`
3. Also push/update the `latest` tag

### Manual Build (Alternative)

```bash
# Build locally
docker build -f Dockerfile.api -t ghcr.io/stevebuer/cs330-projects/dx-cluster-api:latest .

# Push to registry
docker push ghcr.io/stevebuer/cs330-projects/dx-cluster-api:latest
```

## Running the Container

### With Docker Compose

```bash
# Set environment variables
export PGHOST=your-db-host
export PGDATABASE=dxcluster
export PGUSER=dx_reader
export PGPASSWORD=your-password
export PGPORT=5432

# Start container
docker-compose up -d dx-api

# View logs
docker-compose logs -f dx-api
```

### Direct Docker Run

```bash
docker run -d \
  --name dx-cluster-api \
  -p 8080:8080 \
  -e PGHOST=your-db-host \
  -e PGDATABASE=dxcluster \
  -e PGUSER=dx_reader \
  -e PGPASSWORD=your-password \
  -e PGPORT=5432 \
  -e FLASK_ENV=production \
  ghcr.io/stevebuer/cs330-projects/dx-cluster-api:latest
```

## Accessing the API

### Health Check
```bash
curl http://localhost:8080/api/health
```

### Documentation
- **Home**: http://localhost:8080/docs
- **Quick Start**: http://localhost:8080/docs/quickstart
- **Full Documentation**: http://localhost:8080/docs/api
- **OpenAPI YAML**: http://localhost:8080/docs/openapi
- **OpenAPI JSON**: http://localhost:8080/docs/openapi.json

### API Endpoints
- **Root**: http://localhost:8080/api
- **Recent Spots**: http://localhost:8080/api/spots/recent
- **Spots**: http://localhost:8080/api/spots
- **Bands**: http://localhost:8080/api/bands
- **Stats**: http://localhost:8080/api/stats
- **Top Callsigns**: http://localhost:8080/api/callsigns/top

## Production Deployment

### On Remote Server (Vultr)

1. **Pull the latest image**:
   ```bash
   docker pull ghcr.io/stevebuer/cs330-projects/dx-cluster-api:latest
   ```

2. **Stop old container** (if running):
   ```bash
   docker stop dx-cluster-api
   docker rm dx-cluster-api
   ```

3. **Start new container**:
   ```bash
   docker-compose up -d dx-api
   ```

4. **Verify health**:
   ```bash
   curl http://localhost:8080/api/health
   ```

### Environment Configuration

Create `.env` file in homework5 directory:

```env
PGHOST=your-db-hostname
PGPORT=5432
PGDATABASE=dxcluster
PGUSER=dx_reader
PGPASSWORD=your-secure-password
FLASK_ENV=production
```

## Disk Space Management

If running low on disk space on the Vultr server:

```bash
# Remove old images
docker image prune -a

# Remove stopped containers
docker container prune

# Remove unused volumes
docker volume prune

# Remove all unused resources
docker system prune -a
```

## Monitoring

### Container Status
```bash
docker-compose ps

docker stats dx-cluster-api
```

### Logs
```bash
docker-compose logs -f dx-api

# Last 100 lines
docker-compose logs --tail 100 dx-api
```

### Health Check
```bash
curl -v http://localhost:8080/api/health

# With jq for pretty output
curl http://localhost:8080/api/health | jq '.'
```

## Troubleshooting

### Container won't start
1. Check environment variables: `docker-compose config`
2. Check logs: `docker-compose logs dx-api`
3. Verify PostgreSQL is running and accessible

### Database connection failed
```bash
# Test database connection
docker-compose up postgres-check

# Or manually
psql -h $PGHOST -U $PGUSER -d $PGDATABASE -c "SELECT 1"
```

### Port already in use
```bash
# Find what's using port 8080
lsof -i :8080

# Change port in docker-compose.yml
# ports:
#   - "8081:8080"
```

## Performance Tuning

The API uses Gunicorn with these defaults:
- 2 worker processes
- 120 second timeout

To adjust in Dockerfile.api:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "api.dx_api:app"]
```

## Next Steps

- Deploy to production Vultr instances
- Set up Prometheus metrics collection
- Configure Grafana dashboards
- Implement rate limiting if needed
- Add authentication for write operations (future)

## References

- OpenAPI Specification: `/api/docs/openapi`
- Quick Start Guide: `/api/docs/quickstart`
- Full Documentation: `/api/docs/api`
- GitHub Container Registry: https://github.com/features/packages

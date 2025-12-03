# Quick Deployment Guide for Vultr VMs

This guide explains how to deploy the API container on your Debian Bookworm Vultr VMs using docker-compose v1.29.2.

## Prerequisites

- Docker installed
- docker-compose v1.29.2
- Access to GitHub Container Registry (ghcr.io)
- PostgreSQL database running and accessible

## Setup Steps

### 1. Create deployment directory

```bash
mkdir -p /opt/dx-cluster
cd /opt/dx-cluster
```

### 2. Create `.env` file with your database credentials

```bash
cp .env.example .env
nano .env  # Edit with your actual credentials
```

Update the `.env` file with your database credentials:

```bash
PGHOST=localhost
PGPORT=5432
PGDATABASE=dx_analysis
PGUSER=dx_web_user
PGPASSWORD=your-secure-password
FLASK_ENV=production
```

**IMPORTANT**: 
- The `.env` file is protected by `.gitignore` and will NOT be committed
- Use `localhost` if PostgreSQL is on the same machine (uses host networking)
- For remote databases, use the hostname or IP address
- Protect this file - it contains your database password

### 3. Download docker-compose file

```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/stevebuer/cs330-projects/main/homework5/docker-compose.yml
```

Or copy manually to `/opt/dx-cluster/docker-compose.yml`

### 4. Pull the latest image

```bash
docker pull ghcr.io/stevebuer/cs330-projects/dx-cluster-api:latest
```

### 5. Start the container

```bash
docker-compose up -d
```

### 6. Verify it's running

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f dx-api

# Test API health
curl http://localhost:8080/api/health
```

## Access the API

- **API Base**: `http://your-server-ip:8080/api`
- **Documentation**: `http://your-server-ip:8080/docs`
- **Quick Start**: `http://your-server-ip:8080/docs/quickstart`
- **Full Docs**: `http://your-server-ip:8080/docs/api`
- **Health Check**: `http://your-server-ip:8080/api/health`

## Common Commands

### View logs
```bash
docker-compose logs -f dx-api
docker-compose logs --tail 50 dx-api
```

### Stop container
```bash
docker-compose stop
```

### Start container
```bash
docker-compose start
```

### Restart container
```bash
docker-compose restart dx-api
```

### Remove container
```bash
docker-compose down
```

### Update to new image
```bash
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Container won't start

1. Check the logs:
   ```bash
   docker-compose logs dx-api
   ```

2. **Database connection error**: Make sure `PGHOST` in `.env` is the actual hostname or IP of your database server, NOT `localhost`. Inside containers, `localhost` refers to the container itself.
   ```bash
   # Example for database on another server
   PGHOST=144.202.1.188  # Use IP or hostname, not localhost
   ```

3. Verify database connection:
   ```bash
   docker run --rm -it postgres:15-alpine \
     psql -h your-database-host -U dx_reader -d dxcluster -c "SELECT 1"
   ```

4. Verify environment variables:
   ```bash
   docker-compose config | grep -A5 environment
   ```

### Port already in use

If port 8080 is in use, edit `docker-compose.yml`:

```yaml
ports:
  - "8081:8080"  # Use 8081 instead
```

Then restart:
```bash
docker-compose up -d
```

### Disk space issues

```bash
# Remove unused images
docker image prune -a

# Remove stopped containers
docker container prune

# Check disk usage
docker system df
```

## Files Reference

- **docker-compose.yml** - Simple, compatible config (recommended)
- **docker-compose.simple.yml** - Minimal alternative
- **.env** - Your environment variables (DO NOT commit to git!)

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| PGHOST | Yes | - | Database hostname |
| PGPORT | No | 5432 | Database port |
| PGDATABASE | Yes | - | Database name |
| PGUSER | Yes | - | Database user |
| PGPASSWORD | Yes | - | Database password |
| FLASK_ENV | No | production | Set to 'development' for debug mode |

## Example: Multiple VMs

If running on 2 Vultr VMs:

**VM1 (API)**: Run docker-compose as described above

**VM2 (Prometheus/Grafana)**: Monitor the API on VM1
```bash
# Scrape from VM1
targets:
  - 'vm1-ip:8080'
```

## Next Steps

1. Test API endpoints
2. Set up monitoring/alerts in Prometheus
3. Configure Grafana dashboards
4. Set up SSL/TLS if needed (nginx reverse proxy)

## Support

Check the documentation:
- Quick Start: `http://your-server:8080/docs/quickstart`
- Full API Docs: `http://your-server:8080/docs/api`
- OpenAPI Spec: `http://your-server:8080/docs/openapi`

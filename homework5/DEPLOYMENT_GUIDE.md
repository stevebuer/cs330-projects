# DX Streamlit Dashboard - Production Deployment Guide

## Container Built and Published Successfully ✓

Your Streamlit dashboard container has been built and published to GitHub Container Registry.

**Container:** `ghcr.io/stevebuer/cs330-projects/dx-streamlit-dashboard:latest`
**Local tag:** `dx-streamlit-dashboard:latest`

## Deployment Steps

### Option 1: Deploy with Docker Compose (Recommended)

This approach deploys both the API and dashboard together using docker-compose. The images are pulled from ghcr.io.

1. **Copy files to production server:**
```bash
# From your local machine, sync the homework5 directory to production
rsync -avz --exclude='*.pyc' --exclude='__pycache__' \
  /home/steve/GITHUB/cs330-projects/homework5/ \
  user@jersey.jxzq.org:/path/to/homework5/
```

2. **On production server, log in to GitHub Container Registry:**
```bash
# Create a GitHub personal access token with read:packages scope
# Then login to ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u stevebuer --password-stdin
```

3. **Configure environment:**
```bash
cd /path/to/homework5
cp .env.example .env
nano .env  # Edit with production database credentials
```

4. **Deploy the stack:**
```bash
# Pull and start both containers
docker-compose pull
docker-compose up -d

# Check logs
docker-compose logs -f dx-dashboard
```

4. **Verify deployment:**
```bash
curl http://localhost:8501/_stcore/health
```

### Option 2: Direct Docker Run

Run the dashboard container directly without docker-compose:

1. **On production server, log in to ghcr.io:**
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u stevebuer --password-stdin
```

2. **Pull and run the container:**
```bash
docker pull ghcr.io/stevebuer/cs330-projects/dx-streamlit-dashboard:latest

docker run -d \
  --name dx-streamlit-dashboard \
  --restart unless-stopped \
  -p 8501:8501 \
  -e PGHOST=localhost \
  -e PGPORT=5432 \
  -e PGDATABASE=dx_analysis \
  -e PGUSER=dx_web_user \
  -e PGPASSWORD=your-password \
  ghcr.io/stevebuer/cs330-projects/dx-streamlit-dashboard:latest
```

### Option 3: Build on Production Server

1. **Copy source files to production:**
```bash
rsync -avz /home/steve/GITHUB/cs330-projects/homework5/ \
  user@jersey.jxzq.org:/path/to/homework5/
```

2. **Build on production server:**
```bash
ssh user@jersey.jxzq.org
cd /path/to/homework5
bash build-dashboard.sh
```

3. **Deploy with docker-compose:**
```bash
docker-compose up -d dx-dashboard
```

## Configuration

### Environment Variables

The dashboard requires these PostgreSQL connection variables:

- `PGHOST` - Database host (e.g., localhost or jersey.jxzq.org)
- `PGPORT` - Database port (default: 5432)
- `PGDATABASE` - Database name (e.g., dx_analysis)
- `PGUSER` - Database user (e.g., dx_web_user)
- `PGPASSWORD` - Database password

### Port Configuration

- Dashboard runs on port **8501**
- API runs on port **8080** (if using docker-compose)
- Ensure firewall allows traffic on port 8501

## Accessing the Dashboard

Once deployed, access the dashboard at:
- Local: http://localhost:8501
- Production: http://dx.jxqz.org:8501

## Monitoring

### Check container status:
```bash
docker ps | grep dx-streamlit-dashboard
```

### View logs:
```bash
docker logs -f dx-streamlit-dashboard
```

### Health check:
```bash
curl http://localhost:8501/_stcore/health
```

## Troubleshooting

### Container won't start:
```bash
# Check logs
docker logs dx-streamlit-dashboard

# Common issues:
# - Database connection failure (check PGHOST, credentials)
# - Port 8501 already in use
# - Missing environment variables
```

### Database connection issues:
```bash
# Test database connectivity from container
docker exec -it dx-streamlit-dashboard bash
pip install psycopg2-binary
python -c "import psycopg2; conn = psycopg2.connect('host=localhost dbname=dx_analysis user=dx_web_user password=yourpass')"
```

### Restart the dashboard:
```bash
docker restart dx-streamlit-dashboard
```

## Updating the Dashboard

To deploy updates:

1. **Rebuild the container:**
```bash
cd /home/steve/GITHUB/cs330-projects/homework5
bash build-dashboard.sh
```

2. **Stop old container:**
```bash
docker stop dx-streamlit-dashboard
docker rm dx-streamlit-dashboard
```

3. **Start new container:**
```bash
docker-compose up -d dx-dashboard
# or use docker run with updated image
```

## Production Checklist

- [ ] Container built successfully (✓ Done)
- [ ] .env file configured with production credentials
- [ ] Port 8501 open in firewall
- [ ] Database accessible from production server
- [ ] SSL/TLS certificate configured (if needed)
- [ ] Grafana monitoring configured for dashboard
- [ ] Backup strategy in place
- [ ] Container auto-restart configured

## Next Steps

1. Choose your deployment method (docker-compose recommended)
2. Transfer files/image to production
3. Configure environment variables
4. Start the container
5. Verify dashboard is accessible
6. Set up monitoring alerts

## Support

For issues, check:
- Container logs: `docker logs dx-streamlit-dashboard`
- Database connectivity
- Firewall rules
- Environment variables

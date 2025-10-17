# Production Deployment Guide

## Quick Start for Pre-built Container Deployment

### The Problem
Your production server (Debian bullseye) has an older Docker Compose version that doesn't support the `version: '3.8'` syntax in your docker-compose.yml file.

### The Solution
Use pre-built container images instead of building on the production server.

## Step-by-Step Deployment

### 1. On Your Development Machine

Export your tested containers:
```bash
cd /home/steve/GITHUB/cs330-projects/homework2

# If your images have different names (e.g., homework2_dx-api), tag them first:
# docker tag homework2_dx-api:latest dx-cluster-api:latest
# docker tag homework2_dx-web:latest dx-cluster-web:latest

./deploy-production.sh export
```

This creates:
- `exports/dx-cluster-api-latest.tar.gz`
- `exports/dx-cluster-web-latest.tar.gz`

### 2. Transfer to Production Server

Copy the entire homework2 directory (or at minimum these files) to your production server:
- `exports/` directory (with the .tar.gz files)
- `docker-compose.production.yml`
- `deploy-production.sh`
- `.env.docker.production` (rename to `.env`)

```bash
# Example transfer command
scp -r homework2/ user@production-server:/path/to/deployment/
```

### 3. On Production Server

```bash
cd /path/to/deployment/homework2

# Copy environment template
cp .env.docker.production .env

# Edit with your production database credentials
nano .env

# Run full deployment
./deploy-production.sh full-deploy
```

## Alternative: Manual Deployment

If the script doesn't work, you can deploy manually:

### Import Images
```bash
docker load < exports/dx-cluster-api-latest.tar.gz
docker load < exports/dx-cluster-web-latest.tar.gz
```

### Configure Environment
```bash
cp .env.docker.production .env
# Edit .env with your database settings
```

### Deploy
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Check Status
```bash
docker-compose -f docker-compose.production.yml ps
```

## Key Differences from Development

1. **No Version Field**: The production compose file removes the deprecated `version` field
2. **Pre-built Images**: Uses `image:` instead of `build:` directives
3. **Compatibility**: Works with older Docker Compose versions

## Environment Variables

Configure these in your `.env` file:
```env
PGHOST=your_database_host
PGDATABASE=dxcluster
PGUSER=dx_reader
PGPASSWORD=your_secure_password
PGPORT=5432
FLASK_ENV=production
```

## Service Access

After deployment, your services will be available at:
- **API**: http://your-server:8080
- **Dashboard**: http://your-server:8050
- **Health Check**: http://your-server:8080/api/health

## Troubleshooting

### Check Logs
```bash
./deploy-production.sh logs
# or for specific service:
./deploy-production.sh logs dx-api
```

### Health Check
```bash
./deploy-production.sh health
```

### Stop Services
```bash
./deploy-production.sh stop
```

## Security Notes

1. Change default passwords in `.env`
2. Use secure database credentials
3. Consider running behind a reverse proxy (nginx/apache)
4. Enable SSL/TLS for production access
5. Restrict network access to necessary ports only

## Container Registry Alternative

For future deployments, consider pushing to a container registry:

```bash
# Tag and push to registry
docker tag dx-cluster-api:latest your-registry.com/dx-cluster-api:latest
docker push your-registry.com/dx-cluster-api:latest

# Update docker-compose.production.yml to use registry images
# image: your-registry.com/dx-cluster-api:latest
```
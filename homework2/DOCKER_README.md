# Docker Deployment Guide for DX Cluster Services

This guide covers deploying the DX Cluster API and Web Dashboard using Docker containers.

## 🐳 Architecture

The Docker setup provides:
- **dx-api**: Flask REST API server (port 8080)
- **dx-web**: Dash web dashboard (port 8050)
- **postgres-check**: Database connectivity verification
- **traefik**: Optional reverse proxy with load balancing

## 📋 Prerequisites

- Docker Engine 20.x+
- Docker Compose 2.x+
- PostgreSQL database (running separately)
- Environment configuration

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy the environment template
cp .env.docker .env

# Edit the configuration
nano .env
```

Configure your database connection:
```env
PGHOST=your_postgres_host
PGDATABASE=dxcluster
PGUSER=dx_reader
PGPASSWORD=your_password
PGPORT=5432
```

### 2. Build and Start Services

```bash
# Make management script executable
chmod +x docker-manage.sh

# Build images
./docker-manage.sh build

# Start services
./docker-manage.sh start
```

### 3. Access Services

- **API**: http://localhost:8080
- **Dashboard**: http://localhost:8050
- **API Health Check**: http://localhost:8080/api/health

## 🛠 Management Commands

The `docker-manage.sh` script provides easy service management:

```bash
# Build Docker images
./docker-manage.sh build

# Start all services
./docker-manage.sh start

# Start with Traefik proxy
./docker-manage.sh start-proxy

# Stop services
./docker-manage.sh stop

# Restart services
./docker-manage.sh restart

# View logs (all services)
./docker-manage.sh logs

# View logs (specific service)
./docker-manage.sh logs dx-api

# Check service status
./docker-manage.sh status

# Development mode (live reload)
./docker-manage.sh dev

# Clean up resources
./docker-manage.sh clean

# Open database shell
./docker-manage.sh db-shell
```

## 🔧 Development Mode

For development with live code changes:

```bash
# Start in development mode
./docker-manage.sh dev

# Services will rebuild and restart when code changes
```

## 🌐 Production Deployment

### With Reverse Proxy

```bash
# Start with Traefik proxy
./docker-manage.sh start-proxy

# Add to /etc/hosts:
# 127.0.0.1 api.dx.local dashboard.dx.local

# Access services:
# API: http://api.dx.local
# Dashboard: http://dashboard.dx.local  
# Traefik UI: http://localhost:8888
```

### Custom Domains

Edit `docker-compose.yml` to change the Traefik rules:

```yaml
labels:
  - "traefik.http.routers.dx-api.rule=Host(`api.yourdomain.com`)"
  - "traefik.http.routers.dx-web.rule=Host(`dashboard.yourdomain.com`)"
```

## 🔒 Security Considerations

### Environment Variables
- Use strong passwords for database connections
- Set `SECRET_KEY` for Flask sessions
- Enable rate limiting in production

### Network Security
```yaml
networks:
  dx-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Container Security
- Services run as non-root users
- Minimal base images (Python slim)
- Health checks for monitoring

## 📊 Monitoring

### Health Checks
Both containers include health checks:
```bash
# Check container health
docker ps

# View health check logs
docker inspect dx-cluster-api | grep Health -A 10
```

### Resource Monitoring
```bash
# Real-time resource usage
./docker-manage.sh status

# Detailed container stats
docker stats
```

### Log Management
```bash
# View logs with timestamps
docker-compose logs -f -t

# View specific service logs
docker-compose logs -f dx-api

# Save logs to file
docker-compose logs dx-api > api.log
```

## 🚨 Troubleshooting

### Database Connection Issues
```bash
# Test database connectivity
./docker-manage.sh db-shell

# Check postgres-check service logs
docker-compose logs postgres-check

# Verify network connectivity
docker exec dx-cluster-api ping your_postgres_host
```

### Port Conflicts
If ports 8080 or 8050 are in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # API on different port
  - "8051:8050"  # Dashboard on different port
```

### Container Startup Issues
```bash
# View build logs
docker-compose build --no-cache --progress=plain

# Check service logs
./docker-manage.sh logs

# Debug container interactively
docker run --rm -it dx-cluster-api /bin/bash
```

## 🔄 Updates and Maintenance

### Updating Services
```bash
# Pull latest code changes
git pull

# Rebuild and restart
./docker-manage.sh stop
./docker-manage.sh build
./docker-manage.sh start
```

### Backup and Restore
```bash
# Export container images
docker save dx-cluster-api:latest | gzip > dx-api-backup.tar.gz
docker save dx-cluster-web:latest | gzip > dx-web-backup.tar.gz

# Import container images
docker load < dx-api-backup.tar.gz
docker load < dx-web-backup.tar.gz
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# In docker-compose.yml
dx-api:
  deploy:
    replicas: 3
  ports:
    - "8080-8082:8080"
```

### Load Balancing
The Traefik proxy automatically load balances across replicas.

## 🔗 Integration

### CI/CD Pipeline Example
```bash
#!/bin/bash
# deploy.sh
git pull
./docker-manage.sh stop
./docker-manage.sh build
./docker-manage.sh start
./docker-manage.sh status
```

### Systemd Integration
Create `/etc/systemd/system/dx-cluster-docker.service`:
```ini
[Unit]
Description=DX Cluster Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/homework2
ExecStart=/path/to/homework2/docker-manage.sh start
ExecStop=/path/to/homework2/docker-manage.sh stop

[Install]
WantedBy=multi-user.target
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Dash Deployment](https://dash.plotly.com/deployment)
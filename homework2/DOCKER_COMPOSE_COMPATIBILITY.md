# Docker Compose Compatibility Fix

## Problem
Very old Docker Compose versions (< 1.27) don't support:
- Advanced network configurations
- Volume definitions in newer format
- Service profiles (like Traefik)
- Some environment variable syntax

## Solution
Created two compose files:

### 1. `docker-compose.production.yml` (Full Featured)
- For Docker Compose 1.27+
- Includes networks, volumes, Traefik, labels
- Auto-detected for newer versions

### 2. `docker-compose.production.simple.yml` (Maximum Compatibility)  
- For very old Docker Compose versions
- Simplified configuration
- Only essential services (API, Web, postgres-check)
- No advanced networking or volumes
- Uses version '2' format

## Auto-Detection
The deployment script automatically detects your Docker Compose version and uses the appropriate file.

## Manual Override
If auto-detection fails, force the simple version:
```bash
./deploy-production.sh use-simple
```

Then run your commands normally:
```bash
./deploy-production.sh start-api
```

## Compatibility Matrix
- **Docker Compose < 1.27**: Uses simple configuration
- **Docker Compose 1.27+**: Uses full configuration
- **Docker Compose 2.x**: Uses full configuration

## What's Removed in Simple Version
- Custom networks (uses default bridge)
- Named volumes 
- Traefik reverse proxy
- Service labels
- Profiles
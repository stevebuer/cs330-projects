# CI/CD & Deployment Integration

Guide for integrating the CI/CD pipeline with your Terraform and Ansible infrastructure.

## Overview

Once you build Docker images via GitHub Actions, you'll want to deploy them to your infrastructure. This guide connects:

1. **GitHub Actions** (builds images)
2. **GitHub Packages/Docker Hub** (stores images)
3. **Ansible** (deploys to infrastructure)
4. **Terraform** (manages infrastructure)

## Phase 1: Build Images (CI/CD)

### Current Setup

Your CI/CD pipeline:
- Builds on manual trigger or release
- Pushes to GHCR or Docker Hub
- Tags images consistently

### Image Reference Format

After a build, your images are available at:

**From Release (automatic):**
```
ghcr.io/stevebuer/dxcluster-api:v1.0.0
ghcr.io/stevebuer/dxcluster-web:v1.0.0
```

**From Manual Build:**
```
ghcr.io/stevebuer/dxcluster-api:latest
ghcr.io/stevebuer/dxcluster-web:latest
```

## Phase 2: Deploy to Infrastructure (Ansible)

### Update Ansible Variables

Update your Ansible group vars to reference built images:

**File:** `homework4/ansible/group_vars/all.yml`

```yaml
# Docker image references (from CI/CD pipeline)
dxcluster_api_image: "ghcr.io/stevebuer/dxcluster-api"
dxcluster_api_tag: "v1.0.0"

dxcluster_web_image: "ghcr.io/stevebuer/dxcluster-web"
dxcluster_web_tag: "v1.0.0"

# Combined image URIs
docker_images:
  api: "{{ dxcluster_api_image }}:{{ dxcluster_api_tag }}"
  web: "{{ dxcluster_web_image }}:{{ dxcluster_web_tag }}"
```

### Update Docker Compose Template

Modify your Ansible docker role to use built images:

**File:** `homework4/ansible/roles/dxcluster_docker/templates/docker-compose.yml.j2`

```yaml
version: '3.8'

services:
  dx-api:
    image: "{{ docker_images.api }}"
    container_name: dx-cluster-api
    ports:
      - "8080:8080"
    environment:
      - PGHOST=${PGHOST}
      - PGDATABASE=${PGDATABASE}
      - PGUSER=${PGUSER}
      - PGPASSWORD=${PGPASSWORD}
      - PGPORT=${PGPORT}
      - FLASK_ENV=production
    env_file:
      - .env
    restart: unless-stopped
    networks:
      - dx-network
    depends_on:
      - postgres-check

  dx-web:
    image: "{{ docker_images.web }}"
    container_name: dx-cluster-web
    ports:
      - "8050:8050"
    environment:
      - PGHOST=${PGHOST}
      - PGDATABASE=${PGDATABASE}
      - PGUSER=${PGUSER}
      - PGPASSWORD=${PGPASSWORD}
      - PGPORT=${PGPORT}
      - DASH_ENV=production
    env_file:
      - .env
    restart: unless-stopped
    networks:
      - dx-network
    depends_on:
      - postgres-check

  postgres-check:
    image: postgres:15-alpine
    container_name: dx-postgres-check
    environment:
      - PGHOST=${PGHOST}
      - PGDATABASE=${PGDATABASE}
      - PGUSER=${PGUSER}
      - PGPASSWORD=${PGPASSWORD}
      - PGPORT=${PGPORT}
    command: >
      sh -c "
        until pg_isready -h $${PGHOST} -p $${PGPORT} -U $${PGUSER}; do
          echo 'Waiting for PostgreSQL...'
          sleep 2
        done
        echo 'PostgreSQL is ready!'
      "
    networks:
      - dx-network

networks:
  dx-network:
    driver: bridge

volumes:
  dx-data:
    driver: local
```

### Handle Registry Authentication

For GHCR, create an Ansible task to login:

**File:** `homework4/ansible/roles/dxcluster_docker/tasks/main.yml`

```yaml
---
- name: Log in to GitHub Container Registry
  docker_login:
    registry_url: ghcr.io
    username: "{{ ghcr_username }}"
    password: "{{ ghcr_password }}"
    reauthorize: yes
  when: use_ghcr | default(false)
  no_log: true

- name: Create docker-compose.yml from template
  template:
    src: docker-compose.yml.j2
    dest: "{{ deployment_home }}/docker-compose.yml"
    owner: "{{ deployment_user }}"
    group: "{{ deployment_user }}"
    mode: '0644'

- name: Pull and deploy containers
  docker_compose:
    project_src: "{{ deployment_home }}"
    state: present
    pull: yes
    build: no
  environment:
    PGHOST: "{{ db_host }}"
    PGDATABASE: "{{ db_database }}"
    PGUSER: "{{ db_user }}"
    PGPASSWORD: "{{ db_password }}"
    PGPORT: "{{ db_port }}"
```

## Complete Deployment Workflow

### Step 1: Build Release Images

```bash
# Create and push release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create GitHub release (triggers automatic build)
gh release create v1.0.0 --title "DX Cluster v1.0.0" --generate-notes

# Wait for build to complete (~5-10 minutes)
# Check: https://github.com/stevebuer/cs330-projects/actions
```

### Step 2: Update Deployment Configuration

```bash
# Update Ansible variables with new image tag
cd homework4/ansible

# Edit group_vars/all.yml
nano group_vars/all.yml

# Update:
# dxcluster_api_tag: "v1.0.0"
# dxcluster_web_tag: "v1.0.0"
```

### Step 3: Deploy to Infrastructure

```bash
# Deploy to staging first
./deploy.sh docker staging-server

# Verify everything works
./deploy.sh status staging-server

# Deploy to production
./deploy.sh docker prod-server

# Verify production
./deploy.sh status prod-server
```

## Automated Release Deployment Script

Create a helper script to automate the full workflow:

**File:** `homework4/ci-cd/deploy-release.sh`

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 v1.0.0"
    exit 1
fi

VERSION=$1
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo -e "${YELLOW}📦 DX Cluster Release Deployment${NC}"
echo "=================================="
echo "Version: $VERSION"
echo "Repo: $REPO_ROOT"
echo ""

# Step 1: Create git tag
echo -e "${YELLOW}1️⃣  Creating git tag...${NC}"
git tag -a "$VERSION" -m "Release version $VERSION" || {
    echo -e "${RED}Error: Tag already exists${NC}"
    exit 1
}

# Step 2: Push tag to GitHub
echo -e "${YELLOW}2️⃣  Pushing to GitHub...${NC}"
git push origin "$VERSION"

# Step 3: Create GitHub release
echo -e "${YELLOW}3️⃣  Creating GitHub release...${NC}"
gh release create "$VERSION" \
    --title "DX Cluster $VERSION" \
    --generate-notes \
    || echo "Release creation skipped (may already exist)"

# Step 4: Wait for build
echo -e "${YELLOW}4️⃣  Waiting for GitHub Actions build...${NC}"
echo "Monitor progress at: https://github.com/stevebuer/cs330-projects/actions"
echo "Press Enter when build completes..."
read

# Step 5: Update Ansible variables
echo -e "${YELLOW}5️⃣  Updating Ansible variables...${NC}"
cd "$REPO_ROOT/homework4/ansible"

# Update group_vars/all.yml
sed -i "s/dxcluster_api_tag: .*/dxcluster_api_tag: \"$VERSION\"/" group_vars/all.yml
sed -i "s/dxcluster_web_tag: .*/dxcluster_web_tag: \"$VERSION\"/" group_vars/all.yml

echo "Updated group_vars/all.yml"

# Step 6: Deploy to staging
echo -e "${YELLOW}6️⃣  Deploying to staging...${NC}"
./deploy.sh docker staging-server || {
    echo -e "${RED}Staging deployment failed. Fix and retry.${NC}"
    exit 1
}

echo -e "${GREEN}✓ Staging deployment successful${NC}"

# Step 7: Confirm production deployment
echo ""
echo -e "${YELLOW}7️⃣  Ready to deploy to production${NC}"
read -p "Deploy to production? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipped production deployment"
    exit 0
fi

# Step 8: Deploy to production
echo -e "${YELLOW}Deploying to production...${NC}"
./deploy.sh docker prod-server

echo -e "${GREEN}✓ Production deployment successful${NC}"
echo -e "${GREEN}✓ Release $VERSION deployed!${NC}"
```

Make it executable:
```bash
chmod +x homework4/ci-cd/deploy-release.sh
```

Usage:
```bash
cd /path/to/cs330-projects
./homework4/ci-cd/deploy-release.sh v1.0.0
```

## Environment Variables for Deployment

When deploying from CI/CD images, ensure these are set:

```bash
# For GHCR images
export GHCR_USERNAME=your-github-username
export GHCR_PASSWORD=your-github-token  # With read:packages scope

# For Docker Hub images
export DOCKER_USERNAME=your-docker-username
export DOCKER_PASSWORD=your-docker-token
```

## Monitoring Deployed Images

### Check Running Container Image

```bash
# SSH to your server
ssh dxcluster@your-server

# See what version is running
docker ps --format "table {{.Names}}\t{{.Image}}"

# Get full image SHA
docker inspect dx-cluster-api | grep -i image
```

### Update Running Containers

```bash
# From your server, update to latest images
cd /opt/dxcluster
docker-compose pull
docker-compose up -d

# Verify update
docker-compose ps
docker logs dx-cluster-api
docker logs dx-cluster-web
```

## Rollback Procedure

If something goes wrong after deployment:

```bash
# Get previous image tag from release history
gh release list --limit 5

# Redeploy to previous version
cd homework4/ansible
sed -i "s/dxcluster_api_tag: .*/dxcluster_api_tag: \"v1.0.0-old\"/" group_vars/all.yml
sed -i "s/dxcluster_web_tag: .*/dxcluster_web_tag: \"v1.0.0-old\"/" group_vars/all.yml

./deploy.sh docker prod-server
```

## Troubleshooting

### "Image pull failed: unauthorized"

**Issue:** Ansible can't pull GHCR images

**Solution:**
```yaml
# In group_vars/all.yml, add:
ghcr_username: "your-github-username"
ghcr_password: "your-github-token"
use_ghcr: true
```

### "docker-compose.yml: Template not found"

**Issue:** Template file missing

**Solution:**
```bash
# Verify template exists
ls -la homework4/ansible/roles/dxcluster_docker/templates/

# Create if missing - copy from docker-compose.yml.j2 example above
```

### Old images still running after deployment

**Issue:** docker-compose didn't pull new images

**Solution:**
```bash
# On server:
docker-compose pull --no-parallel
docker-compose up -d --force-recreate
```

## Next Steps

1. ✅ Build and push first release via CI/CD
2. ✅ Test image pulls locally
3. ✅ Update Ansible configuration for new images
4. ✅ Deploy to staging environment
5. ✅ Test staging thoroughly
6. ✅ Deploy to production
7. ⏳ Monitor and verify production deployment
8. ⏳ Set up automated monitoring/alerts

## Related Documentation

- [Main CI/CD README](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Secrets Configuration](SECRETS_SETUP.md)
- [Ansible Documentation](../ansible/README.md)
- [Terraform Documentation](../terraform/README.md)

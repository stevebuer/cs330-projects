````markdown
# Local Docker Build Script

Build and push Docker containers locally without waiting for GitHub Actions.

**Date**: November 6, 2025  
**Status**: ✅ Ready to use  
**Purpose**: Fast local testing and development builds

---

## Overview

The `build-local.sh` script provides a convenient way to:

- ✅ Build Docker images locally
- ✅ Push to any container registry (GHCR, Docker Hub, private registries)
- ✅ Test builds before committing
- ✅ Support multi-platform builds with Buildx
- ✅ Manage credentials securely
- ✅ Provide detailed colored output and progress

---

## Quick Start (30 seconds)

```bash
# From repository root
cd homework4/ci-cd

# Build locally (no push)
./build-local.sh

# Build and push to GHCR
./build-local.sh -t v1.0.0 -p

# Build and push to Docker Hub
./build-local.sh -r docker.io -t v1.0.0 -p
```

That's it! The script handles everything else.

---

## Installation

The script is already included in the repository. Just make sure it's executable:

```bash
cd homework4/ci-cd
chmod +x build-local.sh
```

Or from the repository root:

```bash
chmod +x homework4/ci-cd/build-local.sh
```

---

## Usage

### Basic Syntax

```bash
./build-local.sh [OPTIONS]
```

### Options Reference

| Option | Alias | Value | Default | Purpose |
|--------|-------|-------|---------|---------|
| `--registry` | `-r` | URL | `ghcr.io` | Container registry host |
| `--tag` | `-t` | string | `latest` | Image tag |
| `--push` | `-p` | (flag) | false | Push to registry |
| `--username` | `-u` | string | (prompt) | Registry username |
| `--password` | `-pw` | string | (prompt) | Registry password/token |
| `--api-only` | | (flag) | false | Build only API |
| `--web-only` | | (flag) | false | Build only Web |
| `--buildx` | | (flag) | false | Use Docker Buildx |
| `--platforms` | | string | `linux/amd64` | Buildx platforms |
| `--help` | `-h` | (flag) | | Show help |

---

## Common Scenarios

### Scenario 1: Test Build Locally

Build images locally without pushing. Useful for testing Dockerfiles.

```bash
./build-local.sh -t test
```

**What happens:**
- Builds both dxcluster-api and dxcluster-web images
- Tags them as `ghcr.io/YOUR_USERNAME/dxcluster-api:test`
- Images available locally in Docker
- No push to registry

**Verify build:**
```bash
docker image ls | grep dxcluster
docker run ghcr.io/YOUR_USERNAME/dxcluster-api:test
```

### Scenario 2: Build and Push to GHCR (GitHub Container Registry)

Deploy to GitHub's container registry.

```bash
# First time: login to GHCR
docker login ghcr.io
# Use: username = YOUR_GITHUB_USERNAME
#      password = YOUR_GITHUB_TOKEN

# Then run build
./build-local.sh -t v1.0.0 -p
```

**What happens:**
- Builds both images
- Pushes to `ghcr.io/YOUR_USERNAME/dxcluster-api:v1.0.0`
- Accessible from anywhere with correct credentials

### Scenario 3: Build and Push to Docker Hub

Deploy to Docker Hub.

```bash
# First time: login to Docker Hub
docker login docker.io
# Use: username = YOUR_DOCKER_USERNAME
#      password = YOUR_DOCKER_PASSWORD

# Then run build
./build-local.sh -r docker.io -t v1.0.0 -p
```

**What happens:**
- Builds both images
- Pushes to `docker.io/YOUR_USERNAME/dxcluster-api:v1.0.0`
- Publicly accessible (depends on repository privacy settings)

### Scenario 4: Build Only the API Image

Build just the API without the web interface.

```bash
./build-local.sh --api-only -t test -p
```

**What happens:**
- Builds only dxcluster-api
- Skips dxcluster-web
- Good for API-only deployments

### Scenario 5: Build for Multiple Platforms

Create images for both AMD64 and ARM64 (e.g., for cloud and Raspberry Pi).

```bash
./build-local.sh --buildx --platforms linux/amd64,linux/arm64 -t multiarch -p
```

**Requirements:**
- Docker 20.10+
- Buildx extension available

**Note:** Buildx requires `--push` to save multi-platform images (can't load to local Docker).

### Scenario 6: Daily Timestamped Build

Create a daily build with today's date as tag.

```bash
./build-local.sh -t daily-$(date +%Y-%m-%d) -p
```

**Example output:**
```bash
# Nov 6, 2025
ghcr.io/YOUR_USERNAME/dxcluster-api:daily-2025-11-06
```

### Scenario 7: Staging Environment

Maintain a staging build for testing before production.

```bash
# Build and push staging
./build-local.sh -t staging -p

# Later, when ready for production
./build-local.sh -t v1.0.0 -p  # Tag as version
```

---

## Registry Configuration

### GitHub Container Registry (GHCR)

**Setup:**
```bash
# Generate personal access token at:
# https://github.com/settings/tokens
# Scopes needed: read:packages, write:packages, delete:packages

docker login ghcr.io
# Username: YOUR_GITHUB_USERNAME
# Password: <your-token>
```

**Build and push:**
```bash
./build-local.sh -t v1.0.0 -p
# Images: ghcr.io/stevebuer/dxcluster-api:v1.0.0
#         ghcr.io/stevebuer/dxcluster-web:v1.0.0
```

**Pull from other machines:**
```bash
docker pull ghcr.io/stevebuer/dxcluster-api:v1.0.0
```

### Docker Hub

**Setup:**
```bash
# Use your Docker Hub credentials
docker login docker.io
# Username: YOUR_DOCKER_USERNAME  
# Password: YOUR_DOCKER_PASSWORD
```

**Build and push:**
```bash
./build-local.sh -r docker.io -t v1.0.0 -p
# Images: docker.io/stevebuer/dxcluster-api:v1.0.0
#         docker.io/stevebuer/dxcluster-web:v1.0.0
```

**Pull from other machines:**
```bash
docker pull stevebuer/dxcluster-api:v1.0.0
```

### Private Registry

**Setup:**
```bash
docker login registry.example.com
# Username: your-username
# Password: your-password
```

**Build and push:**
```bash
./build-local.sh -r registry.example.com -t v1.0.0 -p
# Images: registry.example.com/dxcluster-api:v1.0.0
#         registry.example.com/dxcluster-web:v1.0.0
```

---

## Complete Examples

### Development Workflow

```bash
# 1. Test new Dockerfile changes locally
cd homework4/ci-cd
./build-local.sh -t dev

# 2. Verify images work
docker run ghcr.io/stevebuer/dxcluster-api:dev /bin/bash

# 3. When satisfied, push to staging
./build-local.sh -t staging -p

# 4. After review, tag as release
./build-local.sh -t v1.0.0 -p
```

### Production Release

```bash
# Build and push to production tag
./build-local.sh -t v1.0.0 -p

# Verify images in registry
curl -s https://ghcr.io/v2/stevebuer/dxcluster-api/tags/list | jq .

# Update deployment to use new version
# (In your Ansible or docker-compose files)
```

### Cross-Platform Release

```bash
# Build for multiple architectures
./build-local.sh --buildx \
  --platforms linux/amd64,linux/arm64 \
  -t v1.0.0 \
  -p
```

### Parallel Development

```bash
# Build API changes
./build-local.sh --api-only -t dev-api

# Build web changes  
./build-local.sh --web-only -t dev-web

# Test both
docker run ghcr.io/stevebuer/dxcluster-api:dev-api
docker run ghcr.io/stevebuer/dxcluster-web:dev-web
```

---

## Output Examples

### Successful Build (Local)

```
ℹ Docker Build Script

ℹ Verifying Docker installation...
✓ Docker is ready
ℹ Verifying Dockerfiles...
✓ Found homework2/Dockerfile.api
✓ Found homework2/Dockerfile.web

ℹ Configuration:
  Registry: ghcr.io
  Owner: stevebuer
  Tag: test
  Push: false
  Building: dxcluster-api
  Building: dxcluster-web

ℹ Building ghcr.io/stevebuer/dxcluster-api:test...
Step 1/10 : FROM python:3.11-slim
...
Step 10/10 : CMD ["python", "-m", "flask", "run"]
✓ Built ghcr.io/stevebuer/dxcluster-api:test

ℹ Building ghcr.io/stevebuer/dxcluster-web:test...
...
✓ Built ghcr.io/stevebuer/dxcluster-web:test

✓ Build completed successfully!

Image(s) available at:
  ghcr.io/stevebuer/dxcluster-api:test
  ghcr.io/stevebuer/dxcluster-web:test

ℹ Images built locally but not pushed. Use '-p' to push.
```

### Successful Build with Push

```
ℹ Docker Build Script

ℹ Verifying Docker installation...
✓ Docker is ready
ℹ Verifying Dockerfiles...
✓ Found homework2/Dockerfile.api
✓ Found homework2/Dockerfile.web

ℹ Configuration:
  Registry: ghcr.io
  Owner: stevebuer
  Tag: v1.0.0
  Push: true
  Building: dxcluster-api
  Building: dxcluster-web

ℹ Logging in to ghcr.io...
✓ Successfully logged in to ghcr.io

ℹ Building ghcr.io/stevebuer/dxcluster-api:v1.0.0...
...
✓ Built ghcr.io/stevebuer/dxcluster-api:v1.0.0
ℹ Pushing ghcr.io/stevebuer/dxcluster-api:v1.0.0...
✓ Pushed ghcr.io/stevebuer/dxcluster-api:v1.0.0

ℹ Building ghcr.io/stevebuer/dxcluster-web:v1.0.0...
...
✓ Built ghcr.io/stevebuer/dxcluster-web:v1.0.0
ℹ Pushing ghcr.io/stevebuer/dxcluster-web:v1.0.0...
✓ Pushed ghcr.io/stevebuer/dxcluster-web:v1.0.0

✓ Build completed successfully!

Image(s) available at:
  ghcr.io/stevebuer/dxcluster-api:v1.0.0
  ghcr.io/stevebuer/dxcluster-web:v1.0.0
```

---

## Troubleshooting

### Issue: Permission Denied

**Error:**
```
bash: ./build-local.sh: Permission denied
```

**Solution:**
```bash
chmod +x homework4/ci-cd/build-local.sh
```

### Issue: Docker Not Running

**Error:**
```
✗ Docker daemon is not running. Start Docker and try again.
```

**Solution:**
```bash
# On Linux
sudo systemctl start docker

# On macOS with Docker Desktop
# Click the Docker icon in Applications
```

### Issue: Dockerfile Not Found

**Error:**
```
✗ homework2/Dockerfile.api not found
```

**Solution:**
- Make sure you're running the script from the **repository root**
- Verify files exist: `ls homework2/Dockerfile.api`

### Issue: Authentication Failed

**Error:**
```
✗ Failed to login to ghcr.io
```

**Solution:**
```bash
# 1. Verify credentials
docker login ghcr.io

# 2. For GHCR, use personal access token (not password)
# Generate at: https://github.com/settings/tokens
# Scopes: read:packages, write:packages

# 3. For Docker Hub, use app password (not password)
# Generate at: https://hub.docker.com/settings/security
```

### Issue: Push Failed but Build Succeeded

**Error:**
```
✓ Built ghcr.io/stevebuer/dxcluster-api:v1.0.0
✗ Failed to push ghcr.io/stevebuer/dxcluster-api:v1.0.0
```

**Solution:**
```bash
# 1. Verify authentication
docker login ghcr.io

# 2. Manually push to diagnose
docker push ghcr.io/stevebuer/dxcluster-api:v1.0.0

# 3. Check image exists locally
docker image ls | grep dxcluster-api
```

### Issue: Out of Disk Space

**Error:**
```
error writing blob: write failed: no space left on device
```

**Solution:**
```bash
# Clean up old images
docker image prune -a

# Check disk space
df -h

# Remove build cache
docker builder prune -a
```

### Issue: Network Timeout

**Error:**
```
error pulling image: Get "https://registry.docker.io/...": dial tcp: lookup on ...: no such host
```

**Solution:**
- Check internet connection: `ping 8.8.8.8`
- Try again later (registry might be temporarily down)
- For private registry, verify network connectivity to registry host

---

## Advanced Usage

### Dry Run (No Push)

Test everything except the actual push:

```bash
./build-local.sh -t v1.0.0
# Images built and available locally
# No push to registry
```

### Using Environment Variables

```bash
export DOCKER_REGISTRY="ghcr.io"
export DOCKER_TAG="v1.0.0"
./build-local.sh -r $DOCKER_REGISTRY -t $DOCKER_TAG -p
```

### Integration with CI/CD

Use in scripts:

```bash
#!/bin/bash
set -e

cd homework4/ci-cd

# Build
./build-local.sh -t $(git describe --tags --always) -p

# Verify
echo "Verifying pushed image..."
docker pull ghcr.io/stevebuer/dxcluster-api:$(git describe --tags --always)
```

### Multi-Registry Push

Push to multiple registries:

```bash
# Push to GHCR
./build-local.sh -r ghcr.io -t v1.0.0 -p

# Push to Docker Hub
./build-local.sh -r docker.io -t v1.0.0 -p
```

---

## Comparing with GitHub Actions

### Local Build (build-local.sh)

**Pros:**
- Fast (no GitHub queue time)
- Instant feedback
- Test before committing
- Full control and debugging
- Works offline (for local-only builds)

**Cons:**
- Requires Docker installed locally
- Manual credential management
- Must remember to push

### GitHub Actions (CI/CD)

**Pros:**
- Automated with each commit/release
- No local setup needed
- Audit trail in GitHub
- Consistent build environment
- Scheduled builds possible

**Cons:**
- Slower (3-5 minute queue + build time)
- No local debugging
- Requires GitHub commit

### Recommendation

**Use both:**
- **Local**: During development for fast iteration
- **GitHub Actions**: For official releases and CI/CD

---

## Integration with Ansible Deployment

After building and pushing, update your Ansible playbook:

```yaml
# ansible/group_vars/all.yml
dxcluster_api_version: v1.0.0    # Update this
dx_analysis_version: v1.0.0      # Update this

# Then deploy
./deploy.sh docker prod-server
```

---

## Script Features

### Colored Output
- 🔵 Blue: Information
- 🟢 Green: Success
- 🔴 Red: Errors
- 🟡 Yellow: Warnings

### Error Handling
- Exits on first error
- Comprehensive error messages
- Helpful troubleshooting hints

### Progress Tracking
- Clear step-by-step output
- Build step details
- Push confirmation

### User-Friendly
- Comprehensive help: `./build-local.sh -h`
- Interactive prompts for missing values
- Sensible defaults for most options

---

## Files

| File | Purpose | Location |
|------|---------|----------|
| `build-local.sh` | Main build script | `homework4/ci-cd/` |
| `LOCAL_BUILD.md` | This documentation | `homework4/ci-cd/` |
| `QUICKSTART.md` | GitHub Actions quick start | `homework4/ci-cd/` |
| `build-and-push.yml` | GitHub Actions workflow | `.github/workflows/` |

---

## Questions?

See detailed documentation:
- [QUICKSTART.md](QUICKSTART.md) - GitHub Actions pipeline
- [README.md](README.md) - CI/CD overview
- `./build-local.sh -h` - Built-in help

---

**Ready to build! 🚀**

Start with:
```bash
cd homework4/ci-cd
./build-local.sh -h
```

````

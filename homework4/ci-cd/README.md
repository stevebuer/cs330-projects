# CS330 Homework4 - CI/CD Pipeline

GitHub Actions-based CI/CD pipeline for building and publishing Docker containers without automatic builds on every push.

## Overview

This pipeline enables on-demand Docker image building and publishing to either Docker Hub or GitHub Container Registry (GHCR) with zero configuration required for routine pushes to the repository.

### Features

✅ **Manual Trigger on Demand**
- Build and push containers only when explicitly requested
- No automatic builds on git push events
- Reduces build costs and GitHub Actions minutes

✅ **Release-Based Builds**
- Automatically builds and publishes images when releases are published in GitHub
- Release tag becomes the image tag for traceability

✅ **Dual Registry Support**
- Deploy to Docker Hub or GitHub Container Registry
- Choose registry at build time via workflow inputs

✅ **Image Caching**
- Registry-based layer caching for faster subsequent builds
- Automatic buildcache management

✅ **Build Artifacts**
- Two container images: `dxcluster-api` and `dxcluster-web`
- Consistent tagging and naming conventions

## Quick Start Options

### Option A: Local Builds (Fastest for Development)

Build and push containers directly from your machine:

```bash
cd homework4/ci-cd

# Build locally (no push)
./build-local.sh

# Build and push to GHCR
./build-local.sh -t v1.0.0 -p

# See all options
./build-local.sh -h
```

✅ **Why local builds?**
- Instant feedback (no 5-minute GitHub queue)
- Test before committing
- Full debugging control
- Works offline for local-only builds

**For details**, see [LOCAL_BUILD.md](LOCAL_BUILD.md)

### Option B: GitHub Actions (Automated)

Use GitHub Actions for automatic builds on release or manual trigger.

## Setup Instructions (GitHub Actions)

### 1. Install the Workflow File

Copy the workflow file to your repository's `.github/workflows` directory:

```bash
mkdir -p .github/workflows
cp ci-cd/github-actions-build-and-push.yml .github/workflows/build-and-push.yml
```

### 2. Configure Secrets (for Docker Hub)

If you plan to use Docker Hub, add these secrets to your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Create these secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub personal access token

For GitHub Container Registry (GHCR), the `GITHUB_TOKEN` is automatically available - no additional setup needed.

### 3. Verify Repository Settings

Ensure GitHub Actions is enabled:
- **Settings → Actions → General**
- Select "Allow all actions and reusable workflows"

## Usage

### Manual Build Trigger (Recommended)

Manually trigger a build through the GitHub UI:

1. Go to **Actions → Build and Push Docker Images**
2. Click **Run workflow**
3. Configure inputs:
   - **Registry**: Choose `docker` (Docker Hub) or `ghcr` (GitHub Container Registry)
   - **Tag**: Specify the image tag (e.g., `latest`, `v1.0.0`, `2025-01-15`)
   - **Push**: Toggle whether to push images after building

### Release-Based Build (Automatic)

When you create a release on GitHub:

1. Go to **Releases → Create a new release**
2. Tag version (e.g., `v1.0.0`)
3. Publish the release
4. Pipeline automatically builds and pushes images to GHCR with the release tag

To create a release:

```bash
# Create a git tag locally
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0

# Then create release on GitHub UI, or use GitHub CLI:
gh release create v1.0.0 --title "Version 1.0.0" --generate-notes
```

## Image Locations

### Docker Hub Images

After pushing to Docker Hub with tag `latest`:
```
docker pull yourusername/dxcluster-api:latest
docker pull yourusername/dxcluster-web:latest
```

### GitHub Container Registry Images

After pushing to GHCR with tag `latest`:
```
docker pull ghcr.io/yourusername/dxcluster-api:latest
docker pull ghcr.io/yourusername/dxcluster-web:latest
```

Substitute `yourusername` with your actual GitHub/Docker username.

## Workflow Inputs (Manual Trigger)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `registry` | choice | `ghcr` | Target registry: `docker` or `ghcr` |
| `tag` | string | `latest` | Image tag (e.g., `v1.0.0`, `2025-01-15`) |
| `push` | boolean | `true` | Whether to push after building |

## Build Matrix

The pipeline builds the following images:

| Name | Dockerfile | Path | Purpose |
|------|-----------|------|---------|
| `dxcluster-api` | `Dockerfile.api` | `homework2/` | Flask API server |
| `dxcluster-web` | `Dockerfile.web` | `homework2/` | Dash web dashboard |

## Environment Variables

The workflow automatically determines configuration based on inputs:

```yaml
# For manual trigger with registry="docker" and tag="latest"
API_IMAGE: docker.io/yourusername/dxcluster-api:latest
WEB_IMAGE: docker.io/yourusername/dxcluster-web:latest

# For release trigger with tag="v1.0.0"
API_IMAGE: ghcr.io/yourusername/dxcluster-api:v1.0.0
WEB_IMAGE: ghcr.io/yourusername/dxcluster-web:v1.0.0
```

## Build Output

After a successful build, the GitHub Actions summary includes:

- Registry used (docker.io or ghcr.io)
- Image tag applied
- Full image URIs for both containers
- Whether images were pushed to registry

## Troubleshooting

### Build Fails: "authentication required"

**Docker Hub Issue:**
- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set
- Confirm Docker Hub personal access token has "Read, Write & Delete" permissions

**GHCR Issue:**
- Confirm GitHub Actions permissions allow package write access
- Check Settings → Actions → General → Permissions

### Build Times Out

The workflow includes cache optimization. If you still experience timeouts:
- Reduce build context size
- Pre-build dependencies in intermediate images
- Split into separate workflows for each container

### Push Fails but Build Succeeds

Check that:
- Secrets are properly configured
- Registry credentials have push permissions
- Registry quota/limits haven't been exceeded

## Cost Considerations

Using this on-demand approach:
- **No cost for code pushes**: Only your own builds trigger builds
- **Predictable costs**: Only build when releasing or testing
- **GitHub Actions minutes**: ~5-10 minutes per build workflow

Compare to automatic builds: This saves 20+ builds per month on active projects.

## Next Steps

1. ✅ Copy workflow file to `.github/workflows/`
2. ✅ Configure Docker Hub secrets (if using Docker Hub)
3. ✅ Test manual trigger with `tag="test"`
4. ✅ Verify image appears in registry
5. ✅ Create first release for automatic build
6. ⏳ Integrate with Terraform/Ansible deployment

## Related Files

- `build-local.sh` - Local build script (new!)
- `LOCAL_BUILD.md` - Local build documentation (new!)
- `github-actions-build-and-push.yml` - GitHub Actions workflow
- `../terraform/` - Infrastructure deployment
- `../ansible/` - Configuration management
- `../../homework2/Dockerfile.api` - API container definition
- `../../homework2/Dockerfile.web` - Web container definition

## Advanced Configuration

### Custom Build Arguments

To add build arguments to the Dockerfile, modify the workflow step:

```yaml
- name: Build and push dxcluster-api
  uses: docker/build-push-action@v5
  with:
    context: ./homework2
    file: ./homework2/Dockerfile.api
    build-args: |
      BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
      VCS_REF=${{ github.sha }}
    push: true
    tags: ${{ steps.meta.outputs.api_image }}
```

### Multi-Architecture Builds

To build for multiple architectures (ARM64, AMD64):

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  with:
    platforms: linux/amd64,linux/arm64
```

### Scan Images for Vulnerabilities

Add after building:

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.meta.outputs.api_image }}
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload Trivy results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

## Questions?

For more information:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

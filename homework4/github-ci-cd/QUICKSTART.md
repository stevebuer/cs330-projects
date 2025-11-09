# CI/CD Pipeline - Quick Start

Get your Docker CI/CD pipeline running in 5 minutes.

## 1-Minute Setup

### Copy the Workflow File

```bash
# From repository root
mkdir -p .github/workflows
cp homework4/ci-cd/github-actions-build-and-push.yml .github/workflows/build-and-push.yml

# Commit and push
git add .github/workflows/build-and-push.yml
git commit -m "Add GitHub Actions CI/CD pipeline"
git push origin main
```

**That's it!** The workflow is now installed.

## Test Your Setup (2 minutes)

### Manual Test Build

1. Go to your GitHub repository
2. Click the **Actions** tab
3. In the left sidebar, click **Build and Push Docker Images**
4. Click **Run workflow** (blue button on right)
5. Fill in the form:
   - **Registry:** Select `ghcr` (or `docker` if using Docker Hub)
   - **Tag:** Enter `test`
   - **Push:** Leave checked
6. Click **Run workflow**

Watch the build process:
- It should take 3-5 minutes
- You'll see build steps for both images
- At the end, check the summary for image URIs

### Verify Images Were Built

After successful build, your images are now available:

**For GHCR:**
```bash
# Pull the API image
docker pull ghcr.io/stevebuer/dxcluster-api:test

# Pull the web image  
docker pull ghcr.io/stevebuer/dxcluster-web:test
```

**For Docker Hub:**
```bash
# First login
docker login -u YOUR_USERNAME

# Pull the images
docker pull YOUR_USERNAME/dxcluster-api:test
docker pull YOUR_USERNAME/dxcluster-web:test
```

## Regular Usage

### Build for a Release

**Option A: Using GitHub UI (Recommended)**

1. Go to **Releases** on GitHub
2. Click **Create a new release**
3. Set tag to version (e.g., `v1.0.0`)
4. Click **Publish release**
5. Pipeline automatically builds and pushes with tag `v1.0.0`

**Option B: Using Git Command Line**

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create release on GitHub
gh release create v1.0.0 --title "Version 1.0.0" --generate-notes
```

### Build with Custom Tag

Via GitHub Actions UI:

1. Go to **Actions** → **Build and Push Docker Images**
2. Click **Run workflow**
3. Enter your custom tag (e.g., `2025-01-15`, `staging`, `prod`)
4. Choose registry
5. Click **Run workflow**

## Common Workflows

### Scenario 1: Testing a Build Without Pushing

```
Registry: ghcr (or docker)
Tag: staging
Push: Unchecked
```

This builds locally without pushing to the registry. Useful for testing Dockerfiles.

### Scenario 2: Release to Production

```
Go to Releases → Create new release with tag v1.0.0
```

Pipeline automatically:
- Builds both images
- Tags them as `v1.0.0`
- Pushes to GHCR
- No manual input needed!

### Scenario 3: Weekly Rebuild with Latest Code

```
Registry: ghcr
Tag: weekly-$(date +%Y-%m-%d)
Push: Checked
```

This creates a timestamped build like `weekly-2025-01-15`.

### Scenario 4: Staging Environment

```
Registry: ghcr
Tag: staging
Push: Checked
```

Update staging environment to use `staging` tag. Re-run this workflow whenever you want a new staging build.

## Checking Build Status

### View Build History

1. Go to **Actions** tab
2. Click **Build and Push Docker Images**
3. See all past and current builds with status

### View Build Logs

1. Click on any build in the history
2. See detailed steps and output
3. Click any step to expand details
4. Useful for debugging failures

### Real-Time Monitoring

During a build, you can watch it:
1. Go to **Actions** tab
2. Click the currently running workflow
3. See live output as each step executes

## Pulling Built Images

### From GHCR (Public)

```bash
docker pull ghcr.io/stevebuer/dxcluster-api:latest
docker pull ghcr.io/stevebuer/dxcluster-web:latest
```

### From Docker Hub

```bash
docker login
docker pull stevebuer/dxcluster-api:latest
docker pull stevebuer/dxcluster-web:latest
```

### Using in Docker Compose

Update your `docker-compose.yml`:

```yaml
services:
  dx-api:
    image: ghcr.io/stevebuer/dxcluster-api:v1.0.0
    # ... rest of config

  dx-web:
    image: ghcr.io/stevebuer/dxcluster-web:v1.0.0
    # ... rest of config
```

## Next Steps After First Build

1. ✅ Successfully built first test
2. ⏳ Create first release (`v1.0.0`)
3. ⏳ Verify release build succeeded
4. ⏳ Pull and test images locally
5. ⏳ Update deployment scripts to use images
6. ⏳ Integrate with Ansible playbooks

## Useful Links

- [View Builds](https://github.com/stevebuer/cs330-projects/actions/workflows/build-and-push.yml)
- [View Releases](https://github.com/stevebuer/cs330-projects/releases)
- [View Packages](https://github.com/stevebuer/cs330-projects/pkgs/container/dxcluster-api)
- [Docker Hub Repos](https://hub.docker.com/u/stevebuer)

## Troubleshooting

### Build Failed: "File not found"

**Issue:** Dockerfile paths are wrong

**Solution:**
```bash
# Verify Dockerfiles exist
ls homework2/Dockerfile.api
ls homework2/Dockerfile.web

# Update workflow if paths are different
# Edit .github/workflows/build-and-push.yml
```

### Push Failed: "Unauthorized"

**Issue:** Credentials not configured

**Solution:**
- For Docker Hub: See [SECRETS_SETUP.md](SECRETS_SETUP.md)
- For GHCR: Should work automatically

### Build Succeeded but Image Not Found

**Issue:** Image didn't get pushed even though build succeeded

**Solution:**
```bash
# Check if "Push" checkbox was unchecked
# If so, re-run with Push: checked

# Or check registry settings in workflow
# Verify you're pulling from correct registry
```

## Questions?

See detailed documentation:
- [Main README](README.md) - Complete feature documentation
- [Secrets Setup](SECRETS_SETUP.md) - Configure authentication
- [GitHub Actions Docs](https://docs.github.com/en/actions) - Official documentation

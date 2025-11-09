# GitHub Secrets Configuration Guide

This guide walks through setting up the necessary secrets for the CI/CD pipeline to build and push Docker images.

## Quick Setup (5 minutes)

### Option 1: Using GitHub Container Registry (GHCR) - Recommended

GitHub Container Registry uses your repository's existing `GITHUB_TOKEN`, so **no additional setup is required**.

Just copy the workflow file to `.github/workflows/` and you're ready to use GHCR.

### Option 2: Using Docker Hub

If you want to push to Docker Hub, follow these steps:

## Docker Hub Setup

### Step 1: Create Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com) and sign in
2. Click your profile icon → **Account Settings**
3. Go to **Security** tab
4. Click **New Access Token**
5. Set a name like "GitHub Actions - DX Cluster"
6. Select "Read & Write" permissions
7. Click **Generate**
8. **Copy the token immediately** (you won't see it again!)

### Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In the left sidebar, go to **Secrets and variables** → **Actions**
4. Click **New repository secret**

Add these two secrets:

**Secret 1:**
- Name: `DOCKER_USERNAME`
- Value: Your Docker Hub username (e.g., `stevebuer`)

**Secret 2:**
- Name: `DOCKER_PASSWORD`
- Value: The access token you just generated

### Step 3: Test Connection

You can test the secrets by:
1. Going to **Actions** tab in GitHub
2. Selecting **Build and Push Docker Images**
3. Clicking **Run workflow**
4. Selecting `registry: docker`, `tag: test`
5. Watching the build process

## GitHub Container Registry Setup (Recommended)

### Why GHCR?

- ✅ No additional secrets needed
- ✅ Automatic authentication via `GITHUB_TOKEN`
- ✅ Images stored alongside your code
- ✅ Better integration with GitHub
- ✅ Free tier is generous

### How to Use GHCR

The workflow automatically uses GHCR when:
- Running a release (automatic)
- Manually triggered with `registry: ghcr`

No secrets setup needed!

### Access GHCR Images

To pull images from GHCR:

```bash
# Authenticate with GitHub (first time only)
echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u USERNAME --password-stdin

# Pull image
docker pull ghcr.io/stevebuer/dxcluster-api:latest
```

Or use a GitHub Personal Access Token:

```bash
# Create PAT with 'read:packages' scope
# Then authenticate:
echo YOUR_PAT | docker login ghcr.io -u USERNAME --password-stdin
```

## Verify Secrets Are Set

To verify your secrets are configured:

```bash
# This won't show the actual values, but confirms they exist
gh secret list -R stevebuer/cs330-projects
```

Expected output:
```
DOCKER_PASSWORD  Updated Nov 4, 2025
DOCKER_USERNAME  Updated Nov 4, 2025
```

## Rotating Secrets

### Docker Hub Token

To rotate your Docker Hub token:

1. Go to Docker Hub → **Account Settings** → **Security**
2. Find the "GitHub Actions - DX Cluster" token
3. Click the trash icon to delete it
4. Create a new token following "Step 1" above
5. Update the `DOCKER_PASSWORD` secret in GitHub

### GitHub Token

GitHub's `GITHUB_TOKEN` is automatically rotated for each workflow run, so no action needed.

## Troubleshooting

### "authentication required"

**Issue:** Workflow fails with authentication error

**Solution:**
```bash
# Verify secrets are set
gh secret list -R your-org/your-repo

# If missing, check naming:
# Must be exactly: DOCKER_USERNAME and DOCKER_PASSWORD
# (case-sensitive!)
```

### "Unauthorized: authentication required"

**Issue:** Push fails even with correct credentials

**Possible causes:**
1. Docker Hub token lacks push permissions
   - Go to Docker Hub → Settings → Security
   - Delete old token, create new one with full read/write/delete

2. Username is incorrect
   - Verify it matches your Docker Hub username exactly

3. Repository doesn't exist
   - The workflow creates public repositories automatically
   - If using private repos, create them first on Docker Hub

### "Invalid username or password"

**Issue:** Credentials not working

**Solution:**
```bash
# Test locally first
docker login -u YOUR_USERNAME

# When prompted for password, use the access token (not your password!)

# If that works, update GitHub secret:
# Settings → Secrets and variables → Actions → DOCKER_PASSWORD
```

## Best Practices

✅ **Do:**
- Use access tokens instead of passwords
- Set limited permissions on tokens
- Regularly rotate tokens
- Keep token names descriptive

❌ **Don't:**
- Hardcode credentials in workflow files
- Share tokens in chat or commit messages
- Use your Docker Hub password directly
- Commit `.env` files with secrets

## Multiple Registries

You can use both Docker Hub and GHCR by running the workflow twice with different registry choices:

```bash
# Push to Docker Hub with tag "latest"
gh workflow run build-and-push.yml -f registry=docker -f tag=latest

# Push to GHCR with tag "v1.0.0"
gh workflow run build-and-push.yml -f registry=ghcr -f tag=v1.0.0
```

## Secrets Reference

| Secret Name | Used For | Example |
|-------------|----------|---------|
| `DOCKER_USERNAME` | Docker Hub authentication | `stevebuer` |
| `DOCKER_PASSWORD` | Docker Hub authentication | `dckr_pat_XXX...` |
| (None needed) | GHCR authentication | Uses `GITHUB_TOKEN` |

## Next Steps

1. ✅ Choose your registry (GHCR recommended)
2. ✅ If Docker Hub, create access token and add secrets
3. ✅ Test workflow with manual trigger
4. ✅ Verify image appears in registry
5. ✅ Create a release to test automatic build

---

For more help:
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Docker Hub Token Documentation](https://docs.docker.com/docker-hub/access-tokens/)
- [GHCR Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

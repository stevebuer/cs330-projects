# CI/CD Pipeline - Quick Reference Card

Print this or bookmark for quick lookup while working.

## 📦 Installation (One-Time Setup)

```bash
# 1. Copy workflow to GitHub
mkdir -p .github/workflows
cp homework4/ci-cd/github-actions-build-and-push.yml .github/workflows/build-and-push.yml

# 2. Commit and push
git add .github/workflows/build-and-push.yml
git commit -m "Add CI/CD pipeline"
git push origin main

# ✅ Done! Check Actions tab to verify
```

## 🎯 Build a Release (Most Common)

```bash
# Create tag and release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Create GitHub release (triggers build automatically)
gh release create v1.0.0 --generate-notes

# Wait 5-10 minutes...
# Images available at:
# - ghcr.io/stevebuer/dxcluster-api:v1.0.0
# - ghcr.io/stevebuer/dxcluster-web:v1.0.0
```

## 🚀 Manual Build (On-Demand)

**Via GitHub UI:**
1. Go to **Actions** tab
2. Click **Build and Push Docker Images**
3. Click **Run workflow** button
4. Fill in:
   - Registry: `ghcr` (or `docker`)
   - Tag: `latest` (or your tag)
   - Push: ☑️ checked
5. Click **Run workflow**
6. Wait 5-10 minutes

## 🐳 Pull Built Images

```bash
# From GHCR (GitHub Container Registry)
docker pull ghcr.io/stevebuer/dxcluster-api:latest
docker pull ghcr.io/stevebuer/dxcluster-web:latest

# From Docker Hub (if using docker registry)
docker pull yourusername/dxcluster-api:latest
docker pull yourusername/dxcluster-web:latest
```

## 🔐 Setup Authentication (First-Time Only)

### GitHub Container Registry (GHCR) - Default
✅ **No setup needed!** Automatic via GITHUB_TOKEN

### Docker Hub (Optional)
```bash
# 1. Create token at hub.docker.com → Settings → Security
#    Copy the token

# 2. Add GitHub secrets:
#    Settings → Secrets and variables → Actions
#    - DOCKER_USERNAME: your-docker-username
#    - DOCKER_PASSWORD: your-docker-token

# 3. Use registry: docker in workflow
```

## 📊 Available Registries

| Registry | Default | Setup | Speed | Recommendation |
|----------|---------|-------|-------|-----------------|
| GHCR | ✅ Yes | None | 🚀 Fast | Use this |
| Docker Hub | ❌ No | Secrets | 🚀 Fast | Optional |

## 🎨 Image Output

Per build, these images are created:

```
🐳 dxcluster-api    (Flask API server, port 8080)
🐳 dxcluster-web    (Dash dashboard, port 8050)
```

With chosen tag:
```
ghcr.io/stevebuer/dxcluster-api:TAG
ghcr.io/stevebuer/dxcluster-web:TAG
```

## 💡 Common Tags

| Tag | Use Case | Example |
|-----|----------|---------|
| `latest` | Current stable | `latest` |
| `vX.Y.Z` | Release version | `v1.0.0` |
| `staging` | Staging env | `staging` |
| `test` | Testing | `test` |
| `date` | Timestamped | `2025-01-15` |

## 🔍 Monitor Build Progress

```bash
# In GitHub UI:
1. Go to Actions tab
2. Click "Build and Push Docker Images"
3. Click the running workflow
4. Watch real-time logs

# Or check specific images:
docker pull ghcr.io/stevebuer/dxcluster-api:TAG
```

## 🚨 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Workflow not found | Restart browser or check `.github/workflows/` exists |
| Build fails (Docker) | Verify `homework2/Dockerfile.*` exist |
| Push fails | Check GitHub secrets are set (`DOCKER_*`) |
| Can't pull image | Check tag matches, verify in registry UI |
| Build too slow | It's normal (10-15 min first time, 3-5 min cached) |

## 📚 Documentation Files

| File | Use When |
|------|----------|
| `INDEX.md` | Need to navigate docs |
| `QUICKSTART.md` | Starting out (5 min) |
| `README.md` | Want all details |
| `SECRETS_SETUP.md` | Setting up auth |
| `DEPLOYMENT_INTEGRATION.md` | Deploying with Ansible |
| `IMPLEMENTATION_SUMMARY.md` | Need overview |

**Read first:** `QUICKSTART.md`

## 🚀 Deploy Built Image (With Ansible)

```bash
# 1. Update Ansible variables
cd homework4/ansible
nano group_vars/all.yml

# Change:
# dxcluster_api_tag: "v1.0.0"
# dxcluster_web_tag: "v1.0.0"

# 2. Deploy to staging
./deploy.sh docker staging-server

# 3. Test staging thoroughly
./deploy.sh status staging-server

# 4. Deploy to production
./deploy.sh docker prod-server
```

Or use the automated script:
```bash
./homework4/ci-cd/deploy-release.sh v1.0.0
```

## 🔄 Full Release Workflow (From Start to Finish)

```bash
# Step 1: Make changes and commit
git add .
git commit -m "Update DX Cluster components"
git push origin main

# Step 2: Create release (auto-triggers build)
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
gh release create v1.0.0 --generate-notes

# Step 3: Wait for build (5-10 min)
# Go to Actions tab and watch

# Step 4: Update Ansible
cd homework4/ansible
sed -i 's/dxcluster_api_tag: .*/dxcluster_api_tag: "v1.0.0"/' group_vars/all.yml
sed -i 's/dxcluster_web_tag: .*/dxcluster_web_tag: "v1.0.0"/' group_vars/all.yml

# Step 5: Deploy to staging
./deploy.sh docker staging-server

# Step 6: Deploy to production
./deploy.sh docker prod-server

# ✅ Done! New version in production
```

## 🎯 Workflow Inputs (Manual Trigger)

| Input | Type | Options | Default | Example |
|-------|------|---------|---------|---------|
| `registry` | choice | `docker`, `ghcr` | `ghcr` | Use `ghcr` |
| `tag` | string | Any string | `latest` | `v1.0.0` |
| `push` | boolean | true, false | `true` | Check box |

## 📍 Image Locations After Build

**GHCR (if using ghcr):**
```
ghcr.io/stevebuer/dxcluster-api:TAG
ghcr.io/stevebuer/dxcluster-web:TAG
```

**Docker Hub (if using docker):**
```
docker.io/yourusername/dxcluster-api:TAG
docker.io/yourusername/dxcluster-web:TAG
```

## 🔗 Useful Links

- [View Workflows](https://github.com/stevebuer/cs330-projects/actions)
- [View Releases](https://github.com/stevebuer/cs330-projects/releases)
- [GHCR Packages](https://github.com/stevebuer/cs330-projects/pkgs/container/dxcluster-api)
- [Docker Hub](https://hub.docker.com/u/stevebuer)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

## ⏱️ Timing Reference

| Activity | Time | Notes |
|----------|------|-------|
| First build | 10-15 min | All layers downloaded |
| Cached build | 3-5 min | Uses layer cache |
| Push to registry | ~1 min | Automatic |
| Full workflow run | 12-20 min | From trigger to complete |
| Manual workflow trigger | < 1 min | Just to start build |
| Release publication | < 1 min | Auto-triggers build |

## 🎓 Learning Path

1. **Day 1:** Read `QUICKSTART.md` → Run test build
2. **Day 2:** Read `SECRETS_SETUP.md` → Configure registry (if needed)
3. **Day 3:** Create first release → Watch auto-build
4. **Day 4:** Read `DEPLOYMENT_INTEGRATION.md` → Set up Ansible
5. **Day 5:** Deploy to staging → Verify and promote to production

## 💾 Key Files

```
.github/workflows/build-and-push.yml     ← Workflow definition
homework2/Dockerfile.api                 ← API container
homework2/Dockerfile.web                 ← Web container
homework4/ci-cd/                         ← Documentation
homework4/ansible/group_vars/all.yml     ← Deployment config
```

## ✅ Pre-Flight Checklist

- [ ] Workflow file copied to `.github/workflows/`
- [ ] Changes committed and pushed
- [ ] Workflow visible in GitHub Actions tab
- [ ] Test build completed successfully
- [ ] Image found in registry (GHCR or Docker Hub)
- [ ] Ansible variables ready to update
- [ ] Infrastructure deployed via Terraform

---

**Quick Links:**
- Installation: See above ⬆️
- Quick Start: [QUICKSTART.md](QUICKSTART.md)
- Full Docs: [README.md](README.md)
- Help: [INDEX.md](INDEX.md)

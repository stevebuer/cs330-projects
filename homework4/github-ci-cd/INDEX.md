# CI/CD Pipeline Documentation Index

Quick navigation for the CI/CD pipeline documentation.

## 📚 Quick Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [QUICKSTART.md](QUICKSTART.md) | Get running in 5 minutes | 5 min |
| [README.md](README.md) | Complete feature documentation | 10 min |
| [SECRETS_SETUP.md](SECRETS_SETUP.md) | Configure authentication | 5 min |
| [DEPLOYMENT_INTEGRATION.md](DEPLOYMENT_INTEGRATION.md) | Integrate with Ansible/Terraform | 15 min |

## 🚀 Getting Started

**Choose your path:**

### I just want to get it working (5 min)
→ Start with [QUICKSTART.md](QUICKSTART.md)

### I want to understand all the details
→ Read [README.md](README.md) first, then [SECRETS_SETUP.md](SECRETS_SETUP.md)

### I need to set up authentication
→ Go to [SECRETS_SETUP.md](SECRETS_SETUP.md)

### I want to deploy built images
→ See [DEPLOYMENT_INTEGRATION.md](DEPLOYMENT_INTEGRATION.md)

## 🎯 Common Tasks

### Build a Docker image
1. Go to GitHub Actions tab
2. Select "Build and Push Docker Images"
3. Click "Run workflow"
4. Fill in tag and registry
5. Watch build progress

See: [QUICKSTART.md - Test Your Setup](QUICKSTART.md#test-your-setup-2-minutes)

### Create a release with automatic build
```bash
git tag -a v1.0.0 -m "Release"
git push origin v1.0.0
gh release create v1.0.0 --generate-notes
```

See: [QUICKSTART.md - Build for a Release](QUICKSTART.md#build-for-a-release)

### Deploy to production
```bash
./homework4/ci-cd/deploy-release.sh v1.0.0
```

See: [DEPLOYMENT_INTEGRATION.md](DEPLOYMENT_INTEGRATION.md)

### Set up Docker Hub authentication
1. Create Docker Hub access token
2. Add GitHub secrets: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
3. Use `docker` registry in workflow

See: [SECRETS_SETUP.md - Docker Hub Setup](SECRETS_SETUP.md#docker-hub-setup)

## 📋 File Structure

```
ci-cd/
├── INDEX.md                      ← You are here
├── QUICKSTART.md                 ← Start here
├── README.md                     ← Main documentation
├── SECRETS_SETUP.md              ← Authentication setup
├── DEPLOYMENT_INTEGRATION.md     ← Deploy with Ansible
└── github-actions-build-and-push.yml  ← Workflow definition
```

## 🔧 How It Works

```
┌──────────────────┐
│ Make Commit      │
└────────┬─────────┘
         │
    ❌ No auto-build
         │
    ✅ Manual trigger
         │
┌────────▼──────────────────┐
│ GitHub Actions Workflow   │
│ - Build dxcluster-api     │
│ - Build dxcluster-web     │
└────────┬──────────────────┘
         │
┌────────▼──────────────────┐
│ Push to Registry          │
│ - GHCR or Docker Hub      │
└────────┬──────────────────┘
         │
┌────────▼──────────────────┐
│ Deploy with Ansible       │
│ - Pull images             │
│ - Update docker-compose   │
│ - Run containers          │
└──────────────────────────┘
```

## 🎨 Workflow Inputs

When manually triggering a build:

| Input | Options | Default | Meaning |
|-------|---------|---------|---------|
| Registry | `docker` or `ghcr` | `ghcr` | Where to push images |
| Tag | Any string | `latest` | Version tag for images |
| Push | true/false | `true` | Push to registry after build |

## 📊 What Gets Built

Two Docker images per build:

| Image | Dockerfile | Purpose | Port |
|-------|-----------|---------|------|
| `dxcluster-api` | `homework2/Dockerfile.api` | Flask API server | 8080 |
| `dxcluster-web` | `homework2/Dockerfile.web` | Dash dashboard | 8050 |

## 🔐 Authentication

### GHCR (GitHub Container Registry) - Recommended ✅
- Automatic via `GITHUB_TOKEN`
- No setup required
- Free tier is generous
- Integrated with GitHub

### Docker Hub - Optional
- Requires personal access token
- Need to set 2 secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- See [SECRETS_SETUP.md](SECRETS_SETUP.md) for details

## 📈 Key Features

✅ **On-Demand Builds**
- Manual trigger prevents unnecessary builds
- Saves GitHub Actions minutes and compute resources

✅ **Release Automation**
- Automatic build on GitHub releases
- Release tag becomes image tag

✅ **Dual Registry Support**
- Build once, choose where to push
- Can use both GHCR and Docker Hub

✅ **Smart Caching**
- Registry-based layer caching
- Faster builds after first run

✅ **Build Summary**
- GitHub Actions step summary shows image URIs
- Easy copy/paste for deployment

## 🐛 Troubleshooting

### Build won't start
→ Check GitHub Actions is enabled in Settings

### Build fails immediately
→ Check workflow syntax: `.github/workflows/build-and-push.yml`

### Push fails but build succeeds
→ Check authentication secrets in Settings → Secrets

### Can't pull built image
→ Verify image URI and registry choice
→ See [SECRETS_SETUP.md - Verify Secrets Are Set](SECRETS_SETUP.md#verify-secrets-are-set)

See complete troubleshooting: [README.md - Troubleshooting](README.md#troubleshooting)

## ⏭️ Next Steps

1. ✅ Copy workflow file to `.github/workflows/`
2. ✅ Test with manual build (`tag: test`)
3. ✅ Verify image in registry
4. ✅ Create first release (`v1.0.0`)
5. ✅ Test Ansible deployment
6. ⏳ Monitor production deployment

## 📞 Getting Help

### Quick questions?
- Check [QUICKSTART.md](QUICKSTART.md) troubleshooting section
- See [README.md - Troubleshooting](README.md#troubleshooting)

### Setup issues?
- See [SECRETS_SETUP.md - Troubleshooting](SECRETS_SETUP.md#troubleshooting)

### Deployment help?
- See [DEPLOYMENT_INTEGRATION.md - Troubleshooting](DEPLOYMENT_INTEGRATION.md#troubleshooting)

### Still stuck?
- Check [GitHub Actions Documentation](https://docs.github.com/en/actions)
- See related files: `../terraform/README.md`, `../ansible/README.md`

## 📝 Workflow File

The main workflow file is: `github-actions-build-and-push.yml`

To install it:
```bash
mkdir -p .github/workflows
cp ci-cd/github-actions-build-and-push.yml .github/workflows/build-and-push.yml
git add .github/workflows/build-and-push.yml
git commit -m "Add GitHub Actions CI/CD pipeline"
git push origin main
```

## 🎓 Learning Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub Docs](https://docs.docker.com/docker-hub/)

---

**Start here:** [QUICKSTART.md](QUICKSTART.md) ⚡

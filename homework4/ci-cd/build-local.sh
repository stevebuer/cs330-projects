#!/bin/bash

# Local Docker Build and Push Script
# Builds dxcluster-api and dxcluster-web containers locally and optionally pushes to registry
# Usage: ./build-local.sh [OPTIONS]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
REGISTRY="ghcr.io"
TAG="latest"
PUSH=false
BUILD_API=true
BUILD_WEB=true
REGISTRY_USER=""
REGISTRY_PASS=""
BUILDX=false
PLATFORMS="linux/amd64"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -r|--registry)
      REGISTRY="$2"
      shift 2
      ;;
    -t|--tag)
      TAG="$2"
      shift 2
      ;;
    -p|--push)
      PUSH=true
      shift
      ;;
    -u|--username)
      REGISTRY_USER="$2"
      shift 2
      ;;
    -pw|--password)
      REGISTRY_PASS="$2"
      shift 2
      ;;
    --api-only)
      BUILD_WEB=false
      shift
      ;;
    --web-only)
      BUILD_API=false
      shift
      ;;
    --buildx)
      BUILDX=true
      shift
      ;;
    --platforms)
      PLATFORMS="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      show_help
      exit 1
      ;;
  esac
done

show_help() {
  cat << EOF
${BLUE}Local Docker Build and Push Script${NC}

${GREEN}USAGE:${NC}
  ./build-local.sh [OPTIONS]

${GREEN}OPTIONS:${NC}
  -r, --registry REGISTRY      Container registry (default: ghcr.io)
                               Options: ghcr.io, docker.io, or custom registry URL
  
  -t, --tag TAG                Image tag (default: latest)
                               Examples: v1.0.0, test, staging, 2025-01-15
  
  -p, --push                   Push images to registry after build
                               Without this flag, images are only built locally
  
  -u, --username USERNAME      Registry username (prompted if needed)
  
  -pw, --password PASSWORD     Registry password/token (prompted if needed)
  
  --api-only                   Build only dxcluster-api
  
  --web-only                   Build only dxcluster-web
  
  --buildx                     Use Docker Buildx for faster builds
                               Supports multi-platform builds
                               Note: Multi-platform builds require --push
  
  --platforms PLATFORMS        Buildx platforms (default: linux/amd64)
                               Examples: linux/amd64, linux/arm64
                               Multiple: linux/amd64,linux/arm64
  
  -h, --help                   Show this help message

${GREEN}EXAMPLES:${NC}
  # Build both images locally (no push)
  ./build-local.sh

  # Build and tag for testing
  ./build-local.sh -t test

  # Build and push to GHCR
  ./build-local.sh -t v1.0.0 -p

  # Build and push to Docker Hub
  ./build-local.sh -r docker.io -t latest -p

  # Build only the API image
  ./build-local.sh -t test --api-only

  # Use Buildx for multi-platform build
  ./build-local.sh --buildx --platforms linux/amd64,linux/arm64 -t latest -p

${GREEN}REGISTRY EXAMPLES:${NC}
  GitHub Container Registry:
    ./build-local.sh -r ghcr.io -t v1.0.0 -p
    # Images: ghcr.io/YOUR_USERNAME/dxcluster-api:v1.0.0

  Docker Hub:
    ./build-local.sh -r docker.io -t v1.0.0 -p
    # Images: YOUR_USERNAME/dxcluster-api:v1.0.0

  Private Registry:
    ./build-local.sh -r registry.example.com -t v1.0.0 -p
    # Images: registry.example.com/dxcluster-api:v1.0.0

${GREEN}AUTHENTICATION:${NC}
  GHCR (GitHub Container Registry):
    docker login ghcr.io
    # Use: username = YOUR_GITHUB_USERNAME
    #      password = YOUR_GITHUB_TOKEN (with read:packages, write:packages scopes)

  Docker Hub:
    docker login docker.io
    # Use: username = YOUR_DOCKER_USERNAME
    #      password = YOUR_DOCKER_PASSWORD

${GREEN}PREREQUISITES:${NC}
  - Docker installed and running
  - For push: authenticated to registry (docker login)
  - For Buildx: Docker version 20.10+

${GREEN}TROUBLESHOOTING:${NC}
  Can't push: Did you run 'docker login' for the registry?
  Build failed: Check that homework2/Dockerfile.api and Dockerfile.web exist
  Permission denied: Run 'chmod +x build-local.sh'

EOF
}

log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

# Get repository owner from GitHub config or prompt
get_repo_owner() {
  # Try to get from git remote
  local remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
  
  if [[ $remote_url =~ /([^/]+)/[^/]+\.git$ ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    # If not in git repo, ask user
    if [[ $REGISTRY == "ghcr.io" ]] || [[ $REGISTRY == "docker.io" ]]; then
      read -p "Enter your GitHub/Docker username: " username
      echo "$username"
    fi
  fi
}

# Verify Docker is running
verify_docker() {
  log_info "Verifying Docker installation..."
  if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
  fi
  
  if ! docker ps &> /dev/null; then
    log_error "Docker daemon is not running. Start Docker and try again."
    exit 1
  fi
  
  log_success "Docker is ready"
}

# Verify Dockerfiles exist
verify_dockerfiles() {
  log_info "Verifying Dockerfiles..."
  
  if [[ $BUILD_API == true ]]; then
    if [[ ! -f "homework2/Dockerfile.api" ]]; then
      log_error "homework2/Dockerfile.api not found"
      exit 1
    fi
    log_success "Found homework2/Dockerfile.api"
  fi
  
  if [[ $BUILD_WEB == true ]]; then
    if [[ ! -f "homework2/Dockerfile.web" ]]; then
      log_error "homework2/Dockerfile.web not found"
      exit 1
    fi
    log_success "Found homework2/Dockerfile.web"
  fi
}

# Login to registry
login_to_registry() {
  if [[ $PUSH != true ]]; then
    log_info "Skipping login (not pushing)"
    return 0
  fi
  
  log_info "Logging in to $REGISTRY..."
  
  if [[ -z "$REGISTRY_USER" ]]; then
    read -p "Registry username: " REGISTRY_USER
  fi
  
  if [[ -z "$REGISTRY_PASS" ]]; then
    read -sp "Registry password/token: " REGISTRY_PASS
    echo ""
  fi
  
  if echo "$REGISTRY_PASS" | docker login "$REGISTRY" -u "$REGISTRY_USER" --password-stdin 2>/dev/null; then
    log_success "Successfully logged in to $REGISTRY"
  else
    log_error "Failed to login to $REGISTRY"
    exit 1
  fi
}

# Get repository owner for image name
REPO_OWNER=$(get_repo_owner)
if [[ -z "$REPO_OWNER" ]]; then
  read -p "Enter repository owner/username: " REPO_OWNER
fi

# Build image function
build_image() {
  local dockerfile=$1
  local image_name=$2
  
  local full_image="${REGISTRY}/${REPO_OWNER}/${image_name}:${TAG}"
  
  log_info "Building $full_image..."
  
  if [[ $BUILDX == true ]]; then
    log_info "Using Docker Buildx (platforms: $PLATFORMS)"
    
    # Buildx requires --push for multi-platform builds
    if [[ "$PLATFORMS" == *","* ]] && [[ $PUSH != true ]]; then
      log_warning "Multi-platform builds require --push. Enabling push..."
      PUSH=true
    fi
    
    if [[ $PUSH == true ]]; then
      # Multi-platform or pushing: use --push
      if docker buildx build \
          -f "$dockerfile" \
          -t "$full_image" \
          --platform "$PLATFORMS" \
          --push \
          . 2>&1 | grep -v "^#"; then
        log_success "Built and pushed $full_image"
      else
        log_error "Failed to build/push $full_image"
        return 1
      fi
    else
      # Single platform, not pushing: use --load
      if docker buildx build \
          -f "$dockerfile" \
          -t "$full_image" \
          --platform "$PLATFORMS" \
          --load \
          . 2>&1 | grep -v "^#"; then
        log_success "Built $full_image"
      else
        log_error "Failed to build $full_image"
        return 1
      fi
    fi
  else
    # Use standard docker build
    if docker build \
        -f "$dockerfile" \
        -t "$full_image" \
        . 2>&1 | grep -E "(Step|Digest|^sha256|Successfully|error|Error)"; then
      log_success "Built $full_image"
    else
      log_error "Failed to build $full_image"
      return 1
    fi
    
    if [[ $PUSH == true ]]; then
      log_info "Pushing $full_image..."
      if docker push "$full_image" 2>&1 | grep -E "(Pushed|digest|error|Error)"; then
        log_success "Pushed $full_image"
      else
        log_error "Failed to push $full_image"
        return 1
      fi
    fi
  fi
}

# Main execution
main() {
  echo ""
  log_info "Docker Build Script"
  echo ""
  
  # Verify prerequisites
  verify_docker
  verify_dockerfiles
  
  # Show configuration
  echo ""
  log_info "Configuration:"
  echo "  Registry: $REGISTRY"
  echo "  Owner: $REPO_OWNER"
  echo "  Tag: $TAG"
  echo "  Push: $PUSH"
  [[ $BUILDX == true ]] && echo "  Buildx: enabled (platforms: $PLATFORMS)"
  [[ $BUILD_API == true ]] && echo "  Building: dxcluster-api"
  [[ $BUILD_WEB == true ]] && echo "  Building: dxcluster-web"
  echo ""
  
  # Login if pushing
  if [[ $PUSH == true ]]; then
    login_to_registry
    echo ""
  fi
  
  # Build images
  build_failed=0
  
  if [[ $BUILD_API == true ]]; then
    if ! build_image "homework2/Dockerfile.api" "dxcluster-api"; then
      build_failed=1
    fi
  fi
  
  if [[ $BUILD_WEB == true ]]; then
    if ! build_image "homework2/Dockerfile.web" "dxcluster-web"; then
      build_failed=1
    fi
  fi
  
  echo ""
  
  if [[ $build_failed -eq 0 ]]; then
    log_success "Build completed successfully!"
    echo ""
    echo "Image(s) available at:"
    if [[ $BUILD_API == true ]]; then
      echo "  ${REGISTRY}/${REPO_OWNER}/dxcluster-api:${TAG}"
    fi
    if [[ $BUILD_WEB == true ]]; then
      echo "  ${REGISTRY}/${REPO_OWNER}/dxcluster-web:${TAG}"
    fi
    echo ""
    
    if [[ $PUSH != true ]]; then
      log_info "Images built locally but not pushed. Use '-p' to push."
    fi
  else
    log_error "Build failed!"
    exit 1
  fi
}

# Run main function
main

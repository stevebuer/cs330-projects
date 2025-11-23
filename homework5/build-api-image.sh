#!/bin/bash

# Build and push DX Cluster API container to ghcr.io
# Usage: ./build-api-image.sh [TAG]

set -e

# Configuration
REGISTRY="ghcr.io"
OWNER="stevebuer"
REPO_NAME="cs330-projects"
IMAGE_NAME="dx-cluster-api"
TAG="${1:-latest}"

# Full image name
FULL_IMAGE="${REGISTRY}/${OWNER}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== DX Cluster API Container Build ===${NC}"
echo -e "${YELLOW}Building: ${FULL_IMAGE}${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

# Check if we have credentials
if [ ! -f "$HOME/.docker/config.json" ]; then
    echo -e "${YELLOW}Warning: Docker credentials not found at $HOME/.docker/config.json${NC}"
    echo -e "${YELLOW}You may need to run: docker login ghcr.io${NC}"
fi

# Build the image
echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
if docker build \
    -f Dockerfile.api \
    -t "${FULL_IMAGE}" \
    -t "${REGISTRY}/${OWNER}/${REPO_NAME}/${IMAGE_NAME}:latest" \
    .; then
    echo -e "${GREEN}✓ Image built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build image${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Pushing image to registry...${NC}"

# Push the specific tag
if docker push "${FULL_IMAGE}"; then
    echo -e "${GREEN}✓ Pushed ${FULL_IMAGE}${NC}"
else
    echo -e "${RED}✗ Failed to push ${FULL_IMAGE}${NC}"
    echo -e "${YELLOW}Make sure you are logged in: docker login ghcr.io${NC}"
    exit 1
fi

# Also push latest tag
if [ "${TAG}" != "latest" ]; then
    echo ""
    echo -e "${YELLOW}Pushing 'latest' tag...${NC}"
    if docker push "${REGISTRY}/${OWNER}/${REPO_NAME}/${IMAGE_NAME}:latest"; then
        echo -e "${GREEN}✓ Pushed latest tag${NC}"
    else
        echo -e "${RED}✗ Failed to push latest tag${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}=== Build Complete ===${NC}"
echo ""
echo "Image pushed successfully!"
echo "Image: ${FULL_IMAGE}"
echo ""
echo "To use this image:"
echo "  docker pull ${FULL_IMAGE}"
echo ""
echo "To run the container:"
echo "  docker run -p 8080:8080 \\"
echo "    -e PGHOST=your-host \\"
echo "    -e PGDATABASE=your-db \\"
echo "    -e PGUSER=your-user \\"
echo "    -e PGPASSWORD=your-pass \\"
echo "    ${FULL_IMAGE}"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose pull"
echo "  docker-compose up"

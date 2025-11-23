#!/bin/bash

# Build script for DX Cluster Scraper Debian package
# Builds dxcluster-scraper package with Prometheus metrics support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="dxcluster-scraper"
PACKAGE_DIR="$SCRIPT_DIR/$PACKAGE_NAME"
VERSION="2.0.0"

echo -e "${BLUE}=== DX Cluster Scraper Package Builder ===${NC}"
echo -e "${YELLOW}Package: ${PACKAGE_NAME}${NC}"
echo -e "${YELLOW}Version: ${VERSION}${NC}"
echo -e "${YELLOW}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Check if package directory exists
if [ ! -d "$PACKAGE_DIR" ]; then
    echo -e "${RED}Error: Package directory not found: ${PACKAGE_DIR}${NC}"
    exit 1
fi

# Check if debian directory exists
if [ ! -d "$PACKAGE_DIR/debian" ]; then
    echo -e "${RED}Error: Debian directory not found: ${PACKAGE_DIR}/debian${NC}"
    exit 1
fi

# Check dependencies
echo -e "${YELLOW}Checking build dependencies...${NC}"
MISSING_DEPS=()

if ! command -v debhelper &> /dev/null; then
    MISSING_DEPS+=("debhelper")
fi

if ! command -v dpkg-dev &> /dev/null; then
    MISSING_DEPS+=("dpkg-dev")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing dependencies: ${MISSING_DEPS[*]}${NC}"
    sudo apt-get update
    sudo apt-get install -y "${MISSING_DEPS[@]}"
fi

echo -e "${GREEN}✓ Dependencies check complete${NC}"
echo ""

# Navigate to package directory
cd "$PACKAGE_DIR"

echo -e "${YELLOW}Building package...${NC}"
echo ""

# Run debuild
if debuild -us -uc -b; then
    echo ""
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
    
    # List the built package
    cd "$SCRIPT_DIR/.."
    if [ -f "${PACKAGE_NAME}_${VERSION}-1_all.deb" ]; then
        echo -e "${GREEN}Package created:${NC}"
        ls -lh "${PACKAGE_NAME}_${VERSION}-1_all.deb"
        echo ""
        echo "To install the package:"
        echo "  sudo dpkg -i ${PACKAGE_NAME}_${VERSION}-1_all.deb"
        echo "  sudo apt-get install -f  # If you need to resolve dependencies"
        echo ""
        echo "After installation:"
        echo "  1. Configure: sudo nano /etc/dxcluster/dxcluster.env"
        echo "  2. Enable:    sudo systemctl enable dx-scraper"
        echo "  3. Start:     sudo systemctl start dx-scraper"
        echo "  4. Monitor:   curl http://localhost:8000/metrics"
    else
        echo -e "${YELLOW}Package not found in ${SCRIPT_DIR}/../${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

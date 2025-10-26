#!/bin/bash

# Build script for DX Cluster Debian packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGES_DIR="$SCRIPT_DIR/packages"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building DX Cluster Debian Packages${NC}"

# Check if dpkg-deb is available
if ! command -v dpkg-deb &> /dev/null; then
    echo -e "${RED}Error: dpkg-deb not found. Install dpkg-dev package.${NC}"
    exit 1
fi

# Check if debhelper is available
if ! command -v dh &> /dev/null; then
    echo -e "${RED}Error: debhelper not found. Install debhelper package.${NC}"
    exit 1
fi

build_package() {
    local package_name=$1
    local package_dir="$PACKAGES_DIR/$package_name"
    
    echo -e "${YELLOW}Building package: $package_name${NC}"
    
    if [ ! -d "$package_dir" ]; then
        echo -e "${RED}Error: Package directory not found: $package_dir${NC}"
        return 1
    fi
    
    cd "$package_dir"
    
    # Make sure postinst, prerm, etc. are executable
    chmod +x debian/postinst debian/prerm 2>/dev/null || true
    chmod +x debian/postrm 2>/dev/null || true
    
    # Clean previous build
    if [ -d "debian/tmp" ]; then
        rm -rf debian/tmp
    fi
    
    # Build the package
    if dpkg-buildpackage -us -uc -b; then
        echo -e "${GREEN}✓ Successfully built $package_name${NC}"
        
        # Move the .deb file to packages directory
        if ls ../*.deb 1> /dev/null 2>&1; then
            mv ../*.deb ../
            echo -e "${GREEN}Package files available in $PACKAGES_DIR/${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}✗ Failed to build $package_name${NC}"
        return 1
    fi
}

# Create output directory
mkdir -p "$PACKAGES_DIR"

# Build database package
if build_package "dxcluster-database"; then
    DATABASE_SUCCESS=true
else
    DATABASE_SUCCESS=false
fi

echo ""

# Build scraper package
if build_package "dxcluster-scraper"; then
    SCRAPER_SUCCESS=true
else
    SCRAPER_SUCCESS=false
fi

echo ""
echo -e "${YELLOW}Build Summary:${NC}"
echo -e "Database package: $(if $DATABASE_SUCCESS; then echo -e "${GREEN}SUCCESS${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"
echo -e "Scraper package:  $(if $SCRAPER_SUCCESS; then echo -e "${GREEN}SUCCESS${NC}"; else echo -e "${RED}FAILED${NC}"; fi)"

if $DATABASE_SUCCESS && $SCRAPER_SUCCESS; then
    echo ""
    echo -e "${GREEN}All packages built successfully!${NC}"
    echo ""
    echo "Installation commands:"
    echo "  sudo dpkg -i $PACKAGES_DIR/dxcluster-database_*.deb"
    echo "  sudo dpkg -i $PACKAGES_DIR/dxcluster-scraper_*.deb"
    echo ""
    echo "To install dependencies:"
    echo "  sudo apt-get install -f"
    exit 0
else
    echo ""
    echo -e "${RED}Some packages failed to build. Check the errors above.${NC}"
    exit 1
fi
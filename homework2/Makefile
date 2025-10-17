# Makefile for DX Cluster Debian Packages

PACKAGES_DIR = packages
DATABASE_PKG = $(PACKAGES_DIR)/dxcluster-database
SCRAPER_PKG = $(PACKAGES_DIR)/dxcluster-scraper

.PHONY: all clean install database scraper build-database build-scraper install-deps

all: build-database build-scraper

# Build both packages
build: all

# Build database package
build-database:
	@echo "Building dxcluster-database package..."
	cd $(DATABASE_PKG) && dpkg-buildpackage -us -uc -b
	@mv $(PACKAGES_DIR)/*.deb $(PACKAGES_DIR)/ 2>/dev/null || true

# Build scraper package  
build-scraper:
	@echo "Building dxcluster-scraper package..."
	cd $(SCRAPER_PKG) && dpkg-buildpackage -us -uc -b
	@mv $(PACKAGES_DIR)/*.deb $(PACKAGES_DIR)/ 2>/dev/null || true

# Install both packages
install:
	@echo "Installing DX Cluster packages..."
	sudo dpkg -i $(PACKAGES_DIR)/dxcluster-database_*.deb || true
	sudo dpkg -i $(PACKAGES_DIR)/dxcluster-scraper_*.deb || true
	sudo apt-get install -f

# Install database package only
install-database:
	@echo "Installing dxcluster-database..."
	sudo dpkg -i $(PACKAGES_DIR)/dxcluster-database_*.deb || true
	sudo apt-get install -f

# Install scraper package only
install-scraper:
	@echo "Installing dxcluster-scraper..."
	sudo dpkg -i $(PACKAGES_DIR)/dxcluster-scraper_*.deb || true
	sudo apt-get install -f

# Install build dependencies
install-deps:
	@echo "Installing build dependencies..."
	sudo apt-get update
	sudo apt-get install -y debhelper dpkg-dev build-essential

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(PACKAGES_DIR)/*.deb
	rm -f $(PACKAGES_DIR)/*.buildinfo
	rm -f $(PACKAGES_DIR)/*.changes
	rm -rf $(DATABASE_PKG)/debian/tmp
	rm -rf $(DATABASE_PKG)/debian/.debhelper
	rm -rf $(DATABASE_PKG)/debian/dxcluster-database
	rm -rf $(SCRAPER_PKG)/debian/tmp
	rm -rf $(SCRAPER_PKG)/debian/.debhelper  
	rm -rf $(SCRAPER_PKG)/debian/dxcluster-scraper

# Show package info
info:
	@echo "DX Cluster Packages:"
	@echo "  Database: $(DATABASE_PKG)"
	@echo "  Scraper:  $(SCRAPER_PKG)"
	@echo ""
	@echo "Available targets:"
	@echo "  all         - Build both packages"
	@echo "  build       - Build both packages (alias for all)"
	@echo "  database    - Build database package only"  
	@echo "  scraper     - Build scraper package only"
	@echo "  install     - Install both packages"
	@echo "  install-deps - Install build dependencies"
	@echo "  clean       - Clean build artifacts"
	@echo "  info        - Show this help"

# Aliases
database: build-database
scraper: build-scraper
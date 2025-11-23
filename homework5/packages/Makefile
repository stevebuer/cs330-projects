.PHONY: all build build-scraper clean install install-deps help info

# Package configuration
PACKAGE_NAME := dxcluster-scraper
VERSION := 2.0.0
ARCH := all

help:
	@echo "DX Cluster Scraper Package Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Build the scraper package"
	@echo "  build            - Build the scraper package"
	@echo "  clean            - Remove build artifacts"
	@echo "  install-deps     - Install build dependencies"
	@echo "  help             - Show this help message"
	@echo "  info             - Show package information"
	@echo ""

info:
	@echo "Package Information"
	@echo "==================="
	@echo "Name:     $(PACKAGE_NAME)"
	@echo "Version:  $(VERSION)"
	@echo "Arch:     $(ARCH)"
	@echo ""
	@echo "Features:"
	@echo "  - DX Cluster monitoring with socket connections"
	@echo "  - PostgreSQL data storage"
	@echo "  - Prometheus metrics export (port 8000)"
	@echo "  - Systemd service integration"
	@echo "  - Real-time spot parsing and filtering"
	@echo ""

all: build

build: build-scraper

build-scraper:
	@echo "Building $(PACKAGE_NAME) package..."
	@echo "Version: $(VERSION)"
	@if [ ! -d "$(PACKAGE_NAME)" ]; then \
		echo "Error: $(PACKAGE_NAME) directory not found"; \
		exit 1; \
	fi
	@cd $(PACKAGE_NAME) && debuild -us -uc -b
	@echo "Build complete!"
	@echo ""
	@ls -lh ../$(PACKAGE_NAME)_$(VERSION)-1_$(ARCH).deb 2>/dev/null || echo "Package build in progress..."

install-deps:
	@echo "Installing build dependencies..."
	@command -v debhelper >/dev/null 2>&1 || (echo "Installing debhelper..." && sudo apt-get install -y debhelper)
	@command -v dpkg-dev >/dev/null 2>&1 || (echo "Installing dpkg-dev..." && sudo apt-get install -y dpkg-dev)
	@command -v python3 >/dev/null 2>&1 || (echo "Installing python3..." && sudo apt-get install -y python3)
	@echo "Build dependencies installed!"

clean:
	@echo "Cleaning build artifacts..."
	@if [ -d "$(PACKAGE_NAME)" ]; then \
		cd $(PACKAGE_NAME) && debclean 2>/dev/null || true; \
	fi
	@rm -f ../$(PACKAGE_NAME)_*
	@echo "Clean complete!"

.DEFAULT_GOAL := help

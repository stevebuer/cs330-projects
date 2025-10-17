#!/bin/bash

# Production Deployment Script for DX Cluster
# This script handles deployment of pre-built Docker images to production

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_NAME="dx-cluster"
PRODUCTION_COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in production environment
check_production_environment() {
    log_info "Checking production environment..."
    
    if [[ -f "/etc/debian_version" ]]; then
        DEBIAN_VERSION=$(cat /etc/debian_version)
        log_info "Detected Debian version: $DEBIAN_VERSION"
    fi
    
    # Check Docker version
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_info "Docker version: $DOCKER_VERSION"
    else
        log_error "Docker is not installed!"
        exit 1
    fi
    
    # Check Docker Compose version
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        log_info "Docker Compose version: $COMPOSE_VERSION"
    else
        log_error "Docker Compose is not installed!"
        exit 1
    fi
}

# Export images from development machine
export_images() {
    log_info "Exporting Docker images..."
    
    # Create exports directory
    mkdir -p exports
    
    # Export API image
    if docker image inspect dx-cluster-api:latest &> /dev/null; then
        log_info "Exporting dx-cluster-api:latest..."
        docker save dx-cluster-api:latest | gzip > exports/dx-cluster-api-latest.tar.gz
        log_success "API image exported to exports/dx-cluster-api-latest.tar.gz"
    else
        log_error "dx-cluster-api:latest image not found. Build it first with: docker-compose build dx-api"
        exit 1
    fi
    
    # Export Web image
    if docker image inspect dx-cluster-web:latest &> /dev/null; then
        log_info "Exporting dx-cluster-web:latest..."
        docker save dx-cluster-web:latest | gzip > exports/dx-cluster-web-latest.tar.gz
        log_success "Web image exported to exports/dx-cluster-web-latest.tar.gz"
    else
        log_error "dx-cluster-web:latest image not found. Build it first with: docker-compose build dx-web"
        exit 1
    fi
    
    log_success "Images exported successfully!"
    log_info "Transfer these files to your production server:"
    log_info "- exports/dx-cluster-api-latest.tar.gz"
    log_info "- exports/dx-cluster-web-latest.tar.gz"
}

# Import images on production machine
import_images() {
    log_info "Importing Docker images..."
    
    # Import API image
    if [[ -f "exports/dx-cluster-api-latest.tar.gz" ]]; then
        log_info "Importing dx-cluster-api:latest..."
        docker load < exports/dx-cluster-api-latest.tar.gz
        log_success "API image imported successfully"
    else
        log_error "API image file not found: exports/dx-cluster-api-latest.tar.gz"
        exit 1
    fi
    
    # Import Web image
    if [[ -f "exports/dx-cluster-web-latest.tar.gz" ]]; then
        log_info "Importing dx-cluster-web:latest..."
        docker load < exports/dx-cluster-web-latest.tar.gz
        log_success "Web image imported successfully"
    else
        log_error "Web image file not found: exports/dx-cluster-web-latest.tar.gz"
        exit 1
    fi
    
    log_success "All images imported successfully!"
}

# Setup production environment
setup_production() {
    log_info "Setting up production environment..."
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.production.template" ]]; then
            log_info "Copying .env.production.template to .env"
            cp .env.production.template .env
            log_warning "Please edit .env file with your production database credentials"
        else
            log_warning "No .env file found. Please create one with your database credentials"
        fi
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    
    log_success "Production environment setup complete"
}

# Deploy services using production compose file
deploy() {
    log_info "Deploying services using $PRODUCTION_COMPOSE_FILE..."
    
    # Stop any running services
    if docker-compose -f "$PRODUCTION_COMPOSE_FILE" ps | grep -q "Up"; then
        log_info "Stopping existing services..."
        docker-compose -f "$PRODUCTION_COMPOSE_FILE" down
    fi
    
    # Start services
    log_info "Starting production services..."
    docker-compose -f "$PRODUCTION_COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Check service status
    docker-compose -f "$PRODUCTION_COMPOSE_FILE" ps
    
    log_success "Deployment complete!"
    log_info "Services are available at:"
    log_info "- API: http://localhost:8080"
    log_info "- Dashboard: http://localhost:8050"
}

# Check service health
health_check() {
    log_info "Performing health checks..."
    
    # Check API health
    if curl -f -s http://localhost:8080/api/health > /dev/null; then
        log_success "API service is healthy"
    else
        log_error "API service health check failed"
    fi
    
    # Check if containers are running
    if docker-compose -f "$PRODUCTION_COMPOSE_FILE" ps | grep -q "Up"; then
        log_success "All containers are running"
    else
        log_warning "Some containers may not be running properly"
        docker-compose -f "$PRODUCTION_COMPOSE_FILE" ps
    fi
}

# Show logs
show_logs() {
    SERVICE="${1:-}"
    if [[ -n "$SERVICE" ]]; then
        docker-compose -f "$PRODUCTION_COMPOSE_FILE" logs -f "$SERVICE"
    else
        docker-compose -f "$PRODUCTION_COMPOSE_FILE" logs -f
    fi
}

# Stop services
stop_services() {
    log_info "Stopping production services..."
    docker-compose -f "$PRODUCTION_COMPOSE_FILE" down
    log_success "Services stopped"
}

# Clean up
cleanup() {
    log_info "Cleaning up Docker resources..."
    docker system prune -f
    log_success "Cleanup complete"
}

# Main function
main() {
    case "${1:-}" in
        "check")
            check_production_environment
            ;;
        "export")
            export_images
            ;;
        "import")
            import_images
            ;;
        "setup")
            setup_production
            ;;
        "deploy")
            deploy
            ;;
        "health")
            health_check
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "start-api")
            log_info "Starting API service only..."
            docker-compose -f "$PRODUCTION_COMPOSE_FILE" up -d dx-api postgres-check
            log_success "API service started"
            ;;
        "start-web")
            log_info "Starting Web service only..."
            docker-compose -f "$PRODUCTION_COMPOSE_FILE" up -d dx-web postgres-check
            log_success "Web service started"
            ;;
        "stop")
            stop_services
            ;;
        "cleanup")
            cleanup
            ;;
        "full-deploy")
            check_production_environment
            import_images
            setup_production
            deploy
            health_check
            ;;
        *)
            echo "Production Deployment Script for DX Cluster"
            echo ""
            echo "Usage: $0 {command}"
            echo ""
            echo "Commands:"
            echo "  check       - Check production environment requirements"
            echo "  export      - Export Docker images for transfer (run on dev machine)"
            echo "  import      - Import Docker images (run on production server)"
            echo "  setup       - Setup production environment"
            echo "  deploy      - Deploy services using pre-built images"
            echo "  start-api   - Start only the API service (with database check)"
            echo "  start-web   - Start only the Web service (with database check)"
            echo "  health      - Check service health"
            echo "  logs [svc]  - Show logs (all services or specific service)"
            echo "  stop        - Stop all services"
            echo "  cleanup     - Clean up Docker resources"
            echo "  full-deploy - Complete deployment process (import + setup + deploy + health)"
            echo ""
            echo "Example deployment workflow:"
            echo "  1. On dev machine: $0 export"
            echo "  2. Transfer exports/ directory to production server"
            echo "  3. On production: $0 full-deploy"
            ;;
    esac
}

# Change to script directory
cd "$SCRIPT_DIR"

# Run main function with all arguments
main "$@"
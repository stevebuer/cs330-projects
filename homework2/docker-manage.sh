#!/bin/bash
#
# Docker Management Script for DX Cluster Services
# Usage: ./docker-manage.sh [command]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if docker and docker-compose are available
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found, creating from template..."
        cp .env.docker .env
        print_warning "Please edit .env file with your database credentials"
        return 1
    fi
    return 0
}

# Build images
build() {
    print_header "Building Docker Images"
    docker-compose build --no-cache
    print_status "Build completed successfully"
}

# Start services
start() {
    print_header "Starting DX Cluster Services"
    setup_env || {
        print_error "Please configure .env file before starting services"
        return 1
    }
    
    docker-compose up -d
    print_status "Services started successfully"
    print_status "API available at: http://localhost:8080"
    print_status "Dashboard available at: http://localhost:8050"
}

# Start with proxy
start_with_proxy() {
    print_header "Starting DX Cluster Services with Traefik Proxy"
    setup_env || {
        print_error "Please configure .env file before starting services"
        return 1
    }
    
    docker-compose --profile proxy up -d
    print_status "Services started with proxy"
    print_status "API available at: http://api.dx.local (add to /etc/hosts)"
    print_status "Dashboard available at: http://dashboard.dx.local"
    print_status "Traefik dashboard: http://localhost:8888"
}

# Stop services
stop() {
    print_header "Stopping DX Cluster Services"
    docker-compose down
    print_status "Services stopped successfully"
}

# Restart services
restart() {
    print_header "Restarting DX Cluster Services"
    stop
    start
}

# Show logs
logs() {
    service=${2:-""}
    if [ -n "$service" ]; then
        print_header "Showing logs for $service"
        docker-compose logs -f "$service"
    else
        print_header "Showing logs for all services"
        docker-compose logs -f
    fi
}

# Show status
status() {
    print_header "Service Status"
    docker-compose ps
    echo
    print_header "Resource Usage"
    docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || print_warning "No running containers"
}

# Development mode (with live reload)
dev() {
    print_header "Starting Development Mode"
    setup_env || {
        print_error "Please configure .env file before starting services"
        return 1
    }
    
    # Override for development
    export FLASK_ENV=development
    export DASH_ENV=development
    
    docker-compose up --build
}

# Clean up
clean() {
    print_header "Cleaning Up Docker Resources"
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_status "Cleanup completed"
}

# Database shell
db_shell() {
    print_header "Opening Database Shell"
    if [ ! -f .env ]; then
        print_error ".env file not found"
        return 1
    fi
    
    source .env
    docker run --rm -it --network homework2_dx-network postgres:15-alpine \
        psql -h "$PGHOST" -d "$PGDATABASE" -U "$PGUSER"
}

# Show help
show_help() {
    echo "DX Cluster Docker Management Script"
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  build              Build Docker images"
    echo "  start              Start all services"
    echo "  start-proxy        Start services with Traefik proxy"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  logs [service]     Show logs (optionally for specific service)"
    echo "  status             Show service status and resource usage"
    echo "  dev                Start in development mode"
    echo "  clean              Stop services and clean up resources"
    echo "  db-shell           Open PostgreSQL shell"
    echo "  help               Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start           # Start all services"
    echo "  $0 logs dx-api     # Show API logs"
    echo "  $0 dev             # Development mode with live reload"
}

# Main script logic
main() {
    check_dependencies
    
    case "${1:-help}" in
        build)
            build
            ;;
        start)
            start
            ;;
        start-proxy)
            start_with_proxy
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs "$@"
            ;;
        status)
            status
            ;;
        dev)
            dev
            ;;
        clean)
            clean
            ;;
        db-shell)
            db_shell
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
#!/bin/bash

# Resume Relevance System - Local Docker Deployment Script
# This script sets up and runs the Resume Relevance System using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
COMPOSE_PROFILES="development"

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Resume Relevance System - Docker Deployment Script

Usage: $0 [OPTION]

Options:
    -h, --help          Show this help message
    -p, --production    Deploy in production mode
    -d, --development   Deploy in development mode (default)
    -m, --monitoring    Enable monitoring stack (Prometheus, Grafana)
    -s, --stop          Stop all services
    -c, --clean         Clean up all containers and volumes
    -l, --logs          Show logs from all services
    -r, --restart       Restart all services
    --build             Force rebuild of images

Examples:
    $0                  # Start in development mode
    $0 -p              # Start in production mode
    $0 -m              # Start with monitoring enabled
    $0 -s              # Stop all services
    $0 -c              # Clean up everything

EOF
}

# Check requirements
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Create environment file if it doesn't exist
setup_environment() {
    if [[ ! -f "$ENV_FILE" ]]; then
        print_status "Creating environment file..."
        cat > "$ENV_FILE" << EOF
# Resume Relevance System Environment Configuration

# Security
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || echo "change-this-secret-key-in-production")

# Database
DB_PASSWORD=$(openssl rand -base64 16 2>/dev/null || echo "password")

# Email Configuration (Optional)
EMAIL_ENABLED=false
EMAIL_PROVIDER=smtp
SMTP_SERVER=
SMTP_USERNAME=
SMTP_PASSWORD=

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=1

# File Upload Settings
MAX_CONTENT_LENGTH=16777216

# Monitoring (Optional)
ENABLE_METRICS=false
EOF
        print_success "Environment file created at $ENV_FILE"
        print_warning "Please review and update $ENV_FILE with your configuration"
    else
        print_status "Environment file exists"
    fi
}

# Build images
build_images() {
    print_status "Building Docker images..."
    
    if [[ "$FORCE_BUILD" == "true" ]]; then
        docker-compose build --no-cache
    else
        docker-compose build
    fi
    
    print_success "Images built successfully"
}

# Start services
start_services() {
    print_status "Starting services with profile: $COMPOSE_PROFILES"
    
    if [[ "$COMPOSE_PROFILES" == "production" ]]; then
        docker-compose --profile production up -d
    elif [[ "$COMPOSE_PROFILES" == "monitoring" ]]; then
        docker-compose --profile development --profile monitoring up -d
    else
        docker-compose up -d
    fi
    
    print_success "Services started successfully"
}

# Stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "Services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up containers, networks, and volumes..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Show logs
show_logs() {
    print_status "Showing logs from all services..."
    docker-compose logs -f
}

# Restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_success "Services restarted"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    until docker-compose exec db pg_isready -U postgres; do
        sleep 1
    done
    
    # Wait for application
    print_status "Waiting for application..."
    until curl -f http://localhost:5000/health &> /dev/null; do
        sleep 1
    done
    
    print_success "All services are ready"
}

# Show status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo
    print_status "Application URLs:"
    echo "  Main Application: http://localhost:5000"
    echo "  Health Check:     http://localhost:5000/health"
    
    if docker-compose ps | grep -q pgadmin; then
        echo "  pgAdmin:          http://localhost:5050"
    fi
    
    if docker-compose ps | grep -q grafana; then
        echo "  Grafana:          http://localhost:3000"
        echo "  Prometheus:       http://localhost:9090"
    fi
}

# Main execution
main() {
    # Default values
    ACTION="start"
    FORCE_BUILD="false"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -p|--production)
                COMPOSE_PROFILES="production"
                shift
                ;;
            -d|--development)
                COMPOSE_PROFILES="development"
                shift
                ;;
            -m|--monitoring)
                COMPOSE_PROFILES="monitoring"
                shift
                ;;
            -s|--stop)
                ACTION="stop"
                shift
                ;;
            -c|--clean)
                ACTION="clean"
                shift
                ;;
            -l|--logs)
                ACTION="logs"
                shift
                ;;
            -r|--restart)
                ACTION="restart"
                shift
                ;;
            --build)
                FORCE_BUILD="true"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Check if we're in the right directory
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_error "docker-compose.yml not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Execute action
    case $ACTION in
        start)
            check_requirements
            setup_environment
            build_images
            start_services
            wait_for_services
            show_status
            ;;
        stop)
            stop_services
            ;;
        clean)
            cleanup
            ;;
        logs)
            show_logs
            ;;
        restart)
            restart_services
            ;;
    esac
}

# Run main function
main "$@"
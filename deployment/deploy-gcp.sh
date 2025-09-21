#!/bin/bash

# Resume Relevance System - Google Cloud Platform Deployment Script
# This script deploys the Resume Relevance System to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-resume-relevance-project}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-resume-relevance}"
IMAGE_NAME="${IMAGE_NAME:-resume-relevance}"

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
Resume Relevance System - Google Cloud Platform Deployment Script

Usage: $0 [OPTION]

Options:
    -h, --help          Show this help message
    -i, --init          Initialize GCP project and services
    -b, --build         Build and push Docker image to GCR
    -d, --deploy        Deploy to Cloud Run
    -s, --status        Show deployment status
    -l, --logs          Show application logs
    -c, --cleanup       Delete all GCP resources
    --project ID        GCP project ID
    --region REGION     GCP region (default: us-central1)
    --service NAME      Cloud Run service name

Environment Variables:
    PROJECT_ID          GCP project ID
    REGION              GCP region
    SERVICE_NAME        Cloud Run service name
    IMAGE_NAME          Docker image name

Examples:
    $0 -i              # Initialize GCP project
    $0 -b              # Build and push image
    $0 -d              # Deploy to Cloud Run
    $0 -s              # Show deployment status

EOF
}

# Check requirements
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 &> /dev/null; then
        print_error "Please authenticate with Google Cloud: gcloud auth login"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Initialize GCP project
init_project() {
    print_status "Initializing GCP project..."
    
    # Set project
    gcloud config set project "$PROJECT_ID"
    
    # Enable required APIs
    print_status "Enabling required APIs..."
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        sql-component.googleapis.com \
        secretmanager.googleapis.com \
        logging.googleapis.com \
        monitoring.googleapis.com
    
    print_success "GCP project initialized"
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker
    
    # Build image using Cloud Build
    gcloud builds submit \
        --tag "gcr.io/${PROJECT_ID}/${IMAGE_NAME}" \
        --region="$REGION" \
        .
    
    print_success "Image built and pushed to gcr.io/${PROJECT_ID}/${IMAGE_NAME}"
}

# Create Cloud SQL instance (optional)
create_database() {
    print_status "Creating Cloud SQL PostgreSQL instance..."
    
    DB_INSTANCE_NAME="resume-relevance-db"
    DB_PASSWORD=$(openssl rand -base64 32 2>/dev/null || echo "change-this-password")
    
    # Create Cloud SQL instance
    gcloud sql instances create "$DB_INSTANCE_NAME" \
        --database-version=POSTGRES_13 \
        --tier=db-f1-micro \
        --region="$REGION" \
        --storage-type=SSD \
        --storage-size=10GB \
        --backup-start-time=02:00 \
        --enable-bin-log \
        --maintenance-release-channel=production \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=02
    
    # Set root password
    gcloud sql users set-password postgres \
        --instance="$DB_INSTANCE_NAME" \
        --password="$DB_PASSWORD"
    
    # Create database
    gcloud sql databases create resume_relevance \
        --instance="$DB_INSTANCE_NAME"
    
    # Store database connection info
    cat > .gcp_db_config << EOF
DB_INSTANCE_NAME=$DB_INSTANCE_NAME
DB_PASSWORD=$DB_PASSWORD
DB_CONNECTION_NAME=${PROJECT_ID}:${REGION}:${DB_INSTANCE_NAME}
EOF
    
    print_success "Cloud SQL instance created"
}

# Create secrets in Secret Manager
create_secrets() {
    print_status "Creating secrets in Secret Manager..."
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || echo "change-this-secret-key")
    
    # Create secrets
    echo -n "$SECRET_KEY" | gcloud secrets create app-secret-key --data-file=-
    
    if [[ -f .gcp_db_config ]]; then
        source .gcp_db_config
        echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=-
    fi
    
    print_success "Secrets created in Secret Manager"
}

# Deploy to Cloud Run
deploy_service() {
    print_status "Deploying to Cloud Run..."
    
    # Prepare environment variables
    ENV_VARS="FLASK_ENV=production,DATABASE_TYPE=sqlite"
    
    # Add database configuration if available
    if [[ -f .gcp_db_config ]]; then
        source .gcp_db_config
        ENV_VARS="${ENV_VARS},DATABASE_TYPE=postgresql"
    fi
    
    # Deploy to Cloud Run
    gcloud run deploy "$SERVICE_NAME" \
        --image="gcr.io/${PROJECT_ID}/${IMAGE_NAME}" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --max-instances=10 \
        --timeout=300 \
        --port=5000 \
        --set-env-vars="$ENV_VARS" \
        --set-secrets="SECRET_KEY=app-secret-key:latest" \
        --concurrency=80
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)")
    
    print_success "Service deployed successfully"
    print_success "Service URL: $SERVICE_URL"
    
    # Save service URL
    echo "SERVICE_URL=$SERVICE_URL" > .gcp_service_url
}

# Set up custom domain (optional)
setup_domain() {
    DOMAIN_NAME="$1"
    
    if [[ -z "$DOMAIN_NAME" ]]; then
        print_error "Domain name required"
        return 1
    fi
    
    print_status "Setting up custom domain: $DOMAIN_NAME"
    
    # Create domain mapping
    gcloud run domain-mappings create \
        --service="$SERVICE_NAME" \
        --domain="$DOMAIN_NAME" \
        --region="$REGION"
    
    print_success "Domain mapping created"
    print_status "Please configure your DNS to point $DOMAIN_NAME to ghs.googlehosted.com"
}

# Set up monitoring and logging
setup_monitoring() {
    print_status "Setting up monitoring and logging..."
    
    # Create log-based metric for errors
    gcloud logging metrics create error_rate \
        --description="Rate of application errors" \
        --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
    
    # Create alerting policy (requires notification channels)
    cat > alerting-policy.json << EOF
{
    "displayName": "Resume Relevance System - High Error Rate",
    "conditions": [
        {
            "displayName": "Error rate condition",
            "conditionThreshold": {
                "filter": "metric.type=\"logging.googleapis.com/user/error_rate\" resource.type=\"global\"",
                "comparison": "COMPARISON_GREATER_THAN",
                "thresholdValue": 10,
                "duration": "300s"
            }
        }
    ],
    "enabled": true
}
EOF
    
    print_success "Monitoring and logging configured"
}

# Show deployment status
show_status() {
    print_status "Deployment Status:"
    
    # Cloud Run service status
    gcloud run services describe "$SERVICE_NAME" --region="$REGION"
    
    # Recent deployments
    print_status "Recent deployments:"
    gcloud run revisions list --service="$SERVICE_NAME" --region="$REGION" --limit=5
    
    # Service URL
    if [[ -f .gcp_service_url ]]; then
        source .gcp_service_url
        print_success "Service URL: $SERVICE_URL"
        print_status "Health check: ${SERVICE_URL}/health"
    fi
}

# Show logs
show_logs() {
    print_status "Application logs:"
    
    gcloud logs tail "projects/${PROJECT_ID}/logs/run.googleapis.com%2Fstdout" \
        --filter="resource.labels.service_name=${SERVICE_NAME}"
}

# Scale service
scale_service() {
    INSTANCE_COUNT="$1"
    
    if [[ -z "$INSTANCE_COUNT" ]]; then
        print_error "Instance count required"
        return 1
    fi
    
    print_status "Scaling service to $INSTANCE_COUNT instances..."
    
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --max-instances="$INSTANCE_COUNT"
    
    print_success "Service scaled"
}

# Set up CI/CD with Cloud Build
setup_cicd() {
    print_status "Setting up CI/CD with Cloud Build..."
    
    cat > cloudbuild.yaml << EOF
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/\$PROJECT_ID/${IMAGE_NAME}', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/\$PROJECT_ID/${IMAGE_NAME}']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${SERVICE_NAME}'
      - '--image'
      - 'gcr.io/\$PROJECT_ID/${IMAGE_NAME}'
      - '--region'
      - '${REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/\$PROJECT_ID/${IMAGE_NAME}'
EOF
    
    # Create build trigger (requires GitHub/Bitbucket integration)
    print_status "To complete CI/CD setup:"
    print_status "1. Connect your repository to Cloud Build"
    print_status "2. Create a trigger using cloudbuild.yaml"
    
    print_success "CI/CD configuration created"
}

# Clean up resources
cleanup() {
    print_warning "This will delete all GCP resources. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up GCP resources..."
        
        # Delete Cloud Run service
        gcloud run services delete "$SERVICE_NAME" --region="$REGION" --quiet 2>/dev/null || true
        
        # Delete Cloud SQL instance
        if [[ -f .gcp_db_config ]]; then
            source .gcp_db_config
            gcloud sql instances delete "$DB_INSTANCE_NAME" --quiet 2>/dev/null || true
        fi
        
        # Delete container images
        gcloud container images delete "gcr.io/${PROJECT_ID}/${IMAGE_NAME}" --quiet 2>/dev/null || true
        
        # Delete secrets
        gcloud secrets delete app-secret-key --quiet 2>/dev/null || true
        gcloud secrets delete db-password --quiet 2>/dev/null || true
        
        # Clean up local files
        rm -f .gcp_db_config .gcp_service_url alerting-policy.json cloudbuild.yaml
        
        print_success "Cleanup completed"
    fi
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -i|--init)
                ACTION="init"
                shift
                ;;
            -b|--build)
                ACTION="build"
                shift
                ;;
            -d|--deploy)
                ACTION="deploy"
                shift
                ;;
            -s|--status)
                ACTION="status"
                shift
                ;;
            -l|--logs)
                ACTION="logs"
                shift
                ;;
            -c|--cleanup)
                ACTION="cleanup"
                shift
                ;;
            --project)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --service)
                SERVICE_NAME="$2"
                shift 2
                ;;
            --domain)
                DOMAIN_NAME="$2"
                ACTION="domain"
                shift 2
                ;;
            --scale)
                INSTANCE_COUNT="$2"
                ACTION="scale"
                shift 2
                ;;
            --cicd)
                ACTION="cicd"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Execute action
    case "${ACTION:-help}" in
        init)
            check_requirements
            init_project
            ;;
        build)
            check_requirements
            build_and_push_image
            ;;
        deploy)
            check_requirements
            create_secrets
            deploy_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        domain)
            setup_domain "$DOMAIN_NAME"
            ;;
        scale)
            scale_service "$INSTANCE_COUNT"
            ;;
        cicd)
            setup_cicd
            ;;
        cleanup)
            cleanup
            ;;
        help|*)
            show_help
            ;;
    esac
}

main "$@"
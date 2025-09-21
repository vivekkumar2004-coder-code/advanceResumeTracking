#!/bin/bash

# Resume Relevance System - AWS ECS Deployment Script
# This script deploys the Resume Relevance System to AWS ECS using Fargate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
CLUSTER_NAME="${CLUSTER_NAME:-resume-relevance-cluster}"
SERVICE_NAME="${SERVICE_NAME:-resume-relevance-service}"
TASK_DEFINITION_NAME="${TASK_DEFINITION_NAME:-resume-relevance-task}"
ECR_REPOSITORY="${ECR_REPOSITORY:-resume-relevance}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

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
Resume Relevance System - AWS ECS Deployment Script

Usage: $0 [OPTION]

Options:
    -h, --help          Show this help message
    -d, --deploy        Deploy to AWS ECS
    -b, --build-push    Build and push Docker image to ECR
    -c, --create-infra  Create AWS infrastructure (VPC, ECS cluster, etc.)
    -s, --status        Show deployment status
    -l, --logs          Show application logs
    --clean             Clean up AWS resources
    --region REGION     AWS region (default: us-east-1)
    --cluster NAME      ECS cluster name
    --service NAME      ECS service name

Environment Variables:
    AWS_REGION          AWS region
    CLUSTER_NAME        ECS cluster name
    SERVICE_NAME        ECS service name
    ECR_REPOSITORY      ECR repository name
    IMAGE_TAG           Docker image tag

Examples:
    $0 -c              # Create infrastructure
    $0 -b              # Build and push image
    $0 -d              # Deploy application
    $0 -s              # Show status

EOF
}

# Check AWS CLI and dependencies
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured or credentials are invalid"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Create ECR repository if it doesn't exist
create_ecr_repository() {
    print_status "Creating ECR repository..."
    
    if aws ecr describe-repositories --repository-names "$ECR_REPOSITORY" --region "$AWS_REGION" &> /dev/null; then
        print_status "ECR repository already exists"
    else
        aws ecr create-repository \
            --repository-name "$ECR_REPOSITORY" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true
        print_success "ECR repository created"
    fi
    
    # Get ECR login token and login
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin \
        "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com"
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}"
    
    create_ecr_repository
    
    # Build image
    docker build -t "$ECR_REPOSITORY:$IMAGE_TAG" .
    docker tag "$ECR_REPOSITORY:$IMAGE_TAG" "$ECR_URI"
    
    # Push image
    docker push "$ECR_URI"
    
    print_success "Image pushed to $ECR_URI"
    echo "ECR_URI=$ECR_URI" > .ecr_uri
}

# Create VPC and networking
create_vpc() {
    print_status "Creating VPC and networking..."
    
    # Create VPC
    VPC_ID=$(aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=resume-relevance-vpc}]' \
        --query 'Vpc.VpcId' \
        --output text \
        --region "$AWS_REGION")
    
    # Enable DNS hostnames
    aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames --region "$AWS_REGION"
    
    # Create Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway \
        --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=resume-relevance-igw}]' \
        --query 'InternetGateway.InternetGatewayId' \
        --output text \
        --region "$AWS_REGION")
    
    # Attach Internet Gateway to VPC
    aws ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID" --region "$AWS_REGION"
    
    # Create subnets
    SUBNET1_ID=$(aws ec2 create-subnet \
        --vpc-id "$VPC_ID" \
        --cidr-block 10.0.1.0/24 \
        --availability-zone "${AWS_REGION}a" \
        --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=resume-relevance-subnet-1}]' \
        --query 'Subnet.SubnetId' \
        --output text \
        --region "$AWS_REGION")
    
    SUBNET2_ID=$(aws ec2 create-subnet \
        --vpc-id "$VPC_ID" \
        --cidr-block 10.0.2.0/24 \
        --availability-zone "${AWS_REGION}b" \
        --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=resume-relevance-subnet-2}]' \
        --query 'Subnet.SubnetId' \
        --output text \
        --region "$AWS_REGION")
    
    # Enable auto-assign public IP
    aws ec2 modify-subnet-attribute --subnet-id "$SUBNET1_ID" --map-public-ip-on-launch --region "$AWS_REGION"
    aws ec2 modify-subnet-attribute --subnet-id "$SUBNET2_ID" --map-public-ip-on-launch --region "$AWS_REGION"
    
    # Create route table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table \
        --vpc-id "$VPC_ID" \
        --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=resume-relevance-rt}]' \
        --query 'RouteTable.RouteTableId' \
        --output text \
        --region "$AWS_REGION")
    
    # Add route to Internet Gateway
    aws ec2 create-route \
        --route-table-id "$ROUTE_TABLE_ID" \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id "$IGW_ID" \
        --region "$AWS_REGION"
    
    # Associate subnets with route table
    aws ec2 associate-route-table --subnet-id "$SUBNET1_ID" --route-table-id "$ROUTE_TABLE_ID" --region "$AWS_REGION"
    aws ec2 associate-route-table --subnet-id "$SUBNET2_ID" --route-table-id "$ROUTE_TABLE_ID" --region "$AWS_REGION"
    
    # Create security group
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name resume-relevance-sg \
        --description "Security group for Resume Relevance System" \
        --vpc-id "$VPC_ID" \
        --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=resume-relevance-sg}]' \
        --query 'GroupId' \
        --output text \
        --region "$AWS_REGION")
    
    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 5000 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
    
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region "$AWS_REGION"
    
    # Save configuration
    cat > .aws_config << EOF
VPC_ID=$VPC_ID
SUBNET1_ID=$SUBNET1_ID
SUBNET2_ID=$SUBNET2_ID
SECURITY_GROUP_ID=$SECURITY_GROUP_ID
IGW_ID=$IGW_ID
ROUTE_TABLE_ID=$ROUTE_TABLE_ID
EOF
    
    print_success "VPC and networking created"
}

# Create ECS cluster
create_ecs_cluster() {
    print_status "Creating ECS cluster..."
    
    aws ecs create-cluster \
        --cluster-name "$CLUSTER_NAME" \
        --capacity-providers FARGATE \
        --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
        --region "$AWS_REGION"
    
    print_success "ECS cluster created"
}

# Create task definition
create_task_definition() {
    print_status "Creating ECS task definition..."
    
    if [[ ! -f .ecr_uri ]]; then
        print_error "ECR URI not found. Run build and push first."
        exit 1
    fi
    
    ECR_URI=$(cat .ecr_uri | cut -d'=' -f2)
    
    cat > task-definition.json << EOF
{
    "family": "$TASK_DEFINITION_NAME",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "resume-relevance-app",
            "image": "$ECR_URI",
            "portMappings": [
                {
                    "containerPort": 5000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "FLASK_ENV",
                    "value": "production"
                },
                {
                    "name": "DATABASE_TYPE",
                    "value": "sqlite"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/resume-relevance",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOF
    
    # Create log group
    aws logs create-log-group --log-group-name "/ecs/resume-relevance" --region "$AWS_REGION" 2>/dev/null || true
    
    # Register task definition
    aws ecs register-task-definition \
        --cli-input-json file://task-definition.json \
        --region "$AWS_REGION"
    
    print_success "Task definition created"
}

# Create ECS service
create_ecs_service() {
    print_status "Creating ECS service..."
    
    source .aws_config
    
    aws ecs create-service \
        --cluster "$CLUSTER_NAME" \
        --service-name "$SERVICE_NAME" \
        --task-definition "$TASK_DEFINITION_NAME" \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1_ID,$SUBNET2_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
        --region "$AWS_REGION"
    
    print_success "ECS service created"
}

# Create Application Load Balancer (optional)
create_load_balancer() {
    print_status "Creating Application Load Balancer..."
    
    source .aws_config
    
    # Create target group
    TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
        --name resume-relevance-tg \
        --protocol HTTP \
        --port 5000 \
        --vpc-id "$VPC_ID" \
        --target-type ip \
        --health-check-path /health \
        --region "$AWS_REGION" \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text)
    
    # Create load balancer
    LOAD_BALANCER_ARN=$(aws elbv2 create-load-balancer \
        --name resume-relevance-alb \
        --subnets "$SUBNET1_ID" "$SUBNET2_ID" \
        --security-groups "$SECURITY_GROUP_ID" \
        --region "$AWS_REGION" \
        --query 'LoadBalancers[0].LoadBalancerArn' \
        --output text)
    
    # Create listener
    aws elbv2 create-listener \
        --load-balancer-arn "$LOAD_BALANCER_ARN" \
        --protocol HTTP \
        --port 80 \
        --default-actions Type=forward,TargetGroupArn="$TARGET_GROUP_ARN" \
        --region "$AWS_REGION"
    
    print_success "Load balancer created"
    
    # Get load balancer DNS name
    DNS_NAME=$(aws elbv2 describe-load-balancers \
        --load-balancer-arns "$LOAD_BALANCER_ARN" \
        --region "$AWS_REGION" \
        --query 'LoadBalancers[0].DNSName' \
        --output text)
    
    echo "TARGET_GROUP_ARN=$TARGET_GROUP_ARN" >> .aws_config
    echo "LOAD_BALANCER_ARN=$LOAD_BALANCER_ARN" >> .aws_config
    echo "DNS_NAME=$DNS_NAME" >> .aws_config
    
    print_success "Application will be available at: http://$DNS_NAME"
}

# Show deployment status
show_status() {
    print_status "Deployment Status:"
    
    # ECS cluster status
    aws ecs describe-clusters --clusters "$CLUSTER_NAME" --region "$AWS_REGION"
    
    # Service status
    aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$SERVICE_NAME" --region "$AWS_REGION"
    
    # Task status
    aws ecs list-tasks --cluster "$CLUSTER_NAME" --service-name "$SERVICE_NAME" --region "$AWS_REGION"
}

# Show logs
show_logs() {
    print_status "Application logs:"
    
    aws logs tail "/ecs/resume-relevance" --follow --region "$AWS_REGION"
}

# Clean up resources
cleanup() {
    print_warning "This will delete all AWS resources. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up AWS resources..."
        
        # Delete ECS service
        aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME" --desired-count 0 --region "$AWS_REGION" 2>/dev/null || true
        aws ecs delete-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME" --region "$AWS_REGION" 2>/dev/null || true
        
        # Delete ECS cluster
        aws ecs delete-cluster --cluster "$CLUSTER_NAME" --region "$AWS_REGION" 2>/dev/null || true
        
        # Clean up VPC resources if config exists
        if [[ -f .aws_config ]]; then
            source .aws_config
            
            # Delete load balancer resources
            aws elbv2 delete-load-balancer --load-balancer-arn "$LOAD_BALANCER_ARN" --region "$AWS_REGION" 2>/dev/null || true
            aws elbv2 delete-target-group --target-group-arn "$TARGET_GROUP_ARN" --region "$AWS_REGION" 2>/dev/null || true
            
            # Delete VPC resources
            aws ec2 detach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID" --region "$AWS_REGION" 2>/dev/null || true
            aws ec2 delete-internet-gateway --internet-gateway-id "$IGW_ID" --region "$AWS_REGION" 2>/dev/null || true
            aws ec2 delete-subnet --subnet-id "$SUBNET1_ID" --region "$AWS_REGION" 2>/dev/null || true
            aws ec2 delete-subnet --subnet-id "$SUBNET2_ID" --region "$AWS_REGION" 2>/dev/null || true
            aws ec2 delete-security-group --group-id "$SECURITY_GROUP_ID" --region "$AWS_REGION" 2>/dev/null || true
            aws ec2 delete-route-table --route-table-id "$ROUTE_TABLE_ID" --region "$AWS_REGION" 2>/dev/null || true
            aws ec2 delete-vpc --vpc-id "$VPC_ID" --region "$AWS_REGION" 2>/dev/null || true
        fi
        
        # Clean up local files
        rm -f .aws_config .ecr_uri task-definition.json
        
        print_success "Cleanup completed"
    fi
}

# Main function
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            ;;
        -c|--create-infra)
            check_requirements
            create_vpc
            create_ecs_cluster
            ;;
        -b|--build-push)
            check_requirements
            build_and_push_image
            ;;
        -d|--deploy)
            check_requirements
            create_task_definition
            create_ecs_service
            create_load_balancer
            ;;
        -s|--status)
            show_status
            ;;
        -l|--logs)
            show_logs
            ;;
        --clean)
            cleanup
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

main "$@"
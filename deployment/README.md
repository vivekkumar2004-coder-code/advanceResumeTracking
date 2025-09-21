# Resume Relevance System - Deployment Scripts

This directory contains deployment scripts for various platforms:

## Local Docker Deployment

### `deploy-docker.sh`

Deploy and manage the application using Docker Compose locally.

**Usage:**

```bash
# Start in development mode (default)
./deployment/deploy-docker.sh

# Start in production mode
./deployment/deploy-docker.sh -p

# Start with monitoring stack
./deployment/deploy-docker.sh -m

# Stop services
./deployment/deploy-docker.sh -s

# Clean up everything
./deployment/deploy-docker.sh -c

# View logs
./deployment/deploy-docker.sh -l
```

**Features:**

- Multi-stage Docker builds (development/production)
- PostgreSQL database with pgAdmin
- Redis for caching
- Nginx reverse proxy
- Prometheus and Grafana monitoring (optional)
- Automatic environment file creation

## AWS ECS Deployment

### `deploy-aws.sh`

Deploy to Amazon Web Services using ECS Fargate.

**Prerequisites:**

- AWS CLI configured with appropriate permissions
- Docker installed

**Usage:**

```bash
# Create AWS infrastructure (VPC, ECS cluster, etc.)
./deployment/deploy-aws.sh -c

# Build and push Docker image to ECR
./deployment/deploy-aws.sh -b

# Deploy application to ECS
./deployment/deploy-aws.sh -d

# Show deployment status
./deployment/deploy-aws.sh -s

# View application logs
./deployment/deploy-aws.sh -l

# Clean up all AWS resources
./deployment/deploy-aws.sh --clean
```

**Features:**

- VPC with public subnets across multiple AZs
- ECS Fargate cluster with auto-scaling
- Application Load Balancer
- CloudWatch logging
- ECR container registry
- Security groups and IAM roles

## Google Cloud Platform Deployment

### `deploy-gcp.sh`

Deploy to Google Cloud Platform using Cloud Run.

**Prerequisites:**

- Google Cloud SDK installed and authenticated
- Docker installed

**Usage:**

```bash
# Initialize GCP project and enable APIs
./deployment/deploy-gcp.sh -i

# Build and push image to Container Registry
./deployment/deploy-gcp.sh -b

# Deploy to Cloud Run
./deployment/deploy-gcp.sh -d

# Show deployment status
./deployment/deploy-gcp.sh -s

# View application logs
./deployment/deploy-gcp.sh -l

# Clean up all GCP resources
./deployment/deploy-gcp.sh -c
```

**Additional Features:**

```bash
# Set up custom domain
./deployment/deploy-gcp.sh --domain your-domain.com

# Scale service
./deployment/deploy-gcp.sh --scale 5

# Set up CI/CD
./deployment/deploy-gcp.sh --cicd
```

**Features:**

- Cloud Run serverless deployment
- Cloud SQL PostgreSQL (optional)
- Secret Manager for sensitive data
- Cloud Build for CI/CD
- Custom domain mapping
- Auto-scaling and load balancing

## Environment Variables

All deployment scripts support environment variables for configuration:

### Common Variables

```bash
# Security
SECRET_KEY=your-secret-key

# Database
DATABASE_TYPE=postgresql  # or sqlite
DATABASE_URL=postgresql://user:pass@host:port/db

# Email Configuration
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application Settings
FLASK_ENV=production
MAX_CONTENT_LENGTH=16777216
```

### AWS-Specific Variables

```bash
AWS_REGION=us-east-1
CLUSTER_NAME=resume-relevance-cluster
SERVICE_NAME=resume-relevance-service
ECR_REPOSITORY=resume-relevance
```

### GCP-Specific Variables

```bash
PROJECT_ID=resume-relevance-project
REGION=us-central1
SERVICE_NAME=resume-relevance
IMAGE_NAME=resume-relevance
```

## Security Considerations

### Production Checklist

- [ ] Use strong, unique secret keys
- [ ] Enable HTTPS/TLS encryption
- [ ] Configure proper firewall rules
- [ ] Use managed databases with backups
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Implement proper access controls
- [ ] Use secrets management services

### Database Security

- [ ] Use connection encryption
- [ ] Regular backups and point-in-time recovery
- [ ] Network isolation (VPC/private subnets)
- [ ] Strong passwords and user management
- [ ] Audit logging enabled

### Container Security

- [ ] Scan images for vulnerabilities
- [ ] Use non-root users in containers
- [ ] Minimal base images (distroless/alpine)
- [ ] Regular image updates
- [ ] Resource limits and quotas

## Monitoring and Logging

### Local Development

- **Logs**: `docker-compose logs -f`
- **Metrics**: Prometheus at http://localhost:9090
- **Dashboards**: Grafana at http://localhost:3000

### AWS ECS

- **Logs**: CloudWatch Logs
- **Metrics**: CloudWatch Metrics
- **Monitoring**: CloudWatch Dashboards and Alarms

### Google Cloud

- **Logs**: Cloud Logging
- **Metrics**: Cloud Monitoring
- **Tracing**: Cloud Trace

## Troubleshooting

### Common Issues

1. **Container Won't Start**

   - Check logs: `docker-compose logs app`
   - Verify environment variables
   - Check port conflicts

2. **Database Connection Failed**

   - Verify database is running
   - Check connection string
   - Ensure network connectivity

3. **Image Build Fails**

   - Check Dockerfile syntax
   - Verify all dependencies are available
   - Ensure sufficient disk space

4. **Memory Issues**
   - Increase container memory limits
   - Check for memory leaks
   - Optimize ML model loading

### Getting Help

1. Check application logs first
2. Verify environment configuration
3. Test components individually
4. Review security group/firewall rules
5. Check resource quotas and limits

## Cost Optimization

### AWS

- Use Fargate Spot for development
- Set up auto-scaling policies
- Use smaller instance types when possible
- Monitor and set up billing alerts

### GCP

- Use Cloud Run's pay-per-request model
- Set minimum instances to 0 for development
- Use preemptible instances for batch jobs
- Monitor billing and set up budget alerts

### General

- Implement proper caching strategies
- Use CDN for static assets
- Optimize database queries
- Regular cleanup of unused resources

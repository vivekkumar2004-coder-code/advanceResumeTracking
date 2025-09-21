# 🎯 Resume Relevance System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-Pytest-orange.svg)](https://pytest.org/)

An intelligent, AI-powered system for automatically evaluating resume relevance against job descriptions, with advanced ML capabilities, automated email notifications, and comprehensive analytics.

## 🌟 Features

### Core Functionality

- **🤖 AI-Powered Analysis**: Advanced resume parsing with ML-based relevance scoring
- **📊 Smart Matching**: Intelligent skill extraction and job-resume compatibility analysis
- **📧 Automated Communication**: Personalized email notifications with professional templates
- **💾 Persistent Storage**: Comprehensive database system for candidates, jobs, and evaluations
- **🎨 Interactive Dashboard**: Modern web interface with real-time analytics
- **🔄 RESTful API**: Complete REST API for integration with external systems

### Advanced Features

- **🧠 Transformer Models**: Semantic similarity using state-of-the-art NLP models
- **📈 Analytics Dashboard**: Comprehensive reporting and visualization
- **🔍 Advanced Search**: Full-text search across resumes and job descriptions
- **📱 Responsive Design**: Mobile-friendly interface with Bootstrap
- **🚀 Production Ready**: Docker containerization with cloud deployment scripts
- **🔐 Security**: Input validation, SQL injection protection, and secure file handling

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
4. [Usage](#-usage)
5. [API Documentation](#-api-documentation)
6. [Deployment](#-deployment)
7. [Development](#-development)
8. [Testing](#-testing)
9. [Contributing](#-contributing)
10. [License](#-license)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/resume-relevance-system.git
cd resume-relevance-system

# Start with Docker Compose
chmod +x deployment/deploy-docker.sh
./deployment/deploy-docker.sh

# Access the application
open http://localhost:5000
```

### Option 2: Local Installation

```bash
# Clone and setup virtual environment
git clone https://github.com/your-username/resume-relevance-system.git
cd resume-relevance-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_new.txt

# Run the application
python app_safe.py

# Access the application
open http://localhost:5000
```

### Option 3: Cloud Deployment

```bash
# AWS ECS
./deployment/deploy-aws.sh -c  # Create infrastructure
./deployment/deploy-aws.sh -b  # Build and push image
./deployment/deploy-aws.sh -d  # Deploy application

# Google Cloud Run
./deployment/deploy-gcp.sh -i  # Initialize project
./deployment/deploy-gcp.sh -b  # Build and push image
./deployment/deploy-gcp.sh -d  # Deploy application
```

## 💻 Installation

### Prerequisites

- **Python 3.11+** (3.11 recommended for best ML library compatibility)
- **Git** for version control
- **Docker & Docker Compose** (optional, for containerized deployment)
- **PostgreSQL** (optional, SQLite used by default)

### System Requirements

- **Memory**: 2GB RAM minimum (4GB+ recommended with ML features)
- **Storage**: 1GB free space (more for file uploads and cache)
- **Network**: Internet access for ML model downloads

### Local Development Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/resume-relevance-system.git
   cd resume-relevance-system
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**

   ```bash
   # Core dependencies
   pip install -r requirements_new.txt

   # Development dependencies (optional)
   pip install -r requirements-test.txt
   ```

4. **Create Environment File**

   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python -c "from app import create_app; from app.utils.database_manager import db_manager; app = create_app(); app.app_context().push(); db_manager.create_tables()"
   ```

### Production Dependencies

For production deployment with full ML capabilities:

```bash
# Install additional ML libraries
pip install torch>=2.0.0 transformers>=4.30.0 sentence-transformers>=2.2.0

# For advanced PDF processing
pip install PyMuPDF>=1.23.0

# For production web server
pip install gunicorn>=21.2.0
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
FLASK_DEBUG=0

# Database Configuration
DATABASE_TYPE=sqlite                    # Options: sqlite, postgresql
DATABASE_URL=sqlite:///data/resume_relevance.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/resume_relevance

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216            # 16MB in bytes

# Email Configuration (Optional)
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp                     # Options: smtp, sendgrid, aws_ses
SENDER_EMAIL=noreply@yourcompany.com
SENDER_NAME=HR System

# SMTP Settings (if using EMAIL_PROVIDER=smtp)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password        # Use App Password for Gmail
SMTP_USE_TLS=true

# SendGrid Settings (if using EMAIL_PROVIDER=sendgrid)
SENDGRID_API_KEY=SG.your-sendgrid-api-key

# AWS SES Settings (if using EMAIL_PROVIDER=aws_ses)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# ML Model Settings
ENABLE_TRANSFORMERS=true               # Set to false for lighter deployment
TRANSFORMER_MODEL=all-MiniLM-L6-v2     # Sentence transformer model
EMBEDDING_CACHE_SIZE=1000              # Number of embeddings to cache

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
CORS_ENABLED=true

# Performance Settings
CACHE_TYPE=simple                      # Options: simple, redis
REDIS_URL=redis://localhost:6379       # If using Redis cache
```

### Email Templates Configuration

The system includes three built-in email templates:

- **High Relevance** (`high_relevance.html`): For scores 80-100
- **Medium Relevance** (`medium_relevance.html`): For scores 60-79
- **Low Relevance** (`low_relevance.html`): For scores 0-59

Templates support the following variables:

```python
{
    'candidate_name': 'John Doe',
    'job_title': 'Senior Python Developer',
    'company_name': 'Tech Corporation',
    'relevance_score': 85.5,
    'relevance_level': 'high',
    'matched_skills': ['Python', 'Flask', 'PostgreSQL'],
    'missing_skills': ['Docker', 'Kubernetes'],
    'strengths': ['Strong technical background', '3+ years experience'],
    'recommendations': ['Consider learning containerization', 'Gain cloud experience']
}
```

## 🎯 Usage

### Web Interface

1. **Access the Dashboard**

   - Navigate to `http://localhost:5000`
   - Use the interactive web interface for all operations

2. **Upload Files**

   - Upload resumes (PDF, DOCX, TXT)
   - Upload job descriptions (TXT, PDF)
   - Or paste text directly

3. **Evaluate Resumes**

   - Select resume and job description
   - Click "Evaluate" to get relevance score
   - View detailed analysis and recommendations

4. **Send Email Notifications**
   - Configure email settings in dashboard
   - Send personalized evaluation emails
   - Track delivery status

### API Usage

#### Upload Resume

```bash
# Upload resume file
curl -X POST http://localhost:5000/api/upload/resume \
  -F "file=@resume.pdf"

# Upload resume text
curl -X POST http://localhost:5000/api/upload/resume \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe\nSoftware Engineer\nSkills: Python, Flask..."}'
```

#### Evaluate Resume

```bash
curl -X POST http://localhost:5000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "resume-file-id",
    "job_id": "job-file-id"
  }'
```

#### Send Evaluation Email

```bash
curl -X POST http://localhost:5000/api/email/send-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "eval-123",
    "candidate_email": "candidate@example.com",
    "candidate_name": "John Doe"
  }'
```

### Database Operations

#### Save Candidate

```bash
curl -X POST http://localhost:5000/api/database/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "resume_text": "Software Engineer with 3+ years...",
    "skills": ["Python", "Flask", "PostgreSQL"]
  }'
```

#### Search Candidates

```bash
curl "http://localhost:5000/api/database/candidates/search?q=python&limit=10"
```

#### Get Analytics

```bash
curl "http://localhost:5000/api/database/analytics/dashboard"
```

## 📚 API Documentation

### Authentication

Currently, the API doesn't require authentication. For production deployment, consider implementing:

- API key authentication
- OAuth 2.0
- JWT tokens

### Base URL

```
Local Development: http://localhost:5000
Production: https://your-domain.com
```

### Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Core Endpoints

#### Upload Endpoints

- `POST /api/upload/resume` - Upload resume file or text
- `POST /api/upload/job-description` - Upload job description
- `GET /api/files` - List uploaded files

#### Evaluation Endpoints

- `POST /api/evaluate` - Evaluate resume against job description
- `POST /api/analyze-keywords` - Extract keywords from job description
- `GET /api/evaluate/{evaluation_id}` - Get evaluation details

#### Database Endpoints

- `POST /api/database/candidates` - Create candidate
- `GET /api/database/candidates/{id}` - Get candidate details
- `GET /api/database/candidates/search` - Search candidates
- `POST /api/database/jobs` - Create job description
- `GET /api/database/jobs` - List active jobs
- `POST /api/database/evaluations` - Save evaluation
- `GET /api/database/analytics/dashboard` - Get analytics data

#### Email Endpoints

- `POST /api/email/send-evaluation` - Send evaluation email
- `GET /api/email/config` - Get email configuration
- `POST /api/email/config` - Update email configuration
- `POST /api/email/test` - Send test email
- `GET /api/email/history` - Get email history
- `GET /api/email/stats` - Get email statistics

#### System Endpoints

- `GET /health` - Health check
- `GET /api/info` - System information
- `GET /api/database/health` - Database health check

### Request/Response Examples

#### Evaluate Resume

**Request:**

```json
POST /api/evaluate
{
  "resume_id": "resume-abc123",
  "job_id": "job-def456"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "evaluation_id": "eval-789xyz",
    "relevance_score": 85.5,
    "relevance_level": "high",
    "total_matching_skills": 7,
    "total_job_skills": 10,
    "matched_skills": ["Python", "Flask", "PostgreSQL", "Machine Learning"],
    "missing_skills": ["Docker", "Kubernetes", "AWS"],
    "strengths": [
      "Strong technical background in Python development",
      "Relevant experience with web frameworks",
      "Database design skills"
    ],
    "recommendations": [
      "Consider learning containerization with Docker",
      "Gain experience with cloud platforms like AWS",
      "Develop Kubernetes orchestration skills"
    ],
    "detailed_analysis": {
      "technical_skills": {
        "score": 90,
        "details": "Excellent match for technical requirements"
      },
      "experience": {
        "score": 85,
        "details": "Good experience level for the role"
      },
      "education": {
        "score": 80,
        "details": "Relevant educational background"
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🐳 Deployment

### Docker Deployment (Recommended)

1. **Development Environment**

   ```bash
   # Quick start
   ./deployment/deploy-docker.sh

   # With monitoring stack
   ./deployment/deploy-docker.sh -m
   ```

2. **Production Environment**
   ```bash
   # Production mode with PostgreSQL and Redis
   ./deployment/deploy-docker.sh -p
   ```

### Cloud Deployment

#### AWS ECS with Fargate

```bash
# Create infrastructure
./deployment/deploy-aws.sh -c

# Build and deploy
./deployment/deploy-aws.sh -b
./deployment/deploy-aws.sh -d

# Monitor deployment
./deployment/deploy-aws.sh -s
```

#### Google Cloud Run

```bash
# Initialize project
./deployment/deploy-gcp.sh -i --project your-project-id

# Build and deploy
./deployment/deploy-gcp.sh -b
./deployment/deploy-gcp.sh -d

# Set up custom domain
./deployment/deploy-gcp.sh --domain your-domain.com
```

### Manual Production Deployment

1. **Using Gunicorn (Recommended)**

   ```bash
   # Install Gunicorn
   pip install gunicorn

   # Run with Gunicorn
   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
   ```

2. **Using uWSGI**

   ```bash
   # Install uWSGI
   pip install uwsgi

   # Create uwsgi.ini configuration
   uwsgi --ini uwsgi.ini
   ```

3. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /path/to/your/app/static;
       }
   }
   ```

## 👨‍💻 Development

### Development Setup

1. **Install Development Dependencies**

   ```bash
   pip install -r requirements-test.txt
   ```

2. **Run in Development Mode**

   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   python app.py
   ```

3. **Database Development**

   ```bash
   # Create migration
   flask db migrate -m "Add new table"

   # Apply migration
   flask db upgrade
   ```

### Project Structure

```
resume-relevance-system/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   └── database_schema.py
│   ├── routes/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── upload_routes.py
│   │   ├── evaluation_routes.py
│   │   ├── database_routes.py
│   │   └── email_routes.py
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── resume_parser.py
│       ├── relevance_analyzer.py
│       ├── email_sender.py
│       ├── database_manager.py
│       └── ...
├── templates/                   # Jinja2 templates
│   ├── dashboard.html
│   └── emails/
│       ├── high_relevance.html
│       ├── medium_relevance.html
│       └── low_relevance.html
├── static/                      # Static assets
│   ├── css/
│   └── js/
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_integration.py
│   └── test_email_system.py
├── deployment/                  # Deployment scripts
│   ├── deploy-docker.sh
│   ├── deploy-aws.sh
│   ├── deploy-gcp.sh
│   └── README.md
├── config/                      # Configuration files
├── data/                        # Database files
├── uploads/                     # File uploads
├── embeddings_cache/           # ML model cache
├── docker-compose.yml
├── Dockerfile
├── requirements_new.txt
└── README.md
```

### Code Style and Standards

1. **Python Code Style**

   ```bash
   # Install formatting tools
   pip install black flake8 isort

   # Format code
   black .
   isort .
   flake8 .
   ```

2. **Pre-commit Hooks**

   ```bash
   # Install pre-commit
   pip install pre-commit

   # Install hooks
   pre-commit install

   # Run hooks manually
   pre-commit run --all-files
   ```

### Adding New Features

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/new-amazing-feature
   ```

2. **Write Tests First**

   ```bash
   # Add tests to appropriate test file
   touch tests/test_new_feature.py
   ```

3. **Implement Feature**

   - Add route handlers in `app/routes/`
   - Add business logic in `app/utils/`
   - Update database models if needed

4. **Test Your Changes**
   ```bash
   pytest tests/test_new_feature.py -v
   ```

## 🧪 Testing

### Running Tests

1. **Run All Tests**

   ```bash
   # Basic test run
   pytest

   # With coverage
   pytest --cov=app --cov-report=html

   # Verbose output
   pytest -v --tb=short
   ```

2. **Run Specific Test Categories**

   ```bash
   # Unit tests only
   pytest -m unit

   # Integration tests only
   pytest -m integration

   # API tests only
   pytest -m api

   # Database tests only
   pytest -m database

   # Email tests only
   pytest -m email
   ```

3. **Run Tests with Different Configurations**

   ```bash
   # Test with SQLite
   pytest --db-url=sqlite:///:memory:

   # Test with PostgreSQL
   pytest --db-url=postgresql://user:pass@localhost/test_db

   # Parallel testing
   pytest -n auto
   ```

### Test Structure

The test suite includes:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows
- **API Tests**: Test all REST endpoints
- **Database Tests**: Test database operations
- **Email Tests**: Test email functionality

### Writing Tests

Example test structure:

```python
import pytest
from tests.conftest import TestDataFactory

class TestResumeEvaluation:
    def test_evaluate_resume_success(self, client, sample_resume, sample_job):
        """Test successful resume evaluation"""
        response = client.post('/api/evaluate', json={
            'resume_id': sample_resume['id'],
            'job_id': sample_job['id']
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'relevance_score' in data
        assert 0 <= data['relevance_score'] <= 100
```

### Test Coverage

Current test coverage areas:

- ✅ API endpoints (all routes)
- ✅ Database operations (CRUD, queries)
- ✅ Email functionality (sending, templates, tracking)
- ✅ File upload and processing
- ✅ Resume parsing and analysis
- ✅ Error handling and validation
- ✅ Integration workflows
- ✅ Security and input validation

Target coverage: **80%+**

## 🤝 Contributing

We welcome contributions from the community! Here's how to get involved:

### Getting Started

1. **Fork the Repository**

   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/resume-relevance-system.git
   ```

2. **Set Up Development Environment**

   ```bash
   cd resume-relevance-system
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-test.txt
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

1. **Code Quality**

   - Follow PEP 8 style guidelines
   - Write comprehensive tests
   - Add docstrings to functions and classes
   - Use type hints where appropriate

2. **Commit Messages**

   ```bash
   # Use conventional commit format
   feat: add new resume parsing algorithm
   fix: resolve email template rendering issue
   docs: update API documentation
   test: add integration tests for evaluation workflow
   ```

3. **Pull Request Process**
   - Ensure all tests pass
   - Update documentation if needed
   - Add changelog entry
   - Request review from maintainers

### Areas for Contribution

- 🐛 **Bug Fixes**: Fix issues and improve stability
- ✨ **New Features**: Add new functionality and capabilities
- 📚 **Documentation**: Improve docs and examples
- 🧪 **Testing**: Increase test coverage
- 🎨 **UI/UX**: Enhance the web interface
- 🚀 **Performance**: Optimize algorithms and database queries
- 🌐 **Internationalization**: Add multi-language support
- 🔧 **DevOps**: Improve deployment and monitoring

### Feature Requests

Open an issue with:

- Clear description of the feature
- Use case and benefits
- Proposed implementation approach
- Any related resources or examples

### Bug Reports

Open an issue with:

- Steps to reproduce the bug
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces
- Minimal code example if applicable

## 📈 Performance and Scalability

### Performance Considerations

1. **Database Optimization**

   - Use database indexes for frequent queries
   - Implement pagination for large result sets
   - Consider read replicas for heavy read workloads

2. **Caching Strategy**

   - Cache ML model predictions
   - Cache frequently accessed data
   - Use Redis for distributed caching

3. **File Processing**

   - Async processing for large files
   - Implement file size limits
   - Use cloud storage for scalability

4. **ML Model Optimization**
   - Model quantization for smaller memory footprint
   - Batch processing for multiple evaluations
   - Consider model serving frameworks

### Scaling Options

1. **Horizontal Scaling**

   ```bash
   # Docker Swarm
   docker swarm init
   docker stack deploy -c docker-compose.yml resume-app

   # Kubernetes
   kubectl apply -f k8s/
   ```

2. **Load Balancing**

   - Nginx for load balancing
   - Cloud load balancers (AWS ALB, GCP Load Balancer)
   - Consider sticky sessions for file uploads

3. **Database Scaling**
   - Read replicas for read-heavy workloads
   - Database sharding for very large datasets
   - Consider managed database services

## 🛡️ Security

### Security Features

- **Input Validation**: All inputs validated and sanitized
- **SQL Injection Protection**: Parameterized queries and ORM
- **XSS Prevention**: Template auto-escaping and CSP headers
- **File Upload Security**: File type validation and virus scanning
- **Rate Limiting**: API rate limiting and abuse prevention
- **HTTPS Support**: TLS encryption for data in transit

### Security Best Practices

1. **Authentication and Authorization**

   ```python
   # Implement API key authentication
   @require_api_key
   def protected_endpoint():
       return jsonify({'message': 'Authenticated access'})
   ```

2. **Environment Variables**

   ```bash
   # Never commit secrets to version control
   # Use environment variables or secret management
   SECRET_KEY=your-secret-key
   DATABASE_PASSWORD=secure-password
   ```

3. **Regular Updates**
   ```bash
   # Keep dependencies updated
   pip install --upgrade pip
   pip-audit  # Check for security vulnerabilities
   ```

## 📊 Monitoring and Logging

### Application Monitoring

1. **Health Checks**

   ```bash
   # Built-in health check endpoint
   curl http://localhost:5000/health
   ```

2. **Logging Configuration**

   ```python
   # Structured logging with different levels
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

3. **Metrics Collection**
   - Application metrics (requests, response times, errors)
   - Business metrics (evaluations performed, emails sent)
   - System metrics (CPU, memory, disk usage)

### Production Monitoring

1. **Error Tracking**

   - Integration with Sentry for error tracking
   - Custom error handlers for different error types
   - Automated error notifications

2. **Performance Monitoring**

   - APM tools (New Relic, Datadog, Prometheus)
   - Database query monitoring
   - ML model performance tracking

3. **Log Aggregation**
   - ELK stack (Elasticsearch, Logstash, Kibana)
   - Cloud logging (AWS CloudWatch, GCP Cloud Logging)
   - Structured logging with JSON format

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Team** for the excellent web framework
- **Hugging Face** for transformer models and libraries
- **OpenAI** for inspiring the intelligent evaluation approach
- **Bootstrap** for the responsive UI framework
- **Docker** for containerization technology

## 📞 Support

### Getting Help

1. **Documentation**: Check this README and `/docs` directory
2. **Issues**: Search existing issues on GitHub
3. **Discussions**: Join GitHub Discussions for questions
4. **Email**: Contact maintainers for critical issues

### Community

- **GitHub**: [https://github.com/your-username/resume-relevance-system](https://github.com/your-username/resume-relevance-system)
- **Discord**: [Join our community server](#)
- **Stack Overflow**: Tag questions with `resume-relevance-system`

### Commercial Support

For enterprise deployments and commercial support:

- Technical consulting and customization
- Priority support and SLA guarantees
- Training and onboarding assistance
- Custom feature development

Contact: [enterprise@yourcompany.com](mailto:enterprise@yourcompany.com)

---

## 🎉 What's Next?

### Roadmap

- [ ] **v2.0**: Advanced ML models with custom fine-tuning
- [ ] **v2.1**: Multi-language support for global deployments
- [ ] **v2.2**: Advanced analytics and reporting dashboard
- [ ] **v2.3**: Integration with popular ATS systems
- [ ] **v2.4**: Mobile application for recruiters
- [ ] **v2.5**: Real-time collaboration features

### Contributing to the Future

Want to help shape the future of the Resume Relevance System?

- ⭐ Star the repository to show support
- 🐛 Report bugs and suggest improvements
- 💡 Contribute new features and enhancements
- 📖 Help improve documentation
- 🌐 Spread the word about the project

**Made with ❤️ for the HR and recruitment community**

---

_Last updated: December 2024_

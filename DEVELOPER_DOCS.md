# 👨‍💻 Developer Documentation

Welcome to the Resume Relevance System development guide! This document will help you get started with local development, understand the codebase structure, and contribute effectively to the project.

## 🚀 Quick Start for Developers

### Prerequisites

1. **Python 3.11+** (Required for best compatibility)
2. **Git** for version control
3. **Docker & Docker Compose** (Optional, for containerized development)
4. **IDE/Editor** (VS Code recommended with Python extension)

### Initial Setup

1. **Clone and Setup Environment**

   ```bash
   # Fork the repo on GitHub first, then clone your fork
   git clone https://github.com/YOUR_USERNAME/resume-relevance-system.git
   cd resume-relevance-system

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**

   ```bash
   # Core dependencies
   pip install -r requirements_new.txt

   # Development dependencies
   pip install -r requirements-test.txt

   # Optional: Install pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

3. **Configure Environment**

   ```bash
   # Copy environment template
   cp env_example.txt .env

   # Edit .env with your settings (see Configuration Guide below)
   ```

4. **Initialize Database**

   ```bash
   python -c "from app import create_app; from app.utils.database_manager import db_manager; app = create_app(); app.app_context().push(); db_manager.create_tables()"
   ```

5. **Verify Setup**

   ```bash
   # Run tests to verify everything works
   pytest tests/ -v

   # Start development server
   python app_safe.py
   ```

6. **Access Application**
   - Web Interface: http://localhost:5000
   - API Docs: http://localhost:5000/api/info

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Storage       │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • Flask API     │◄──►│ • SQLite/       │
│ • Bootstrap UI  │    │ • Business      │    │   PostgreSQL    │
│ • JavaScript    │    │   Logic         │    │ • File Storage  │
│                 │    │ • ML Models     │    │ • Cache         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  External       │
                       │  Services       │
                       │                 │
                       │ • Email (SMTP)  │
                       │ • ML APIs       │
                       │ • Cloud Storage │
                       └─────────────────┘
```

### Key Technologies

- **Backend**: Flask 3.1.0, Python 3.11+
- **Database**: SQLite (default) or PostgreSQL
- **ML/NLP**: scikit-learn, transformers, sentence-transformers
- **File Processing**: PyPDF2, python-docx, pandas
- **Email**: smtplib, email-templates
- **Testing**: pytest, pytest-cov
- **Containerization**: Docker, Docker Compose
- **Cloud**: AWS ECS, Google Cloud Run

## 📁 Project Structure

```
resume-relevance-system/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models and schemas
│   │   ├── __init__.py
│   │   └── database_schema.py   # SQLAlchemy models
│   ├── routes/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── upload_routes.py     # File upload endpoints
│   │   ├── evaluation_routes.py # Resume evaluation endpoints
│   │   ├── database_routes.py   # Database CRUD endpoints
│   │   └── email_routes.py      # Email notification endpoints
│   └── utils/                   # Utility modules and business logic
│       ├── __init__.py
│       ├── resume_parser.py     # PDF/DOCX parsing
│       ├── relevance_analyzer.py # Core evaluation logic
│       ├── keyword_extractor.py # NLP keyword extraction
│       ├── skill_normalizer.py  # Skill standardization
│       ├── semantic_similarity.py # ML similarity scoring
│       ├── transformer_embeddings.py # BERT/transformer models
│       ├── database_manager.py  # Database operations
│       ├── email_sender.py      # Email delivery
│       ├── email_templates.py   # Template management
│       ├── feedback_generator.py # Recommendation engine
│       ├── advanced_scorer.py   # Advanced scoring algorithms
│       └── file_handler.py      # File I/O operations
├── templates/                   # Jinja2 HTML templates
│   ├── dashboard.html          # Main web interface
│   └── emails/                 # Email templates
│       ├── high_relevance.html
│       ├── medium_relevance.html
│       └── low_relevance.html
├── static/                     # Static web assets
│   ├── css/
│   │   └── dashboard.css       # Custom styles
│   └── js/
│       └── dashboard.js        # Frontend JavaScript
├── tests/                      # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures and configuration
│   ├── test_api.py            # API endpoint tests
│   ├── test_database.py       # Database operation tests
│   ├── test_integration.py    # End-to-end tests
│   ├── test_email_system.py   # Email functionality tests
│   ├── test_resume_parser.py  # File parsing tests
│   ├── test_skill_normalization.py # ML model tests
│   └── test_transformer_integration.py # Advanced ML tests
├── deployment/                 # Deployment scripts and configs
│   ├── deploy-docker.sh       # Local Docker deployment
│   ├── deploy-aws.sh          # AWS ECS deployment
│   ├── deploy-gcp.sh          # Google Cloud Run deployment
│   └── README.md              # Deployment documentation
├── config/                     # Configuration files
│   ├── nginx.conf             # Nginx reverse proxy config
│   └── prometheus.yml         # Monitoring configuration
├── data/                      # Database and data files
│   └── resume_relevance.db    # SQLite database (if used)
├── uploads/                   # File upload storage
│   ├── resumes/               # Uploaded resume files
│   └── job_descriptions/      # Uploaded job description files
├── embeddings_cache/          # ML model cache directory
├── scripts/                   # Database and utility scripts
│   └── init-db.sql           # Database initialization
├── docker-compose.yml         # Docker services orchestration
├── Dockerfile                 # Container build instructions
├── requirements_new.txt       # Production dependencies
├── requirements-test.txt      # Development and testing dependencies
├── pytest.ini                # Test configuration
├── .env                      # Environment variables (create from env_example.txt)
├── .gitignore                # Git ignore patterns
├── README.md                 # Main documentation
├── API_DOCUMENTATION.md      # Detailed API reference
└── DEVELOPER_DOCS.md         # This file
```

## 🧩 Core Components Deep Dive

### 1. Flask Application Factory (`app/__init__.py`)

The application uses the Flask factory pattern for better testability and configuration management:

```python
def create_app(config_override=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    load_configuration(app, config_override)

    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Setup error handlers
    register_error_handlers(app)

    return app
```

### 2. Resume Parser (`app/utils/resume_parser.py`)

Handles multiple file formats and extracts structured data:

```python
class ResumeParser:
    """Extract text and structured data from resume files"""

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse resume file and return structured data"""

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""

    def extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract experience information"""

    def extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information"""
```

### 3. Relevance Analyzer (`app/utils/relevance_analyzer.py`)

Core business logic for resume evaluation:

```python
class RelevanceAnalyzer:
    """Analyze resume relevance against job descriptions"""

    def analyze_relevance(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Perform comprehensive relevance analysis"""

    def calculate_skill_match(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """Calculate skill matching score and details"""

    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
```

### 4. Database Manager (`app/utils/database_manager.py`)

Centralized database operations with connection pooling:

```python
class DatabaseManager:
    """Manage database connections and operations"""

    def create_tables(self):
        """Initialize database tables"""

    def save_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """Save candidate information"""

    def search_candidates(self, query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search candidates with filters"""

    def get_analytics(self, period: str = '30days') -> Dict[str, Any]:
        """Generate analytics data"""
```

### 5. Email System (`app/utils/email_sender.py`)

Multi-provider email delivery with templating:

```python
class EmailSender:
    """Handle email delivery with multiple providers"""

    def send_evaluation_email(self, evaluation_data: Dict[str, Any],
                            recipient: str) -> Dict[str, Any]:
        """Send personalized evaluation email"""

    def render_template(self, template_name: str,
                       context: Dict[str, Any]) -> str:
        """Render email template with context"""
```

## 🔧 Development Workflow

### 1. Feature Development Process

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests First (TDD)**

   ```bash
   # Create test file
   touch tests/test_your_feature.py

   # Write failing tests
   pytest tests/test_your_feature.py -v
   ```

3. **Implement Feature**

   - Add route handler in appropriate `routes/` file
   - Add business logic in `utils/` modules
   - Update database models if needed

4. **Test Implementation**

   ```bash
   # Run specific tests
   pytest tests/test_your_feature.py -v

   # Run all tests
   pytest -x --tb=short

   # Check coverage
   pytest --cov=app --cov-report=html
   ```

5. **Update Documentation**

   - Update API_DOCUMENTATION.md for new endpoints
   - Update README.md if user-facing changes
   - Add docstrings to new functions/classes

6. **Code Review Checklist**
   - [ ] All tests pass
   - [ ] Code follows PEP 8 style
   - [ ] Functions have docstrings
   - [ ] Error handling implemented
   - [ ] Security considerations addressed
   - [ ] Performance impact evaluated

### 2. Testing Strategy

#### Test Categories

1. **Unit Tests** (`test_*.py` files)

   - Test individual functions and classes
   - Mock external dependencies
   - Fast execution, isolated tests

2. **Integration Tests** (`test_integration.py`)

   - Test component interactions
   - End-to-end workflows
   - Database and file system operations

3. **API Tests** (`test_api.py`)
   - Test all endpoints
   - Request validation
   - Response format verification

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m api               # API tests only

# Run specific test file
pytest tests/test_api.py -v

# Run specific test function
pytest tests/test_api.py::TestUploadEndpoints::test_upload_resume_success -v

# Debug failing test
pytest tests/test_api.py::test_function_name -v -s --pdb

# Parallel testing (faster)
pip install pytest-xdist
pytest -n auto
```

#### Writing Good Tests

```python
import pytest
from unittest.mock import Mock, patch
from tests.conftest import TestDataFactory

class TestResumeParser:
    """Test resume parsing functionality"""

    def test_parse_pdf_success(self, sample_pdf_resume):
        """Test successful PDF parsing"""
        parser = ResumeParser()
        result = parser.parse_file(sample_pdf_resume)

        assert result is not None
        assert 'text' in result
        assert 'skills' in result
        assert len(result['skills']) > 0

    @patch('app.utils.resume_parser.extract_text_from_pdf')
    def test_parse_pdf_failure(self, mock_extract):
        """Test PDF parsing failure handling"""
        mock_extract.side_effect = Exception("PDF corrupted")
        parser = ResumeParser()

        with pytest.raises(Exception, match="PDF corrupted"):
            parser.parse_file("corrupted.pdf")

    @pytest.mark.parametrize("file_type,expected_parser", [
        ("pdf", "PyPDF2"),
        ("docx", "python-docx"),
        ("txt", "text")
    ])
    def test_parser_selection(self, file_type, expected_parser):
        """Test correct parser selection for file types"""
        parser = ResumeParser()
        selected = parser._select_parser(f"file.{file_type}")
        assert expected_parser in str(selected)
```

### 3. Code Style and Standards

#### Python Code Style (PEP 8)

1. **Install Linting Tools**

   ```bash
   pip install black flake8 isort mypy
   ```

2. **Format Code**

   ```bash
   # Auto-format code
   black app/ tests/

   # Sort imports
   isort app/ tests/

   # Check style issues
   flake8 app/ tests/

   # Type checking
   mypy app/
   ```

3. **VS Code Configuration** (`.vscode/settings.json`)
   ```json
   {
     "python.formatting.provider": "black",
     "python.linting.flake8Enabled": true,
     "python.linting.mypyEnabled": true,
     "editor.formatOnSave": true,
     "python.sortImports.args": ["--profile", "black"]
   }
   ```

#### Code Standards

1. **Function Documentation**

   ```python
   def analyze_relevance(self, resume_text: str, job_text: str) -> Dict[str, Any]:
       """
       Analyze resume relevance against job description.

       Args:
           resume_text (str): The resume content to analyze
           job_text (str): The job description to match against

       Returns:
           Dict[str, Any]: Analysis results including:
               - relevance_score (float): Overall relevance score (0-100)
               - matched_skills (List[str]): Skills found in both
               - missing_skills (List[str]): Required skills not found
               - recommendations (List[str]): Improvement suggestions

       Raises:
           ValueError: If either text is empty
           ProcessingError: If analysis fails

       Example:
           >>> analyzer = RelevanceAnalyzer()
           >>> result = analyzer.analyze_relevance("resume text", "job text")
           >>> print(result['relevance_score'])
           85.5
       """
   ```

2. **Error Handling**

   ```python
   def upload_resume(file_path: str) -> Dict[str, Any]:
       """Upload and process resume file"""
       try:
           # Validate file
           if not os.path.exists(file_path):
               raise FileNotFoundError(f"Resume file not found: {file_path}")

           # Process file
           parser = ResumeParser()
           result = parser.parse_file(file_path)

           # Save to database
           candidate_id = self.db_manager.save_candidate(result)

           return {
               'success': True,
               'candidate_id': candidate_id,
               'message': 'Resume uploaded successfully'
           }

       except FileNotFoundError as e:
           logger.error(f"File not found: {e}")
           raise
       except ParsingError as e:
           logger.error(f"Resume parsing failed: {e}")
           raise
       except Exception as e:
           logger.error(f"Unexpected error uploading resume: {e}")
           raise ProcessingError("Failed to upload resume")
   ```

3. **Logging Standards**

   ```python
   import logging

   # Configure logger
   logger = logging.getLogger(__name__)

   # Use appropriate log levels
   logger.debug("Debug information for developers")
   logger.info("General information about program execution")
   logger.warning("Something unexpected happened, but still working")
   logger.error("Something went wrong")
   logger.critical("Serious error, program may not continue")

   # Include context in log messages
   logger.info(f"Processing resume for candidate {candidate_id}")
   logger.error(f"Failed to parse resume {file_path}: {str(e)}")
   ```

### 4. Database Development

#### Schema Changes

1. **Creating Migrations**

   ```python
   # In app/models/database_schema.py, modify models
   class Candidate:
       # Add new field
       linkedin_url = Column(String(255), nullable=True)
   ```

2. **Manual Migration Script**

   ```python
   # scripts/migrate_add_linkedin.py
   from app.utils.database_manager import db_manager

   def add_linkedin_column():
       """Add linkedin_url column to candidates table"""
       with db_manager.get_connection() as conn:
           conn.execute("""
               ALTER TABLE candidates
               ADD COLUMN linkedin_url VARCHAR(255)
           """)

   if __name__ == "__main__":
       add_linkedin_column()
       print("Migration completed successfully")
   ```

#### Database Testing

```python
import pytest
from app.utils.database_manager import DatabaseManager

class TestDatabaseOperations:
    """Test database operations"""

    @pytest.fixture
    def db_manager(self):
        """Create test database manager"""
        manager = DatabaseManager(database_url="sqlite:///:memory:")
        manager.create_tables()
        return manager

    def test_save_candidate(self, db_manager):
        """Test saving candidate to database"""
        candidate_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'skills': ['Python', 'Flask']
        }

        candidate_id = db_manager.save_candidate(candidate_data)
        assert candidate_id is not None

        # Verify saved data
        saved_candidate = db_manager.get_candidate(candidate_id)
        assert saved_candidate['name'] == 'John Doe'
        assert saved_candidate['email'] == 'john@example.com'
```

## 🚀 Performance Optimization

### 1. Application Performance

#### Profiling Code

```python
import cProfile
import pstats

def profile_function():
    """Profile a specific function"""
    pr = cProfile.Profile()
    pr.enable()

    # Your code here
    result = analyze_relevance(resume_text, job_text)

    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

    return result
```

#### Memory Usage Monitoring

```python
import tracemalloc

def memory_usage_example():
    """Monitor memory usage"""
    tracemalloc.start()

    # Your memory-intensive code
    large_data = process_large_resume_batch()

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

    tracemalloc.stop()
```

### 2. Database Optimization

#### Query Optimization

```python
# Good: Use indexes and specific queries
def search_candidates_optimized(skills: List[str], limit: int = 20):
    """Optimized candidate search with indexes"""
    # Use database indexes on skills and created_at
    query = """
        SELECT c.*, COUNT(cs.skill) as skill_matches
        FROM candidates c
        JOIN candidate_skills cs ON c.id = cs.candidate_id
        WHERE cs.skill IN %s
        GROUP BY c.id
        HAVING skill_matches >= %s
        ORDER BY skill_matches DESC, c.created_at DESC
        LIMIT %s
    """
    return execute_query(query, (tuple(skills), len(skills)//2, limit))

# Bad: N+1 queries and no pagination
def search_candidates_slow(skills: List[str]):
    """Avoid: Slow candidate search"""
    candidates = get_all_candidates()  # Loads entire table
    matches = []
    for candidate in candidates:  # N+1 queries
        candidate_skills = get_candidate_skills(candidate.id)
        if any(skill in candidate_skills for skill in skills):
            matches.append(candidate)
    return matches
```

#### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Configure connection pooling
engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,        # Number of connections to maintain
    max_overflow=20,     # Additional connections under high load
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600    # Recycle connections every hour
)
```

### 3. Caching Strategies

#### In-Memory Caching

```python
from functools import lru_cache
from typing import Dict, Any

class RelevanceAnalyzer:
    @lru_cache(maxsize=128)
    def _get_skill_embeddings(self, skills_tuple: tuple) -> Dict[str, Any]:
        """Cache skill embeddings for reuse"""
        skills = list(skills_tuple)
        # Expensive ML computation
        return self.transformer_model.encode(skills)

    def analyze_with_cache(self, resume_skills: List[str], job_skills: List[str]):
        """Use cached embeddings when possible"""
        resume_embeddings = self._get_skill_embeddings(tuple(sorted(resume_skills)))
        job_embeddings = self._get_skill_embeddings(tuple(sorted(job_skills)))

        return self.compute_similarity(resume_embeddings, job_embeddings)
```

#### Redis Caching

```python
import redis
import json
from typing import Optional

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)

    def get_evaluation(self, resume_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        """Get cached evaluation result"""
        cache_key = f"evaluation:{resume_id}:{job_id}"
        cached_result = self.redis_client.get(cache_key)

        if cached_result:
            return json.loads(cached_result)
        return None

    def cache_evaluation(self, resume_id: str, job_id: str,
                        result: Dict[str, Any], ttl: int = 3600):
        """Cache evaluation result"""
        cache_key = f"evaluation:{resume_id}:{job_id}"
        self.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(result, default=str)
        )
```

## 🐛 Debugging and Troubleshooting

### 1. Common Issues and Solutions

#### Issue: "ModuleNotFoundError"

```bash
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements_new.txt
```

#### Issue: "Database connection failed"

```python
# Debug database connectivity
from app.utils.database_manager import DatabaseManager

def debug_database():
    try:
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        print("Database connection successful")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Check your DATABASE_URL in .env file")
```

#### Issue: "Email sending fails"

```python
# Debug email configuration
def debug_email():
    from app.utils.email_sender import EmailSender

    try:
        sender = EmailSender()
        result = sender.send_test_email("test@example.com")
        print("Email test successful")
    except Exception as e:
        print(f"Email test failed: {e}")
        print("Check your email configuration in .env file")
```

### 2. Logging and Monitoring

#### Development Logging

```python
# config/logging.py
import logging
import sys

def setup_logging(debug_mode: bool = False):
    """Setup application logging"""
    level = logging.DEBUG if debug_mode else logging.INFO

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

#### Request Debugging Middleware

```python
from flask import request, g
import time
import logging

def log_request_info():
    """Log request details for debugging"""
    g.start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url}")

def log_request_completion(response):
    """Log request completion details"""
    duration = time.time() - g.start_time
    logger.info(
        f"Request completed: {request.method} {request.url} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    return response
```

### 3. Testing in Different Environments

#### Local Development

```bash
# Set environment for local development
export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///data/resume_relevance_dev.db

python app_safe.py
```

#### Staging Environment

```bash
# Use staging configuration
export FLASK_ENV=staging
export DATABASE_URL=postgresql://user:pass@staging-db:5432/resume_relevance
export EMAIL_PROVIDER=sendgrid
export SENDGRID_API_KEY=staging-key

python app_safe.py
```

#### Production Testing

```bash
# Use production-like configuration
export FLASK_ENV=production
export FLASK_DEBUG=0
export DATABASE_URL=postgresql://user:pass@prod-db:5432/resume_relevance

# Run with gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
```

## 🔐 Security Best Practices

### 1. Input Validation

```python
from flask import request, jsonify
from marshmallow import Schema, fields, validate, ValidationError

class CandidateSchema(Schema):
    """Validate candidate data"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(validate=validate.Length(max=20))
    skills = fields.List(fields.Str(), validate=validate.Length(max=50))

def create_candidate():
    """Create candidate with validation"""
    schema = CandidateSchema()

    try:
        # Validate input data
        validated_data = schema.load(request.json)

        # Process validated data
        candidate_id = db_manager.save_candidate(validated_data)

        return jsonify({'success': True, 'candidate_id': candidate_id})

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': e.messages
        }), 400
```

### 2. File Upload Security

```python
import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file_upload(file):
    """Secure file upload with validation"""
    if not file:
        raise ValueError("No file provided")

    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")

    if file.content_length and file.content_length > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Secure filename
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename")

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{filename}"

    return unique_filename
```

### 3. SQL Injection Prevention

```python
# Good: Use parameterized queries
def search_candidates_secure(query: str, limit: int):
    """Secure candidate search"""
    sql = """
        SELECT * FROM candidates
        WHERE name ILIKE %s OR email ILIKE %s
        LIMIT %s
    """
    params = (f"%{query}%", f"%{query}%", limit)
    return execute_query(sql, params)

# Bad: String concatenation (vulnerable to SQL injection)
def search_candidates_insecure(query: str):
    """NEVER DO THIS - Vulnerable to SQL injection"""
    sql = f"SELECT * FROM candidates WHERE name LIKE '%{query}%'"
    return execute_query(sql)
```

## 📚 Additional Resources

### 1. Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **pytest Testing**: https://docs.pytest.org/
- **Docker Documentation**: https://docs.docker.com/
- **Python Best Practices**: https://realpython.com/

### 2. Useful Tools

#### Development Tools

- **VS Code Extensions**:

  - Python (Microsoft)
  - Python Docstring Generator
  - GitLens
  - Docker
  - REST Client

- **Command Line Tools**:

  ```bash
  # Code quality
  pip install black flake8 isort mypy

  # Security scanning
  pip install safety bandit

  # Documentation
  pip install sphinx sphinx-rtd-theme
  ```

#### Debugging Tools

```python
# Debug with IPython
import IPython; IPython.embed()

# Debug with pdb
import pdb; pdb.set_trace()

# Debug with ipdb (better interface)
import ipdb; ipdb.set_trace()
```

### 3. Community and Support

- **GitHub Issues**: Report bugs and feature requests
- **Stack Overflow**: Tag questions with `resume-relevance-system`
- **Developer Discussions**: Join GitHub Discussions
- **Code Reviews**: Submit PRs for community review

## 🤝 Contributing Guidelines

### 1. Code Contribution Process

1. **Fork and Clone**

   ```bash
   # Fork on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/resume-relevance-system.git
   cd resume-relevance-system
   git remote add upstream https://github.com/ORIGINAL_OWNER/resume-relevance-system.git
   ```

2. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**

   - Write tests first (TDD approach)
   - Implement feature
   - Update documentation
   - Run tests and linting

4. **Commit Changes**

   ```bash
   # Use conventional commit format
   git commit -m "feat: add resume batch processing endpoint"
   git commit -m "fix: resolve email template rendering issue"
   git commit -m "docs: update API documentation for new endpoint"
   ```

5. **Submit Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

### 2. Code Review Checklist

#### For Authors

- [ ] All tests pass locally
- [ ] Code follows style guidelines (black, flake8)
- [ ] New functions have docstrings
- [ ] API changes documented
- [ ] Breaking changes noted
- [ ] Security implications considered

#### For Reviewers

- [ ] Code is readable and maintainable
- [ ] Test coverage is adequate
- [ ] Error handling is appropriate
- [ ] Security best practices followed
- [ ] Performance impact acceptable
- [ ] Documentation is complete

### 3. Release Process

1. **Version Bumping**

   ```python
   # Update version in app/__init__.py
   __version__ = "1.1.0"
   ```

2. **Create Release Branch**

   ```bash
   git checkout -b release/v1.1.0
   ```

3. **Update Changelog**

   ```markdown
   ## [1.1.0] - 2024-01-15

   ### Added

   - New batch processing endpoint
   - Enhanced email templates

   ### Fixed

   - Resume parsing error handling
   - Database connection pooling

   ### Changed

   - Improved ML model accuracy
   ```

4. **Test Release**

   ```bash
   # Run full test suite
   pytest tests/ --cov=app --cov-report=html

   # Test Docker build
   docker build -t resume-relevance-system:v1.1.0 .

   # Test deployment scripts
   ./deployment/deploy-docker.sh -t
   ```

---

_Happy coding! 🚀 If you have questions or need help, don't hesitate to reach out to the development team or open an issue on GitHub._

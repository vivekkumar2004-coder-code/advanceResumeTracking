# Database System Documentation

## Overview

The Resume Relevance System includes a comprehensive database layer for persistent storage of candidates, job descriptions, evaluations, and LLM-generated feedback. The system supports both PostgreSQL (production) and SQLite (development/testing) databases.

## Architecture

### Database Schema

The system uses 7 main tables with proper relationships:

1. **Candidates** - Store candidate information and parsed resume data
2. **JobDescriptions** - Store job postings and requirements
3. **Evaluations** - Store evaluation results and scores
4. **ComponentScores** - Store detailed component breakdowns
5. **FeedbackRecords** - Store LLM-generated feedback
6. **AuditLogs** - Track all system activities
7. **SystemMetrics** - Store performance and usage metrics

### Key Features

- **Multi-Database Support**: PostgreSQL and SQLite
- **Business Logic Managers**: High-level operations with validation
- **Audit Trail**: Complete activity logging
- **Search Functionality**: Full-text search across entities
- **Analytics**: Built-in statistics and reporting
- **RESTful API**: Complete CRUD operations
- **Migration Support**: Flask-Migrate for schema changes

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_TYPE=sqlite  # or postgresql
DB_PATH=data/resume_relevance.db  # for SQLite
DB_HOST=localhost  # for PostgreSQL
DB_PORT=5432  # for PostgreSQL
DB_NAME=resume_relevance  # for PostgreSQL
DB_USER=postgres  # for PostgreSQL
DB_PASSWORD=your_password  # for PostgreSQL

# Connection Pooling (PostgreSQL)
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_MAX_OVERFLOW=20

# Debugging
DB_ECHO=false  # Set to true to see SQL queries
DB_RECORD_QUERIES=false  # Record queries for analysis
```

### SQLite Configuration (Default)

```python
# Minimal setup for development
os.environ['DATABASE_TYPE'] = 'sqlite'
os.environ['DB_PATH'] = 'data/resume_relevance.db'
```

### PostgreSQL Configuration

```python
# Production setup
os.environ['DATABASE_TYPE'] = 'postgresql'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'resume_relevance'
os.environ['DB_USER'] = 'your_user'
os.environ['DB_PASSWORD'] = 'your_password'
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```python
from app import create_app
from app.utils.database_manager import db_manager

app = create_app()
with app.app_context():
    db_manager.create_tables()
```

### 3. Run the Application

```bash
python app.py
```

### 4. Test the System

```bash
python demo_database_system.py
```

## API Endpoints

### Candidate Management

```http
POST /api/database/candidates
GET /api/database/candidates/<id>
GET /api/database/candidates/search?q=python
GET /api/database/candidates/<id>/evaluations
```

### Job Description Management

```http
POST /api/database/jobs
GET /api/database/jobs
GET /api/database/jobs/<id>
GET /api/database/jobs/<id>/evaluations
GET /api/database/jobs/<id>/top-candidates
```

### Evaluation Management

```http
POST /api/database/evaluations
GET /api/database/evaluations/<id>
GET /api/database/evaluations/statistics
```

### Feedback Management

```http
POST /api/database/feedback
GET /api/database/candidates/<id>/feedback
```

### Analytics and Monitoring

```http
GET /api/database/health
GET /api/database/analytics/dashboard
GET /api/database/audit/<entity_type>/<entity_id>
```

## Usage Examples

### Creating a Candidate

```python
from app.models import CandidateManager

candidate_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john.doe@email.com',
    'skills': ['Python', 'Machine Learning'],
    'work_experience': [...],
    'education': [...],
    'total_experience_years': 5
}

candidate = CandidateManager.create_candidate(candidate_data)
```

### Saving an Evaluation

```python
from app.models import EvaluationManager

evaluation_data = {
    'candidate_id': candidate.id,
    'job_description_id': job.id,
    'overall_score': 85.5,
    'suitability_verdict': 'HIGH',
    'confidence_level': 'high',
    'component_scores': {...},
    'strengths': [...],
    'weaknesses': [...]
}

evaluation = EvaluationManager.create_evaluation(evaluation_data)
```

### Storing Feedback

```python
from app.models import FeedbackManager

feedback_data = {
    'candidate_id': candidate.id,
    'evaluation_id': evaluation.id,
    'feedback_type': 'comprehensive',
    'feedback_tone': 'professional',
    'llm_provider': 'openai',
    'executive_summary': '...',
    'strengths': [...],
    'areas_for_improvement': [...],
    'skill_recommendations': [...]
}

feedback = FeedbackManager.create_feedback_record(feedback_data)
```

## Business Logic Managers

### CandidateManager

```python
# Create candidate
candidate = CandidateManager.create_candidate(data)

# Search candidates
results = CandidateManager.search_candidates("python", limit=50)

# Get candidate with evaluations
candidate = CandidateManager.get_candidate_by_id(id)

# Update candidate
updated = CandidateManager.update_candidate(id, update_data)
```

### EvaluationManager

```python
# Get top candidates for a job
top_candidates = EvaluationManager.get_top_candidates(job_id, limit=10)

# Get evaluation statistics
stats = EvaluationManager.get_evaluation_statistics(job_id)

# Get candidate's evaluation history
evaluations = EvaluationManager.get_candidate_evaluations(candidate_id)
```

### AuditManager

```python
# Log activity
AuditManager.log_activity(
    action='CREATE',
    entity_type='candidate',
    entity_id=candidate.id,
    user_id='system',
    success=True
)

# Get audit trail
audit_logs = AuditManager.get_entity_audit_trail('candidate', candidate.id)
```

## Database Schema Details

### Candidate Table

- Personal information (name, email, phone, location)
- Resume file details (filename, path, size, mime_type)
- Parsed resume data (JSON field)
- Skills, experience, education (JSON fields)
- Professional profile information
- Metadata (source, tags, notes, timestamps)

### JobDescription Table

- Basic job info (title, company, department, location)
- Job details (description, responsibilities, requirements)
- Skills and experience requirements (JSON fields)
- Compensation and benefits (JSON fields)
- Application details (deadline, URL, internal ID)
- Status and metadata

### Evaluation Table

- Foreign keys to candidate and job
- Overall scores and verdict
- Component scores (JSON field)
- Analysis details (semantic similarity, experience match)
- Processing metadata (time, method, version)
- Strengths, weaknesses, recommendations (JSON fields)

### FeedbackRecord Table

- LLM configuration (provider, model, tone)
- Comprehensive feedback content (JSON fields)
- Executive summary and recommendations
- Processing metadata (time, tokens, cost)
- Quality assessment

## Performance Considerations

### Indexing Strategy

```sql
-- Automatic indexes on primary keys and foreign keys
-- Additional indexes for search performance
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_skills ON candidates USING GIN(skills);
CREATE INDEX idx_evaluations_score ON evaluations(overall_score);
CREATE INDEX idx_evaluations_created ON evaluations(created_at);
```

### Query Optimization

- Use `joinedload()` for eager loading relationships
- Implement pagination for large result sets
- Use database-level constraints for data integrity
- Connection pooling for high concurrency

### Caching Strategy

```python
# Example: Cache frequently accessed data
@lru_cache(maxsize=100)
def get_job_requirements(job_id):
    job = JobDescriptionManager.get_job_by_id(job_id)
    return job.required_skills_list if job else []
```

## Migration and Deployment

### Database Migrations

```bash
# Initialize migration repository
flask db init

# Create migration
flask db migrate -m "Add new column"

# Apply migration
flask db upgrade
```

### Production Deployment

1. **PostgreSQL Setup**:

   ```sql
   CREATE DATABASE resume_relevance;
   CREATE USER resume_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE resume_relevance TO resume_user;
   ```

2. **Environment Configuration**:

   ```bash
   export DATABASE_TYPE=postgresql
   export DB_HOST=your-db-host
   export DB_NAME=resume_relevance
   export DB_USER=resume_user
   export DB_PASSWORD=secure_password
   ```

3. **Connection Pooling**:
   ```bash
   export DB_POOL_SIZE=20
   export DB_MAX_OVERFLOW=30
   export DB_POOL_TIMEOUT=60
   ```

## Monitoring and Maintenance

### Health Checks

```bash
# Test database connectivity
curl http://localhost:5000/api/database/health

# Get system statistics
curl http://localhost:5000/api/database/analytics/dashboard
```

### Backup and Recovery

```python
# SQLite backup (built-in)
backup_info = db_manager.backup_database()

# PostgreSQL backup (external tools)
# pg_dump -U user -h host database_name > backup.sql
```

### Performance Monitoring

```python
# Enable query logging
os.environ['DB_RECORD_QUERIES'] = 'true'
os.environ['DB_ECHO'] = 'true'  # Development only

# Monitor slow queries
from flask import g
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.5:  # Log slow queries
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}")
```

## Security Considerations

### Data Protection

- Use parameterized queries (SQLAlchemy ORM handles this)
- Implement proper access controls
- Encrypt sensitive data at rest
- Use SSL/TLS for database connections
- Regular security audits and updates

### Input Validation

```python
# Example validation in managers
def create_candidate(self, data):
    # Validate email format
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data.get('email', '')):
        raise ValueError("Invalid email format")

    # Sanitize file paths
    if 'resume_file_path' in data:
        data['resume_file_path'] = os.path.normpath(data['resume_file_path'])

    return super().create_candidate(data)
```

## Troubleshooting

### Common Issues

1. **Connection Errors**:

   - Check database service status
   - Verify connection parameters
   - Test network connectivity

2. **Migration Failures**:

   - Review migration files
   - Check for data conflicts
   - Backup before applying migrations

3. **Performance Issues**:
   - Analyze slow query logs
   - Review index usage
   - Check connection pool settings

### Debugging Tools

```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Database introspection
from sqlalchemy import inspect
inspector = inspect(db.engine)
print(inspector.get_table_names())
```

## Testing

### Unit Tests

```python
def test_candidate_creation():
    with app.app_context():
        candidate_data = {...}
        candidate = CandidateManager.create_candidate(candidate_data)
        assert candidate.email == candidate_data['email']
```

### Integration Tests

```python
def test_complete_workflow():
    # Create candidate
    # Create job
    # Create evaluation
    # Create feedback
    # Verify relationships
```

### Performance Tests

```python
def test_search_performance():
    start_time = time.time()
    results = CandidateManager.search_candidates("python", limit=100)
    duration = time.time() - start_time
    assert duration < 1.0  # Should complete within 1 second
```

## Best Practices

1. **Use Managers**: Always use business logic managers instead of direct model access
2. **Transaction Management**: Use database transactions for multi-step operations
3. **Error Handling**: Implement comprehensive error handling and logging
4. **Data Validation**: Validate all input data before database operations
5. **Audit Everything**: Log all significant operations for compliance
6. **Monitor Performance**: Regular performance monitoring and optimization
7. **Backup Strategy**: Implement regular automated backups
8. **Security Updates**: Keep database software and dependencies updated

This database system provides a solid foundation for the Resume Relevance System with production-ready features for scalability, reliability, and maintainability.

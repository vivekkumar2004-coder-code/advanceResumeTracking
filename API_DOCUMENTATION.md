# 📖 Resume Relevance System - API Documentation

## Overview

The Resume Relevance System provides a comprehensive REST API for automated resume evaluation, candidate management, email notifications, and analytics. This document provides detailed information about all available endpoints, including request formats, response structures, and example usage.

## Base Information

- **Base URL**: `http://localhost:5000` (development) or your production domain
- **API Version**: v1
- **Content-Type**: `application/json` (unless otherwise specified)
- **Authentication**: Currently not required (add API keys for production)

## Response Format

All API responses follow a consistent structure:

### Success Response

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_TYPE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `FILE_ERROR`: File processing error
- `DATABASE_ERROR`: Database operation failed
- `EMAIL_ERROR`: Email sending failed
- `INTERNAL_ERROR`: Server internal error
- `NOT_FOUND`: Resource not found

## 📁 File Upload Endpoints

### Upload Resume

Upload a resume file or text content for analysis.

**Endpoint**: `POST /api/upload/resume`

**Content-Type**: `multipart/form-data` (for files) or `application/json` (for text)

#### File Upload Request

```bash
curl -X POST "http://localhost:5000/api/upload/resume" \
  -F "file=@resume.pdf"
```

#### Text Upload Request

```bash
curl -X POST "http://localhost:5000/api/upload/resume" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe\nSoftware Engineer\n\nExperience:\n- 3 years Python development\n- Flask web applications\n- PostgreSQL databases\n\nSkills:\n- Python\n- Flask\n- PostgreSQL\n- Docker\n- Git"
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "file_id": "resume_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "resume_a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf",
    "file_type": "pdf",
    "file_size": 245760,
    "upload_time": "2024-01-15T10:30:00Z",
    "preview": "John Doe\nSoftware Engineer\n\nExperience:\n3 years of experience..."
  },
  "message": "Resume uploaded successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Upload Job Description

Upload a job description file or provide text content.

**Endpoint**: `POST /api/upload/job-description`

**Content-Type**: `multipart/form-data` (for files) or `application/json` (for text)

#### File Upload Request

```bash
curl -X POST "http://localhost:5000/api/upload/job-description" \
  -F "file=@job_description.txt"
```

#### Text Upload Request

```bash
curl -X POST "http://localhost:5000/api/upload/job-description" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Senior Python Developer\n\nWe are looking for an experienced Python developer to join our team.\n\nRequired Skills:\n- Python 3.8+\n- Flask or Django\n- PostgreSQL\n- Docker\n- Git\n- REST API development\n\nPreferred Skills:\n- AWS\n- Kubernetes\n- Machine Learning",
    "job_title": "Senior Python Developer",
    "company_name": "Tech Corporation"
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "file_id": "job_b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "filename": "job_description_b2c3d4e5-f6g7-8901-bcde-f23456789012.txt",
    "file_type": "txt",
    "file_size": 1024,
    "upload_time": "2024-01-15T10:30:00Z",
    "job_title": "Senior Python Developer",
    "company_name": "Tech Corporation",
    "preview": "Senior Python Developer\n\nWe are looking for an experienced..."
  },
  "message": "Job description uploaded successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### List Uploaded Files

Retrieve a list of all uploaded files.

**Endpoint**: `GET /api/files`

#### Request

```bash
curl "http://localhost:5000/api/files?type=resume&limit=10&offset=0"
```

#### Query Parameters

- `type` (optional): Filter by file type (`resume`, `job_description`)
- `limit` (optional): Number of results to return (default: 50)
- `offset` (optional): Number of results to skip (default: 0)

#### Response

```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "resume_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "filename": "resume_a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf",
        "file_type": "pdf",
        "upload_time": "2024-01-15T10:30:00Z",
        "file_size": 245760,
        "content_type": "resume"
      }
    ],
    "total_count": 25,
    "limit": 10,
    "offset": 0
  },
  "message": "Files retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🧠 Evaluation Endpoints

### Evaluate Resume

Perform resume relevance analysis against a job description.

**Endpoint**: `POST /api/evaluate`

#### Request

```bash
curl -X POST "http://localhost:5000/api/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "resume_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "job_id": "job_b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "evaluation_options": {
      "use_transformers": true,
      "detailed_analysis": true,
      "include_recommendations": true
    }
  }'
```

#### Request Body Parameters

- `resume_id` (required): ID of the uploaded resume
- `job_id` (required): ID of the uploaded job description
- `evaluation_options` (optional): Configuration options for evaluation

#### Response

```json
{
  "success": true,
  "data": {
    "evaluation_id": "eval_789xyz123-abc4-5678-90de-f12345678901",
    "resume_id": "resume_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "job_id": "job_b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "relevance_score": 85.5,
    "relevance_level": "high",
    "evaluation_time": "2024-01-15T10:30:00Z",
    "total_matching_skills": 7,
    "total_job_skills": 10,
    "skill_match_percentage": 70.0,
    "matched_skills": [
      "Python",
      "Flask",
      "PostgreSQL",
      "Docker",
      "Git",
      "REST API",
      "Web Development"
    ],
    "missing_skills": ["AWS", "Kubernetes", "Machine Learning"],
    "strengths": [
      "Strong technical background in Python development",
      "Relevant experience with web frameworks (Flask)",
      "Database design and management skills",
      "Experience with containerization (Docker)",
      "Version control proficiency"
    ],
    "recommendations": [
      "Consider learning containerization orchestration with Kubernetes",
      "Gain experience with cloud platforms like AWS",
      "Develop machine learning skills to enhance data analysis capabilities",
      "Build expertise in microservices architecture"
    ],
    "detailed_analysis": {
      "technical_skills": {
        "score": 90,
        "weight": 0.4,
        "details": "Excellent match for core technical requirements"
      },
      "experience": {
        "score": 85,
        "weight": 0.3,
        "details": "Good experience level for the role requirements"
      },
      "education": {
        "score": 80,
        "weight": 0.2,
        "details": "Relevant educational background"
      },
      "soft_skills": {
        "score": 75,
        "weight": 0.1,
        "details": "Evidence of communication and teamwork skills"
      }
    },
    "keyword_analysis": {
      "total_keywords": 25,
      "matched_keywords": 18,
      "keyword_match_rate": 72.0,
      "top_matched_keywords": [
        { "keyword": "Python", "frequency": 12, "importance": 0.95 },
        { "keyword": "Flask", "frequency": 8, "importance": 0.85 },
        { "keyword": "PostgreSQL", "frequency": 5, "importance": 0.8 }
      ]
    },
    "transformer_similarity": {
      "semantic_similarity": 0.847,
      "model_used": "all-MiniLM-L6-v2",
      "confidence": 0.92
    }
  },
  "message": "Resume evaluation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Get Evaluation Details

Retrieve detailed information about a specific evaluation.

**Endpoint**: `GET /api/evaluate/{evaluation_id}`

#### Request

```bash
curl "http://localhost:5000/api/evaluate/eval_789xyz123-abc4-5678-90de-f12345678901"
```

#### Response

Returns the same structure as the evaluate endpoint response.

### Analyze Keywords

Extract and analyze keywords from a job description.

**Endpoint**: `POST /api/analyze-keywords`

#### Request

```bash
curl -X POST "http://localhost:5000/api/analyze-keywords" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job_b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "analysis_options": {
      "extract_skills": true,
      "extract_requirements": true,
      "importance_scoring": true
    }
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "job_id": "job_b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "total_keywords": 35,
    "technical_skills": [
      { "skill": "Python", "importance": 0.95, "frequency": 8 },
      { "skill": "Flask", "importance": 0.85, "frequency": 3 },
      { "skill": "PostgreSQL", "importance": 0.8, "frequency": 2 }
    ],
    "soft_skills": [
      { "skill": "Communication", "importance": 0.7, "frequency": 2 },
      { "skill": "Team Collaboration", "importance": 0.65, "frequency": 1 }
    ],
    "requirements": [
      "3+ years of Python experience",
      "Experience with web frameworks",
      "Database design knowledge",
      "Version control proficiency"
    ],
    "preferred_qualifications": [
      "AWS cloud experience",
      "Kubernetes knowledge",
      "Machine learning background"
    ],
    "keyword_categories": {
      "programming_languages": ["Python", "JavaScript"],
      "frameworks": ["Flask", "Django"],
      "databases": ["PostgreSQL", "MongoDB"],
      "tools": ["Docker", "Git", "Jenkins"],
      "cloud_platforms": ["AWS", "Azure", "GCP"]
    }
  },
  "message": "Keyword analysis completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 💾 Database Endpoints

### Candidate Management

#### Create Candidate

**Endpoint**: `POST /api/database/candidates`

#### Request

```bash
curl -X POST "http://localhost:5000/api/database/candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "resume_text": "Experienced Python developer with 3+ years...",
    "skills": ["Python", "Flask", "PostgreSQL", "Docker"],
    "experience_years": 3,
    "education": "Bachelor of Science in Computer Science",
    "location": "San Francisco, CA",
    "current_position": "Software Engineer",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "portfolio_url": "https://johndoe.dev"
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "candidate_id": "cand_123e4567-e89b-12d3-a456-426614174000",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "skills": ["Python", "Flask", "PostgreSQL", "Docker"],
    "experience_years": 3,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Candidate created successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Get Candidate Details

**Endpoint**: `GET /api/database/candidates/{candidate_id}`

#### Request

```bash
curl "http://localhost:5000/api/database/candidates/cand_123e4567-e89b-12d3-a456-426614174000"
```

#### Search Candidates

**Endpoint**: `GET /api/database/candidates/search`

#### Request

```bash
curl "http://localhost:5000/api/database/candidates/search?q=python&skills=Flask,PostgreSQL&experience_min=2&location=San Francisco&limit=10"
```

#### Query Parameters

- `q` (optional): Search query (searches name, email, skills, resume text)
- `skills` (optional): Comma-separated list of required skills
- `experience_min` (optional): Minimum years of experience
- `experience_max` (optional): Maximum years of experience
- `location` (optional): Location filter
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Offset for pagination (default: 0)

#### Response

```json
{
  "success": true,
  "data": {
    "candidates": [
      {
        "candidate_id": "cand_123e4567-e89b-12d3-a456-426614174000",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "skills": ["Python", "Flask", "PostgreSQL", "Docker"],
        "experience_years": 3,
        "location": "San Francisco, CA",
        "match_score": 0.95
      }
    ],
    "total_count": 1,
    "limit": 10,
    "offset": 0
  },
  "message": "Candidates retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Job Management

#### Create Job

**Endpoint**: `POST /api/database/jobs`

#### Request

```bash
curl -X POST "http://localhost:5000/api/database/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company_name": "Tech Corporation",
    "description": "We are looking for an experienced Python developer...",
    "required_skills": ["Python", "Flask", "PostgreSQL"],
    "preferred_skills": ["AWS", "Docker", "Kubernetes"],
    "experience_required": "3-5 years",
    "location": "San Francisco, CA",
    "employment_type": "full-time",
    "remote_allowed": true,
    "salary_min": 100000,
    "salary_max": 140000,
    "posted_date": "2024-01-15",
    "application_deadline": "2024-02-15",
    "department": "Engineering",
    "job_level": "senior"
  }'
```

#### Response

```json
{
  "success": true,
  "data": {
    "job_id": "job_234f5678-f90c-23e4-b567-537725285111",
    "title": "Senior Python Developer",
    "company_name": "Tech Corporation",
    "required_skills": ["Python", "Flask", "PostgreSQL"],
    "preferred_skills": ["AWS", "Docker", "Kubernetes"],
    "location": "San Francisco, CA",
    "employment_type": "full-time",
    "created_at": "2024-01-15T10:30:00Z",
    "status": "active"
  },
  "message": "Job created successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### List Active Jobs

**Endpoint**: `GET /api/database/jobs`

#### Request

```bash
curl "http://localhost:5000/api/database/jobs?location=San Francisco&skills=Python&remote=true&limit=10"
```

### Evaluation History

#### Save Evaluation

**Endpoint**: `POST /api/database/evaluations`

#### Request

```bash
curl -X POST "http://localhost:5000/api/database/evaluations" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "eval_789xyz123-abc4-5678-90de-f12345678901",
    "candidate_id": "cand_123e4567-e89b-12d3-a456-426614174000",
    "job_id": "job_234f5678-f90c-23e4-b567-537725285111",
    "relevance_score": 85.5,
    "matched_skills": ["Python", "Flask", "PostgreSQL"],
    "missing_skills": ["AWS", "Kubernetes"],
    "recommendations": ["Learn AWS", "Gain Kubernetes experience"],
    "evaluation_details": {
      "technical_score": 90,
      "experience_score": 85,
      "education_score": 80
    }
  }'
```

### Analytics

#### Get Dashboard Analytics

**Endpoint**: `GET /api/database/analytics/dashboard`

#### Request

```bash
curl "http://localhost:5000/api/database/analytics/dashboard?period=30days"
```

#### Query Parameters

- `period` (optional): Time period (`7days`, `30days`, `90days`, `1year`)

#### Response

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_candidates": 1250,
      "total_jobs": 85,
      "total_evaluations": 3420,
      "avg_relevance_score": 72.5,
      "evaluations_this_period": 245
    },
    "score_distribution": {
      "high_relevance": 412,
      "medium_relevance": 1876,
      "low_relevance": 1132
    },
    "top_skills": [
      { "skill": "Python", "count": 890, "avg_score": 82.1 },
      { "skill": "JavaScript", "count": 654, "avg_score": 75.8 },
      { "skill": "Java", "count": 432, "avg_score": 78.2 }
    ],
    "evaluation_trends": [
      { "date": "2024-01-08", "count": 35, "avg_score": 74.2 },
      { "date": "2024-01-09", "count": 42, "avg_score": 71.8 },
      { "date": "2024-01-10", "count": 38, "avg_score": 76.5 }
    ],
    "job_performance": [
      {
        "job_id": "job_234f5678-f90c-23e4-b567-537725285111",
        "title": "Senior Python Developer",
        "applications": 156,
        "avg_relevance": 81.3,
        "high_relevance_count": 45
      }
    ]
  },
  "message": "Analytics data retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📧 Email Endpoints

### Send Evaluation Email

Send personalized evaluation results to candidates.

**Endpoint**: `POST /api/email/send-evaluation`

#### Request

```bash
curl -X POST "http://localhost:5000/api/email/send-evaluation" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "eval_789xyz123-abc4-5678-90de-f12345678901",
    "candidate_email": "john.doe@example.com",
    "candidate_name": "John Doe",
    "job_title": "Senior Python Developer",
    "company_name": "Tech Corporation",
    "email_options": {
      "include_feedback": true,
      "include_recommendations": true,
      "template": "auto"
    }
  }'
```

#### Request Parameters

- `evaluation_id` (required): ID of the evaluation
- `candidate_email` (required): Candidate's email address
- `candidate_name` (required): Candidate's name
- `job_title` (optional): Job title for context
- `company_name` (optional): Company name for context
- `email_options` (optional): Email configuration options

#### Response

```json
{
  "success": true,
  "data": {
    "email_id": "email_345g6789-g01d-34f5-c678-648836396222",
    "evaluation_id": "eval_789xyz123-abc4-5678-90de-f12345678901",
    "recipient": "john.doe@example.com",
    "template_used": "high_relevance",
    "sent_at": "2024-01-15T10:30:00Z",
    "delivery_status": "sent",
    "subject": "Application Update: Senior Python Developer Position"
  },
  "message": "Evaluation email sent successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Email Configuration

#### Get Email Configuration

**Endpoint**: `GET /api/email/config`

#### Request

```bash
curl "http://localhost:5000/api/email/config"
```

#### Response

```json
{
  "success": true,
  "data": {
    "email_enabled": true,
    "provider": "smtp",
    "sender_email": "noreply@techcorp.com",
    "sender_name": "HR System",
    "templates": {
      "high_relevance": "high_relevance.html",
      "medium_relevance": "medium_relevance.html",
      "low_relevance": "low_relevance.html"
    },
    "smtp_configured": true,
    "daily_limit": 1000,
    "daily_sent": 45
  },
  "message": "Email configuration retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Update Email Configuration

**Endpoint**: `POST /api/email/config`

#### Request

```bash
curl -X POST "http://localhost:5000/api/email/config" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_email": "hr@techcorp.com",
    "sender_name": "TechCorp HR Team",
    "smtp_server": "smtp.techcorp.com",
    "smtp_port": 587,
    "smtp_username": "hr@techcorp.com",
    "smtp_password": "secure-password",
    "smtp_use_tls": true,
    "daily_limit": 2000
  }'
```

### Send Test Email

**Endpoint**: `POST /api/email/test`

#### Request

```bash
curl -X POST "http://localhost:5000/api/email/test" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "admin@techcorp.com",
    "template": "high_relevance",
    "test_data": {
      "candidate_name": "Test User",
      "job_title": "Test Position",
      "relevance_score": 85.5,
      "matched_skills": ["Python", "Flask"],
      "missing_skills": ["AWS"]
    }
  }'
```

### Email History

**Endpoint**: `GET /api/email/history`

#### Request

```bash
curl "http://localhost:5000/api/email/history?limit=20&status=sent&date_from=2024-01-01"
```

#### Query Parameters

- `limit` (optional): Number of records (default: 50)
- `offset` (optional): Offset for pagination (default: 0)
- `status` (optional): Filter by status (`sent`, `failed`, `pending`)
- `date_from` (optional): Start date filter (YYYY-MM-DD)
- `date_to` (optional): End date filter (YYYY-MM-DD)
- `recipient` (optional): Filter by recipient email

#### Response

```json
{
  "success": true,
  "data": {
    "emails": [
      {
        "email_id": "email_345g6789-g01d-34f5-c678-648836396222",
        "recipient": "john.doe@example.com",
        "subject": "Application Update: Senior Python Developer Position",
        "template": "high_relevance",
        "sent_at": "2024-01-15T10:30:00Z",
        "delivery_status": "sent",
        "open_count": 2,
        "click_count": 1
      }
    ],
    "total_count": 45,
    "limit": 20,
    "offset": 0
  },
  "message": "Email history retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Email Statistics

**Endpoint**: `GET /api/email/stats`

#### Request

```bash
curl "http://localhost:5000/api/email/stats?period=30days"
```

#### Response

```json
{
  "success": true,
  "data": {
    "period": "30days",
    "total_sent": 1245,
    "total_delivered": 1198,
    "total_failed": 47,
    "delivery_rate": 96.2,
    "open_rate": 68.5,
    "click_rate": 12.3,
    "template_performance": {
      "high_relevance": {
        "sent": 412,
        "open_rate": 78.2,
        "click_rate": 18.5
      },
      "medium_relevance": {
        "sent": 654,
        "open_rate": 65.8,
        "click_rate": 9.8
      },
      "low_relevance": {
        "sent": 179,
        "open_rate": 45.3,
        "click_rate": 3.2
      }
    },
    "daily_stats": [
      { "date": "2024-01-08", "sent": 35, "delivered": 34, "opened": 24 },
      { "date": "2024-01-09", "sent": 42, "delivered": 41, "opened": 29 }
    ]
  },
  "message": "Email statistics retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 System Endpoints

### Health Check

**Endpoint**: `GET /health`

#### Request

```bash
curl "http://localhost:5000/health"
```

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime": "2 days, 14:32:18",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12
    },
    "email": {
      "status": "healthy",
      "provider": "smtp"
    },
    "storage": {
      "status": "healthy",
      "free_space_gb": 45.7
    }
  }
}
```

### System Information

**Endpoint**: `GET /api/info`

#### Request

```bash
curl "http://localhost:5000/api/info"
```

#### Response

```json
{
  "success": true,
  "data": {
    "application": {
      "name": "Resume Relevance System",
      "version": "1.0.0",
      "build_date": "2024-01-01T00:00:00Z",
      "environment": "production"
    },
    "system": {
      "python_version": "3.11.5",
      "flask_version": "3.1.0",
      "os": "Linux",
      "cpu_count": 4,
      "memory_total_gb": 8
    },
    "features": {
      "transformers_enabled": true,
      "email_enabled": true,
      "database_type": "postgresql",
      "cache_enabled": true
    },
    "limits": {
      "max_file_size_mb": 16,
      "max_daily_emails": 1000,
      "max_concurrent_evaluations": 10
    }
  },
  "message": "System information retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Database Health Check

**Endpoint**: `GET /api/database/health`

#### Request

```bash
curl "http://localhost:5000/api/database/health"
```

#### Response

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database_type": "postgresql",
    "connection_pool": {
      "active_connections": 5,
      "max_connections": 20,
      "idle_connections": 3
    },
    "performance": {
      "avg_query_time_ms": 15.4,
      "slow_queries_count": 2,
      "cache_hit_rate": 94.2
    },
    "storage": {
      "total_size_mb": 156.7,
      "free_space_gb": 45.3,
      "backup_status": "completed_2024-01-15T06:00:00Z"
    },
    "tables": {
      "candidates": 1250,
      "jobs": 85,
      "evaluations": 3420,
      "emails": 1245
    }
  },
  "message": "Database health check completed",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔐 Authentication (Future)

The current API doesn't require authentication. For production deployment, consider implementing:

### API Key Authentication

```bash
curl -H "Authorization: Bearer your-api-key" \
  "http://localhost:5000/api/endpoint"
```

### OAuth 2.0 Authentication

```bash
curl -H "Authorization: Bearer oauth-access-token" \
  "http://localhost:5000/api/endpoint"
```

### JWT Token Authentication

```bash
curl -H "Authorization: JWT your-jwt-token" \
  "http://localhost:5000/api/endpoint"
```

## 🚀 Rate Limiting

To prevent abuse, consider implementing rate limiting:

- **File uploads**: 10 requests per minute per IP
- **Evaluations**: 50 requests per hour per IP
- **Email sending**: 100 emails per day per IP
- **Search queries**: 200 requests per hour per IP

## 🐛 Error Handling

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Examples

#### Validation Error (400)

```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "resume_id": ["This field is required"],
    "job_id": ["Invalid format"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### File Not Found (404)

```json
{
  "success": false,
  "error": "Resume not found",
  "error_code": "NOT_FOUND",
  "resource": "resume",
  "resource_id": "invalid-resume-id",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Rate Limit Exceeded (429)

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "limit": 50,
  "reset_time": "2024-01-15T11:00:00Z",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📊 OpenAPI/Swagger Specification

For a complete OpenAPI 3.0 specification, visit `/api/swagger.json` (when implemented) or use tools like Postman to import this documentation.

### Example Swagger Configuration

```yaml
openapi: 3.0.0
info:
  title: Resume Relevance System API
  version: 1.0.0
  description: Intelligent resume evaluation and candidate management system
servers:
  - url: http://localhost:5000
    description: Development server
  - url: https://api.your-domain.com
    description: Production server
paths:
  /api/upload/resume:
    post:
      summary: Upload resume file or text
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
          application/json:
            schema:
              type: object
              properties:
                text:
                  type: string
      responses:
        "200":
          description: Resume uploaded successfully
```

## 🔧 SDK and Client Libraries

Consider implementing client libraries for popular programming languages:

### Python SDK

```python
from resume_relevance import ResumeClient

client = ResumeClient(base_url="http://localhost:5000", api_key="your-key")

# Upload resume
resume = client.upload_resume(file_path="resume.pdf")

# Upload job description
job = client.upload_job_description(text="Job description...")

# Evaluate
evaluation = client.evaluate(resume.file_id, job.file_id)
print(f"Relevance Score: {evaluation.relevance_score}")
```

### JavaScript SDK

```javascript
import { ResumeClient } from "resume-relevance-sdk";

const client = new ResumeClient({
  baseUrl: "http://localhost:5000",
  apiKey: "your-key",
});

// Upload and evaluate
const resume = await client.uploadResume({ file: resumeFile });
const job = await client.uploadJobDescription({ text: jobText });
const evaluation = await client.evaluate(resume.fileId, job.fileId);

console.log(`Score: ${evaluation.relevanceScore}`);
```

---

_For more information and examples, visit the [main documentation](README.md) or contact our support team._

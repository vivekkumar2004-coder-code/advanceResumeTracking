"""
Test Configuration and Fixtures

This module provides pytest configuration, fixtures, and utilities
for testing the Resume Relevance System.
"""

import pytest
import tempfile
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Generator, Optional
from unittest.mock import MagicMock, patch

from app import create_app
from app.models.database_schema import db, Candidate, JobDescription, Evaluation, EmailRecord
from app.utils.database_manager import db_manager
from app.utils.email_config import EmailConfig, EmailProvider, email_config
from app.utils.email_sender import EmailMessage, EmailStatus

# Test data constants
SAMPLE_RESUME_TEXT = """
John Doe
Software Engineer

EXPERIENCE:
- 3 years Python development
- Flask web applications
- Machine Learning with scikit-learn
- Database design with PostgreSQL
- RESTful API development
- Git version control

EDUCATION:
- BS Computer Science, University of Tech

SKILLS:
- Python, Flask, PostgreSQL, scikit-learn
- HTML, CSS, JavaScript
- Docker, AWS
"""

SAMPLE_JOB_DESCRIPTION = """
We are seeking a Senior Python Developer to join our team.

REQUIREMENTS:
- 3+ years Python experience
- Flask or Django framework
- Database experience (PostgreSQL preferred)
- Machine Learning knowledge
- RESTful API development
- Cloud experience (AWS/GCP)

NICE TO HAVE:
- Docker containerization
- CI/CD pipeline experience
- React/Vue.js frontend
"""

SAMPLE_EVALUATION_RESULT = {
    'relevance_score': 85.5,
    'relevance_level': 'high',
    'total_matching_skills': 7,
    'total_job_skills': 10,
    'matched_skills': ['Python', 'Flask', 'PostgreSQL', 'Machine Learning', 'RESTful API', 'Docker', 'AWS'],
    'missing_skills': ['Django', 'CI/CD', 'React'],
    'strengths': ['Strong Python background', 'Relevant web framework experience'],
    'recommendations': ['Consider learning Django', 'Gain CI/CD experience'],
    'detailed_analysis': {
        'technical_skills': {'score': 90, 'details': 'Excellent technical match'},
        'experience': {'score': 85, 'details': 'Good experience level'},
        'education': {'score': 80, 'details': 'Relevant education'}
    }
}


@pytest.fixture(scope="session")
def app_config():
    """Application configuration for testing"""
    return {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        'EMAIL_ENABLED': True,
        'EMAIL_PROVIDER': 'mock'
    }


@pytest.fixture(scope="function")
def app(app_config):
    """Create Flask application for testing"""
    try:
        app = create_app()
        
        # Override config for testing
        app.config.update(app_config)
        
        # Initialize test database
        with app.app_context():
            db.create_all()
            
        yield app
        
        # Cleanup
        with app.app_context():
            db.drop_all()
            
    except Exception as e:
        # Fallback to simple app creation if full app fails
        from flask import Flask
        app = Flask(__name__)
        app.config.update(app_config)
        yield app


@pytest.fixture(scope="function")
def client(app):
    """Flask test client"""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def app_context(app):
    """Flask application context"""
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def mock_db():
    """Mock database manager for testing"""
    with patch('app.utils.database_manager.db_manager') as mock:
        mock.test_connection.return_value = {'connected': True, 'timestamp': datetime.utcnow().isoformat()}
        mock.get_database_info.return_value = {
            'type': 'sqlite',
            'location': ':memory:',
            'tables': ['candidates', 'job_descriptions', 'evaluations']
        }
        yield mock


@pytest.fixture(scope="function")
def sample_files():
    """Sample files for upload testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample resume file
    resume_file = os.path.join(temp_dir, 'sample_resume.txt')
    with open(resume_file, 'w') as f:
        f.write(SAMPLE_RESUME_TEXT)
    
    # Create sample job description file
    job_file = os.path.join(temp_dir, 'sample_job.txt')
    with open(job_file, 'w') as f:
        f.write(SAMPLE_JOB_DESCRIPTION)
    
    return {
        'resume_file': resume_file,
        'job_file': job_file,
        'temp_dir': temp_dir
    }


@pytest.fixture(scope="function")
def sample_candidate_data():
    """Sample candidate data for database testing"""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'resume_text': SAMPLE_RESUME_TEXT,
        'skills': ['Python', 'Flask', 'PostgreSQL', 'Machine Learning'],
        'experience_years': 3,
        'education': 'BS Computer Science',
        'location': 'New York, NY'
    }


@pytest.fixture(scope="function")
def sample_job_data():
    """Sample job description data for database testing"""
    return {
        'title': 'Senior Python Developer',
        'company': 'Tech Corp',
        'department': 'Engineering',
        'description': SAMPLE_JOB_DESCRIPTION,
        'required_skills': ['Python', 'Flask', 'PostgreSQL', 'Machine Learning', 'RESTful API'],
        'preferred_skills': ['Docker', 'AWS', 'Django', 'CI/CD'],
        'experience_level': 'senior',
        'location': 'New York, NY',
        'salary_min': 90000,
        'salary_max': 130000
    }


@pytest.fixture(scope="function")
def sample_evaluation_data():
    """Sample evaluation data for testing"""
    return SAMPLE_EVALUATION_RESULT


@pytest.fixture(scope="function")
def mock_email_service():
    """Mock email service for testing"""
    with patch('app.utils.email_sender.email_sender') as mock:
        mock.send_message.return_value = {
            'success': True,
            'message_id': f'test-{uuid.uuid4()}',
            'status': EmailStatus.SENT
        }
        mock.get_message_status.return_value = {
            'status': EmailStatus.SENT,
            'delivered_at': datetime.utcnow()
        }
        yield mock


@pytest.fixture(scope="function")
def email_config_test():
    """Test email configuration"""
    test_config = EmailConfig(
        enabled=True,
        provider=EmailProvider.SMTP,
        sender_email='test@example.com',
        sender_name='Test System',
        smtp_server='localhost',
        smtp_port=587,
        smtp_username='test',
        smtp_password='password',
        smtp_use_tls=True
    )
    
    # Temporarily set test config
    original_config = email_config._config
    email_config.update_config(test_config)
    
    yield test_config
    
    # Restore original config
    email_config._config = original_config


@pytest.fixture
def auth_headers():
    """Authentication headers for API testing"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_candidate(**kwargs) -> Dict[str, Any]:
        """Create candidate test data"""
        default_data = {
            'id': str(uuid.uuid4()),
            'name': 'Test Candidate',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'resume_text': SAMPLE_RESUME_TEXT,
            'skills': ['Python', 'Flask'],
            'experience_years': 3,
            'created_at': datetime.utcnow()
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_job(**kwargs) -> Dict[str, Any]:
        """Create job description test data"""
        default_data = {
            'id': str(uuid.uuid4()),
            'title': 'Test Job',
            'company': 'Test Company',
            'description': SAMPLE_JOB_DESCRIPTION,
            'required_skills': ['Python', 'Flask'],
            'created_at': datetime.utcnow()
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_evaluation(**kwargs) -> Dict[str, Any]:
        """Create evaluation test data"""
        default_data = {
            'id': str(uuid.uuid4()),
            'candidate_id': str(uuid.uuid4()),
            'job_id': str(uuid.uuid4()),
            'relevance_score': 85.0,
            'relevance_level': 'high',
            'created_at': datetime.utcnow()
        }
        default_data.update(kwargs)
        return default_data


@pytest.fixture
def test_data_factory():
    """Test data factory fixture"""
    return TestDataFactory()


def assert_api_success(response, expected_keys: Optional[list] = None):
    """Assert API response is successful and contains expected keys"""
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert 'success' in data
    assert data['success'] is True
    
    if expected_keys:
        for key in expected_keys:
            assert key in data


def assert_api_error(response, expected_status: int = 400, expected_error_key: str = 'error'):
    """Assert API response is an error with expected status"""
    assert response.status_code == expected_status
    data = response.get_json()
    assert data is not None
    assert expected_error_key in data


# Mock classes for testing
class MockEmailSender:
    """Mock email sender for testing"""
    
    def __init__(self):
        self.sent_messages = []
        self.message_status = {}
    
    def send_message(self, message: EmailMessage) -> Dict[str, Any]:
        """Mock send message"""
        message_id = f'mock-{len(self.sent_messages)}'
        self.sent_messages.append({
            'id': message_id,
            'message': message,
            'sent_at': datetime.utcnow()
        })
        self.message_status[message_id] = EmailStatus.SENT
        
        return {
            'success': True,
            'message_id': message_id,
            'status': EmailStatus.SENT
        }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Mock get message status"""
        return {
            'message_id': message_id,
            'status': self.message_status.get(message_id, EmailStatus.UNKNOWN),
            'delivered_at': datetime.utcnow() if message_id in self.message_status else None
        }


class MockDatabaseManager:
    """Mock database manager for testing"""
    
    def __init__(self):
        self.candidates = {}
        self.jobs = {}
        self.evaluations = {}
        self.connected = True
    
    def test_connection(self):
        """Mock test connection"""
        return {
            'connected': self.connected,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def save_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock save candidate"""
        candidate_id = candidate_data.get('id', str(uuid.uuid4()))
        self.candidates[candidate_id] = candidate_data
        return {'success': True, 'candidate_id': candidate_id}
    
    def save_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock save evaluation"""
        eval_id = evaluation_data.get('id', str(uuid.uuid4()))
        self.evaluations[eval_id] = evaluation_data
        return {'success': True, 'evaluation_id': eval_id}
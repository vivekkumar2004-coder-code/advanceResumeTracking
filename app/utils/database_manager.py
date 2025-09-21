"""
Database Configuration and Connection Management

This module provides database configuration, connection management, and
initialization utilities for the Resume Relevance System.

Features:
- Environment-based configuration (PostgreSQL/SQLite)
- Database initialization and migration support
- Connection pooling and error handling
- Sample data generation for testing
- Database utilities and helpers

Author: Automated Resume Relevance System
Version: 1.0.0
"""

import os
import logging
from typing import Dict, Any, Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import uuid


class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration from environment variables"""
        db_type = os.getenv('DATABASE_TYPE', 'sqlite').lower()
        
        if db_type == 'postgresql':
            return self._get_postgresql_config()
        else:
            return self._get_sqlite_config()
    
    def _get_postgresql_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration"""
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 5432))
        database = os.getenv('DB_NAME', 'resume_relevance')
        username = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        # Connection parameters
        connection_params = {
            'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
            'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
            'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
            'echo': os.getenv('DB_ECHO', 'false').lower() == 'true'
        }
        
        # Build connection URL
        connection_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        return {
            'type': 'postgresql',
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password,
            'connection_url': connection_url,
            'connection_params': connection_params
        }
    
    def _get_sqlite_config(self) -> Dict[str, Any]:
        """Get SQLite configuration"""
        database_path = os.getenv('DB_PATH', 'data/resume_relevance.db')
        
        # Ensure directory exists
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Make path absolute
        if not os.path.isabs(database_path):
            database_path = os.path.abspath(database_path)
        
        connection_url = f"sqlite:///{database_path}"
        
        return {
            'type': 'sqlite',
            'database_path': database_path,
            'connection_url': connection_url,
            'connection_params': {
                'echo': os.getenv('DB_ECHO', 'false').lower() == 'true',
                'pool_pre_ping': True
            }
        }
    
    def _validate_config(self):
        """Validate database configuration"""
        if self.config['type'] == 'postgresql':
            required_fields = ['host', 'database', 'username']
            for field in required_fields:
                if not self.config.get(field):
                    raise ValueError(f"PostgreSQL configuration missing required field: {field}")
        
        elif self.config['type'] == 'sqlite':
            if not self.config.get('database_path'):
                raise ValueError("SQLite configuration missing database_path")
    
    def get_sqlalchemy_config(self) -> Dict[str, Any]:
        """Get SQLAlchemy configuration for Flask app"""
        config = {
            'SQLALCHEMY_DATABASE_URI': self.config['connection_url'],
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_RECORD_QUERIES': os.getenv('DB_RECORD_QUERIES', 'false').lower() == 'true'
        }
        
        # Add engine options
        engine_options = self.config['connection_params'].copy()
        config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
        
        return config


class DatabaseManager:
    """Database connection and operations manager"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.config = DatabaseConfig()
        self.db: Optional[SQLAlchemy] = None
        self.migrate: Optional[Migrate] = None
        self.logger = logging.getLogger(__name__)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize database with Flask app"""
        self.app = app
        
        # Configure SQLAlchemy
        sqlalchemy_config = self.config.get_sqlalchemy_config()
        for key, value in sqlalchemy_config.items():
            app.config[key] = value
        
        # Import models after setting up config
        from ..models import db, migrate
        
        self.db = db
        self.migrate = migrate
        
        # Initialize with app
        db.init_app(app)
        migrate.init_app(app, db)
        
        # Set up event listeners
        self._setup_event_listeners()
        
        self.logger.info(f"Database initialized: {self.config.config['type']}")
    
    def _setup_event_listeners(self):
        """Setup database event listeners"""
        if self.config.config['type'] == 'sqlite':
            # Enable foreign key constraints for SQLite
            from sqlalchemy import event
            from sqlalchemy.engine import Engine
            
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                if 'sqlite' in str(dbapi_connection):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
    
    def create_tables(self):
        """Create all database tables"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                self.db.create_all()
                self.logger.info("Database tables created successfully")
                return True
        except Exception as e:
            self.logger.error(f"Failed to create tables: {str(e)}")
            return False
    
    def drop_tables(self):
        """Drop all database tables"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                self.db.drop_all()
                self.logger.info("Database tables dropped successfully")
                return True
        except Exception as e:
            self.logger.error(f"Failed to drop tables: {str(e)}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection"""
        if not self.db:
            return {'connected': False, 'error': 'Database not initialized'}
        
        try:
            with self.app.app_context():
                # Test basic query
                result = self.db.session.execute(text('SELECT 1 as test'))
                row = result.fetchone()
                
                if row and row.test == 1:
                    return {
                        'connected': True,
                        'database_type': self.config.config['type'],
                        'connection_url': self.config.config['connection_url'].split('@')[-1] if '@' in self.config.config['connection_url'] else self.config.config['connection_url'],
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    return {'connected': False, 'error': 'Query test failed'}
                    
        except Exception as e:
            self.logger.error(f"Database connection test failed: {str(e)}")
            return {'connected': False, 'error': str(e)}
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        if not self.db:
            return {'error': 'Database not initialized'}
        
        try:
            with self.app.app_context():
                # Import models
                from ..models import Candidate, JobDescription, Evaluation, FeedbackRecord, AuditLog
                
                info = {
                    'database_type': self.config.config['type'],
                    'connection_info': self.test_connection(),
                    'table_counts': {
                        'candidates': Candidate.query.count(),
                        'job_descriptions': JobDescription.query.count(),
                        'evaluations': Evaluation.query.count(),
                        'feedback_records': FeedbackRecord.query.count(),
                        'audit_logs': AuditLog.query.count()
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Add database-specific information
                if self.config.config['type'] == 'sqlite':
                    info['database_path'] = self.config.config['database_path']
                    if os.path.exists(self.config.config['database_path']):
                        info['database_size'] = os.path.getsize(self.config.config['database_path'])
                elif self.config.config['type'] == 'postgresql':
                    info['host'] = self.config.config['host']
                    info['port'] = self.config.config['port']
                    info['database_name'] = self.config.config['database']
                
                return info
                
        except Exception as e:
            self.logger.error(f"Failed to get database info: {str(e)}")
            return {'error': str(e)}
    
    def backup_database(self, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """Create database backup (SQLite only)"""
        if self.config.config['type'] != 'sqlite':
            return {'success': False, 'error': 'Backup only supported for SQLite'}
        
        try:
            source_path = self.config.config['database_path']
            if not os.path.exists(source_path):
                return {'success': False, 'error': 'Database file not found'}
            
            if not backup_path:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{source_path}.backup_{timestamp}"
            
            import shutil
            shutil.copy2(source_path, backup_path)
            
            return {
                'success': True,
                'backup_path': backup_path,
                'backup_size': os.path.getsize(backup_path),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def restore_database(self, backup_path: str) -> Dict[str, Any]:
        """Restore database from backup (SQLite only)"""
        if self.config.config['type'] != 'sqlite':
            return {'success': False, 'error': 'Restore only supported for SQLite'}
        
        try:
            if not os.path.exists(backup_path):
                return {'success': False, 'error': 'Backup file not found'}
            
            target_path = self.config.config['database_path']
            
            # Create backup of current database if it exists
            if os.path.exists(target_path):
                current_backup = f"{target_path}.pre_restore_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(target_path, current_backup)
            
            # Restore from backup
            import shutil
            shutil.copy2(backup_path, target_path)
            
            return {
                'success': True,
                'restored_from': backup_path,
                'restored_to': target_path,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Database restore failed: {str(e)}")
            return {'success': False, 'error': str(e)}


def create_sample_data_complete(app: Flask, db_manager: DatabaseManager) -> Dict[str, Any]:
    """Create comprehensive sample data for testing"""
    if not db_manager.db:
        return {'success': False, 'error': 'Database not initialized'}
    
    try:
        with app.app_context():
            from ..models import (
                CandidateManager, JobDescriptionManager, 
                EvaluationManager, FeedbackManager
            )
            
            created_data = {
                'candidates': [],
                'jobs': [],
                'evaluations': [],
                'feedback_records': []
            }
            
            # Create sample candidates
            sample_candidates = [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@email.com',
                    'phone': '+1234567890',
                    'location': 'San Francisco, CA',
                    'resume_filename': 'john_doe_resume.pdf',
                    'skills': ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS'],
                    'work_experience': [
                        {
                            'title': 'Senior Software Engineer',
                            'company': 'Tech Corp',
                            'duration': '2020-2023',
                            'description': 'Led development of web applications'
                        }
                    ],
                    'education': [
                        {
                            'degree': 'Computer Science',
                            'institution': 'Stanford University',
                            'year': 2018
                        }
                    ],
                    'total_experience_years': 5,
                    'current_position': 'Senior Software Engineer',
                    'current_company': 'Tech Corp'
                },
                {
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'email': 'jane.smith@email.com',
                    'phone': '+1234567891',
                    'location': 'New York, NY',
                    'resume_filename': 'jane_smith_resume.pdf',
                    'skills': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'TypeScript'],
                    'work_experience': [
                        {
                            'title': 'Frontend Developer',
                            'company': 'Web Solutions',
                            'duration': '2019-2023',
                            'description': 'Built modern web applications'
                        }
                    ],
                    'education': [
                        {
                            'degree': 'Software Engineering',
                            'institution': 'MIT',
                            'year': 2019
                        }
                    ],
                    'total_experience_years': 4,
                    'current_position': 'Frontend Developer',
                    'current_company': 'Web Solutions'
                }
            ]
            
            for candidate_data in sample_candidates:
                candidate = CandidateManager.create_candidate(candidate_data)
                created_data['candidates'].append(candidate.id)
            
            # Create sample job descriptions
            sample_jobs = [
                {
                    'title': 'Senior Python Developer',
                    'company_name': 'InnovateTech',
                    'department': 'Engineering',
                    'location': 'San Francisco, CA',
                    'description': 'We are looking for an experienced Python developer...',
                    'required_skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
                    'preferred_skills': ['AWS', 'Kubernetes', 'Redis'],
                    'minimum_experience': 3,
                    'maximum_experience': 8,
                    'salary_min': 120000,
                    'salary_max': 180000,
                    'employment_type': 'full_time',
                    'remote_option': 'hybrid'
                },
                {
                    'title': 'Frontend React Developer',
                    'company_name': 'WebCorp',
                    'department': 'Product',
                    'location': 'New York, NY',
                    'description': 'Join our frontend team to build amazing user experiences...',
                    'required_skills': ['JavaScript', 'React', 'TypeScript', 'CSS'],
                    'preferred_skills': ['Node.js', 'GraphQL', 'Jest'],
                    'minimum_experience': 2,
                    'maximum_experience': 6,
                    'salary_min': 100000,
                    'salary_max': 150000,
                    'employment_type': 'full_time',
                    'remote_option': 'remote'
                }
            ]
            
            for job_data in sample_jobs:
                job = JobDescriptionManager.create_job_description(job_data)
                created_data['jobs'].append(job.id)
            
            # Create sample evaluations
            if created_data['candidates'] and created_data['jobs']:
                for candidate_id in created_data['candidates']:
                    for job_id in created_data['jobs']:
                        evaluation_data = {
                            'candidate_id': candidate_id,
                            'job_description_id': job_id,
                            'overall_score': 85.5,
                            'suitability_verdict': 'HIGH',
                            'confidence_level': 'high',
                            'confidence_score': 0.85,
                            'component_scores': {
                                'skills_match': 0.9,
                                'experience_match': 0.8,
                                'education_match': 0.85
                            },
                            'strengths': [
                                'Strong technical skills',
                                'Relevant experience',
                                'Good educational background'
                            ],
                            'weaknesses': [
                                'Could benefit from more cloud experience'
                            ],
                            'processing_time': 2.5,
                            'semantic_similarity_score': 0.82,
                            'experience_match_score': 0.78,
                            'skill_coverage_score': 0.88
                        }
                        
                        evaluation = EvaluationManager.create_evaluation(evaluation_data)
                        created_data['evaluations'].append(evaluation.id)
                        
                        # Create feedback for this evaluation
                        feedback_data = {
                            'candidate_id': candidate_id,
                            'evaluation_id': evaluation.id,
                            'job_description_id': job_id,
                            'feedback_type': 'comprehensive',
                            'feedback_tone': 'professional',
                            'llm_provider': 'mock',
                            'executive_summary': 'Strong candidate with relevant experience...',
                            'strengths': [
                                'Excellent technical skills in required technologies',
                                'Solid work experience in similar roles'
                            ],
                            'areas_for_improvement': [
                                'Consider gaining more cloud platform experience',
                                'Expand knowledge of DevOps practices'
                            ],
                            'skill_recommendations': [
                                'AWS Certified Solutions Architect',
                                'Kubernetes fundamentals'
                            ],
                            'processing_time': 1.2,
                            'generation_quality': 'excellent'
                        }
                        
                        feedback = FeedbackManager.create_feedback_record(feedback_data)
                        created_data['feedback_records'].append(feedback.id)
            
            return {
                'success': True,
                'message': 'Sample data created successfully',
                'created_data': created_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        app.logger.error(f"Failed to create sample data: {str(e)}")
        return {'success': False, 'error': str(e)}

    def save_email_record(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save email sending record to database"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                from ..models import EmailRecord
                
                # Create email record
                email_record = EmailRecord(
                    message_id=email_data.get('message_id'),
                    evaluation_id=email_data.get('evaluation_id'),
                    candidate_email=email_data.get('candidate_email'),
                    candidate_name=email_data.get('candidate_name'),
                    subject=email_data.get('subject', ''),
                    template_used=email_data.get('template_used', ''),
                    relevance_score=email_data.get('relevance_score', 0.0),
                    status=email_data.get('status', 'pending'),
                    sent_at=email_data.get('sent_at'),
                    error_message=email_data.get('error_message'),
                    retry_count=email_data.get('retry_count', 0)
                )
                
                self.db.session.add(email_record)
                self.db.session.commit()
                
                return {
                    'success': True,
                    'email_record_id': email_record.id,
                    'message_id': email_record.message_id
                }
                
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"Failed to save email record: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_email_history(self, page: int = 1, per_page: int = 20, 
                         status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get email sending history with pagination"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                from ..models import EmailRecord
                
                query = EmailRecord.query
                
                # Apply status filter if provided
                if status_filter:
                    query = query.filter(EmailRecord.status == status_filter)
                
                # Order by sent_at descending
                query = query.order_by(EmailRecord.created_at.desc())
                
                # Paginate results
                paginated = query.paginate(
                    page=page, per_page=per_page, error_out=False
                )
                
                # Convert to dict
                emails = []
                for email in paginated.items:
                    emails.append({
                        'id': email.id,
                        'message_id': email.message_id,
                        'evaluation_id': email.evaluation_id,
                        'candidate_email': email.candidate_email,
                        'candidate_name': email.candidate_name,
                        'subject': email.subject,
                        'template_used': email.template_used,
                        'relevance_score': email.relevance_score,
                        'status': email.status,
                        'sent_at': email.sent_at.isoformat() if email.sent_at else None,
                        'created_at': email.created_at.isoformat(),
                        'error_message': email.error_message,
                        'retry_count': email.retry_count
                    })
                
                return {
                    'success': True,
                    'emails': emails,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': paginated.total,
                        'pages': paginated.pages,
                        'has_prev': paginated.has_prev,
                        'has_next': paginated.has_next
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get email history: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_email_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get email sending statistics for date range"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                from ..models import EmailRecord
                from sqlalchemy import func
                
                # Base query for date range
                base_query = EmailRecord.query.filter(
                    EmailRecord.created_at >= start_date,
                    EmailRecord.created_at <= end_date
                )
                
                # Total emails
                total_emails = base_query.count()
                
                # Status breakdown
                status_stats = self.db.session.query(
                    EmailRecord.status,
                    func.count(EmailRecord.id).label('count')
                ).filter(
                    EmailRecord.created_at >= start_date,
                    EmailRecord.created_at <= end_date
                ).group_by(EmailRecord.status).all()
                
                status_breakdown = {status: count for status, count in status_stats}
                
                # Template usage
                template_stats = self.db.session.query(
                    EmailRecord.template_used,
                    func.count(EmailRecord.id).label('count')
                ).filter(
                    EmailRecord.created_at >= start_date,
                    EmailRecord.created_at <= end_date,
                    EmailRecord.template_used.isnot(None)
                ).group_by(EmailRecord.template_used).all()
                
                template_breakdown = {template: count for template, count in template_stats}
                
                # Average relevance score
                avg_relevance = self.db.session.query(
                    func.avg(EmailRecord.relevance_score)
                ).filter(
                    EmailRecord.created_at >= start_date,
                    EmailRecord.created_at <= end_date,
                    EmailRecord.relevance_score > 0
                ).scalar()
                
                # Daily email counts
                daily_stats = self.db.session.query(
                    func.date(EmailRecord.created_at).label('date'),
                    func.count(EmailRecord.id).label('count')
                ).filter(
                    EmailRecord.created_at >= start_date,
                    EmailRecord.created_at <= end_date
                ).group_by(func.date(EmailRecord.created_at)).all()
                
                daily_breakdown = {str(date): count for date, count in daily_stats}
                
                return {
                    'success': True,
                    'stats': {
                        'total_emails': total_emails,
                        'date_range': {
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat()
                        },
                        'status_breakdown': status_breakdown,
                        'template_breakdown': template_breakdown,
                        'average_relevance_score': round(avg_relevance or 0, 2),
                        'daily_breakdown': daily_breakdown
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get email stats: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_evaluation_by_id(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Get evaluation result by ID"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                from ..models import Evaluation
                
                evaluation = Evaluation.query.filter_by(id=evaluation_id).first()
                if not evaluation:
                    return None
                
                return {
                    'id': evaluation.id,
                    'candidate_id': evaluation.candidate_id,
                    'job_description_id': evaluation.job_description_id,
                    'relevance_score': evaluation.relevance_score,
                    'matched_skills': evaluation.matched_skills or [],
                    'missing_skills': evaluation.missing_skills or [],
                    'skill_match_percentage': evaluation.skill_match_percentage,
                    'experience_match': evaluation.experience_match,
                    'education_match': evaluation.education_match,
                    'location_match': evaluation.location_match,
                    'salary_match': evaluation.salary_match,
                    'overall_feedback': evaluation.overall_feedback,
                    'strengths': evaluation.strengths or [],
                    'weaknesses': evaluation.weaknesses or [],
                    'recommendations': evaluation.recommendations or [],
                    'job_title': getattr(evaluation.job_description, 'title', ''),
                    'job_description': getattr(evaluation.job_description, 'description', ''),
                    'job_requirements': getattr(evaluation.job_description, 'requirements', []),
                    'created_at': evaluation.created_at.isoformat(),
                    'updated_at': evaluation.updated_at.isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get evaluation: {str(e)}")
            return None

    def create_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Create a new job description entry"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                from ..models import JobDescription
                
                job = JobDescription(
                    title=job_data.get('title', ''),
                    company=job_data.get('company_name', ''),
                    description=job_data.get('description', ''),
                    requirements=job_data.get('requirements', []),
                    preferred_qualifications=job_data.get('preferred_qualifications', []),
                    skills_required=job_data.get('required_skills', []),
                    skills_preferred=job_data.get('preferred_skills', []),
                    experience_level=job_data.get('experience_required', ''),
                    location=job_data.get('location', ''),
                    employment_type=job_data.get('employment_type', 'full-time'),
                    remote_allowed=job_data.get('remote_allowed', False),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    department=job_data.get('department', ''),
                    job_level=job_data.get('job_level', ''),
                    application_deadline=job_data.get('application_deadline')
                )
                
                self.db.session.add(job)
                self.db.session.commit()
                
                return job.id
                
        except Exception as e:
            self.logger.error(f"Failed to create job: {str(e)}")
            return None

    def save_evaluation(self, evaluation_data: Dict[str, Any]) -> Optional[str]:
        """Save evaluation results to database"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            with self.app.app_context():
                from ..models import Evaluation
                
                evaluation = Evaluation(
                    candidate_id=evaluation_data.get('candidate_id'),
                    job_description_id=evaluation_data.get('job_id'),
                    relevance_score=evaluation_data.get('relevance_score', 0.0),
                    matched_skills=evaluation_data.get('matched_skills', []),
                    missing_skills=evaluation_data.get('missing_skills', []),
                    skill_match_percentage=evaluation_data.get('skill_match_percentage', 0.0),
                    experience_match=evaluation_data.get('experience_match', 0.0),
                    education_match=evaluation_data.get('education_match', 0.0),
                    overall_feedback=evaluation_data.get('overall_feedback', ''),
                    strengths=evaluation_data.get('strengths', []),
                    weaknesses=evaluation_data.get('weaknesses', []),
                    recommendations=evaluation_data.get('recommendations', [])
                )
                
                self.db.session.add(evaluation)
                self.db.session.commit()
                
                return evaluation.id
                
        except Exception as e:
            self.logger.error(f"Failed to save evaluation: {str(e)}")
            return None


# Create mock Manager classes for backward compatibility with tests
class JobDescriptionManager:
    """Mock manager for job descriptions (for test compatibility)"""
    @staticmethod
    def create_job(job_data):
        return db_manager.create_job(job_data)


class EvaluationManager:
    """Mock manager for evaluations (for test compatibility)"""
    @staticmethod
    def save_evaluation(evaluation_data):
        return db_manager.save_evaluation(evaluation_data)


# Global database manager instance
db_manager = DatabaseManager()


# Export utilities
__all__ = [
    'DatabaseConfig', 'DatabaseManager', 'db_manager',
    'create_sample_data_complete'
]
"""
Database Schema Design for Resume Relevance System

This module defines the comprehensive database schema for storing candidate data,
evaluations, scores, and metadata. The schema supports both PostgreSQL and SQLite
with proper relationships, indexing, and constraints.

Schema Components:
- Candidates: Personal information and resume data
- Job Descriptions: Job requirements and specifications
- Evaluations: Resume evaluation results and scores
- Component Scores: Detailed component-wise scoring
- Feedback Records: LLM-generated feedback and recommendations
- Audit Logs: System activity tracking and versioning
- Analytics Tables: Performance metrics and insights

Database Support: PostgreSQL (production), SQLite (development/testing)
ORM: SQLAlchemy with Flask-SQLAlchemy
Migration: Flask-Migrate (Alembic)

Author: Automated Resume Relevance System
Version: 1.0.0
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from sqlalchemy import Index, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, TEXT
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
import uuid
import json

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()


def generate_uuid():
    """Generate UUID string for primary keys"""
    return str(uuid.uuid4())


class BaseModel(db.Model):
    """Base model with common fields and methods"""
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, (dict, list)):
                value = json.dumps(value) if not isinstance(value, str) else value
            result[column.name] = value
        return result
    
    def update_from_dict(self, data):
        """Update model from dictionary"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class Candidate(BaseModel):
    """
    Candidate information and resume data
    
    Stores personal information, contact details, and parsed resume content
    """
    __tablename__ = 'candidates'
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    
    # Resume Information
    resume_filename = db.Column(db.String(255), nullable=False)
    resume_file_path = db.Column(db.String(500), nullable=False)
    resume_file_size = db.Column(db.Integer)
    resume_mime_type = db.Column(db.String(100))
    resume_upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Parsed Resume Data (JSON)
    parsed_resume_data = db.Column(db.Text)  # JSON string for compatibility
    
    # Skills and Experience
    skills = db.Column(db.Text)  # JSON array of skills
    work_experience = db.Column(db.Text)  # JSON array of work experience
    education = db.Column(db.Text)  # JSON array of education
    certifications = db.Column(db.Text)  # JSON array of certifications
    
    # Profile Summary
    professional_summary = db.Column(db.Text)
    total_experience_years = db.Column(db.Float)
    current_position = db.Column(db.String(200))
    current_company = db.Column(db.String(200))
    
    # Metadata
    source = db.Column(db.String(50), default='web_upload')  # web_upload, api, bulk_import
    tags = db.Column(db.Text)  # JSON array of tags
    notes = db.Column(db.Text)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='candidate', lazy='dynamic', cascade='all, delete-orphan')
    feedback_records = db.relationship('FeedbackRecord', backref='candidate', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_candidate_email', 'email'),
        Index('idx_candidate_name', 'first_name', 'last_name'),
        Index('idx_candidate_upload_date', 'resume_upload_date'),
        Index('idx_candidate_active', 'is_active'),
    )
    
    @hybrid_property
    def full_name(self):
        """Get candidate's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def skills_list(self):
        """Get skills as list"""
        return json.loads(self.skills) if self.skills else []
    
    @skills_list.setter
    def skills_list(self, value):
        """Set skills from list"""
        self.skills = json.dumps(value) if value else None
    
    @property
    def parsed_data(self):
        """Get parsed resume data as dict"""
        return json.loads(self.parsed_resume_data) if self.parsed_resume_data else {}
    
    @parsed_data.setter
    def parsed_data(self, value):
        """Set parsed resume data from dict"""
        self.parsed_resume_data = json.dumps(value) if value else None
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if '@' not in email:
            raise ValueError('Invalid email format')
        return email.lower()
    
    def __repr__(self):
        return f'<Candidate {self.full_name} ({self.email})>'


class JobDescription(BaseModel):
    """
    Job description and requirements
    
    Stores job postings, requirements, and evaluation criteria
    """
    __tablename__ = 'job_descriptions'
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(200))
    employment_type = db.Column(db.String(50))  # full_time, part_time, contract, internship
    remote_option = db.Column(db.String(50))  # remote, hybrid, on_site
    
    # Job Details
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text)  # JSON array
    requirements = db.Column(db.Text)  # JSON array
    
    # Skills and Experience
    required_skills = db.Column(db.Text, nullable=False)  # JSON array
    preferred_skills = db.Column(db.Text)  # JSON array
    minimum_experience = db.Column(db.Integer)  # years
    maximum_experience = db.Column(db.Integer)  # years
    education_requirements = db.Column(db.Text)  # JSON array
    certifications_required = db.Column(db.Text)  # JSON array
    certifications_preferred = db.Column(db.Text)  # JSON array
    
    # Compensation
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='USD')
    benefits = db.Column(db.Text)  # JSON array
    
    # Job Posting Information
    posting_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    application_deadline = db.Column(db.DateTime(timezone=True))
    job_posting_url = db.Column(db.String(500))
    internal_job_id = db.Column(db.String(100))
    
    # Evaluation Configuration
    evaluation_criteria = db.Column(db.Text)  # JSON object with weights and criteria
    scoring_weights = db.Column(db.Text)  # JSON object with component weights
    
    # Status and Metadata
    status = db.Column(db.String(20), default='active')  # active, paused, closed, draft
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    tags = db.Column(db.Text)  # JSON array
    notes = db.Column(db.Text)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='job_description', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_job_title', 'title'),
        Index('idx_job_company', 'company_name'),
        Index('idx_job_status', 'status'),
        Index('idx_job_posting_date', 'posting_date'),
        Index('idx_job_priority', 'priority'),
        CheckConstraint('minimum_experience >= 0', name='check_min_experience'),
        CheckConstraint('maximum_experience >= minimum_experience', name='check_max_experience'),
    )
    
    @property
    def required_skills_list(self):
        """Get required skills as list"""
        return json.loads(self.required_skills) if self.required_skills else []
    
    @required_skills_list.setter
    def required_skills_list(self, value):
        """Set required skills from list"""
        self.required_skills = json.dumps(value) if value else None
    
    @property
    def evaluation_config(self):
        """Get evaluation configuration"""
        return json.loads(self.evaluation_criteria) if self.evaluation_criteria else {}
    
    def __repr__(self):
        return f'<JobDescription {self.title} at {self.company_name}>'


class Evaluation(BaseModel):
    """
    Resume evaluation results and scores
    
    Stores comprehensive evaluation results for candidate-job combinations
    """
    __tablename__ = 'evaluations'
    
    # Foreign Keys
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidates.id'), nullable=False)
    job_description_id = db.Column(db.String(36), db.ForeignKey('job_descriptions.id'), nullable=False)
    
    # Evaluation Metadata
    evaluation_type = db.Column(db.String(50), default='comprehensive')  # comprehensive, skill_focused, etc.
    evaluation_version = db.Column(db.String(20), default='2.0.0')
    evaluation_method = db.Column(db.String(50), default='advanced_scorer')
    
    # Overall Scores
    overall_score = db.Column(db.Float, nullable=False)  # 0-100
    suitability_verdict = db.Column(db.String(20), nullable=False)  # HIGH, MEDIUM, LOW, INSUFFICIENT_DATA
    confidence_level = db.Column(db.String(20), nullable=False)  # VERY_HIGH, HIGH, MODERATE, LOW, VERY_LOW
    confidence_score = db.Column(db.Float)  # 0-1
    
    # Processing Information
    processing_time = db.Column(db.Float)  # seconds
    analysis_method = db.Column(db.String(50))
    model_version = db.Column(db.String(50))
    
    # Detailed Results (JSON)
    component_scores = db.Column(db.Text)  # JSON object with component scores
    strengths = db.Column(db.Text)  # JSON array
    weaknesses = db.Column(db.Text)  # JSON array
    recommendations = db.Column(db.Text)  # JSON array
    
    # Analysis Details
    keyword_matches = db.Column(db.Text)  # JSON object
    semantic_similarity_score = db.Column(db.Float)
    experience_match_score = db.Column(db.Float)
    skill_coverage_score = db.Column(db.Float)
    
    # Evaluation Context
    evaluation_notes = db.Column(db.Text)
    evaluator_id = db.Column(db.String(100))  # system, user_id, or api_key
    evaluation_source = db.Column(db.String(50), default='system')  # system, manual, api
    
    # Status
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, archived
    
    # Relationships
    component_scores_rel = db.relationship('ComponentScore', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')
    feedback_records = db.relationship('FeedbackRecord', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_evaluation_candidate', 'candidate_id'),
        Index('idx_evaluation_job', 'job_description_id'),
        Index('idx_evaluation_score', 'overall_score'),
        Index('idx_evaluation_verdict', 'suitability_verdict'),
        Index('idx_evaluation_date', 'created_at'),
        Index('idx_evaluation_status', 'status'),
        UniqueConstraint('candidate_id', 'job_description_id', 'evaluation_type', 'created_at', 
                        name='unique_candidate_job_evaluation'),
        CheckConstraint('overall_score >= 0 AND overall_score <= 100', name='check_score_range'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_range'),
    )
    
    @property
    def component_scores_dict(self):
        """Get component scores as dictionary"""
        return json.loads(self.component_scores) if self.component_scores else {}
    
    @component_scores_dict.setter
    def component_scores_dict(self, value):
        """Set component scores from dictionary"""
        self.component_scores = json.dumps(value) if value else None
    
    @property
    def strengths_list(self):
        """Get strengths as list"""
        return json.loads(self.strengths) if self.strengths else []
    
    @property
    def is_good_match(self):
        """Check if evaluation indicates a good match"""
        return self.overall_score >= 70 and self.suitability_verdict in ['HIGH', 'MEDIUM']
    
    def __repr__(self):
        return f'<Evaluation {self.id}: Score {self.overall_score} ({self.suitability_verdict})>'


class ComponentScore(BaseModel):
    """
    Detailed component-wise scoring
    
    Stores individual component scores for detailed analysis
    """
    __tablename__ = 'component_scores'
    
    # Foreign Key
    evaluation_id = db.Column(db.String(36), db.ForeignKey('evaluations.id'), nullable=False)
    
    # Component Information
    component_name = db.Column(db.String(100), nullable=False)
    component_type = db.Column(db.String(50), nullable=False)  # semantic, keyword, experience, skill, certification
    component_weight = db.Column(db.Float, nullable=False)  # 0-1
    
    # Scores
    raw_score = db.Column(db.Float, nullable=False)  # 0-100
    weighted_score = db.Column(db.Float, nullable=False)  # raw_score * weight
    normalized_score = db.Column(db.Float, nullable=False)  # 0-100
    
    # Analysis Details
    evidence = db.Column(db.Text)  # JSON array of evidence
    methodology = db.Column(db.String(100))
    confidence = db.Column(db.Float)  # 0-1
    
    # Processing Info
    processing_time = db.Column(db.Float)
    
    # Indexes
    __table_args__ = (
        Index('idx_component_evaluation', 'evaluation_id'),
        Index('idx_component_name', 'component_name'),
        Index('idx_component_type', 'component_type'),
        Index('idx_component_score', 'normalized_score'),
        CheckConstraint('raw_score >= 0 AND raw_score <= 100', name='check_raw_score_range'),
        CheckConstraint('component_weight >= 0 AND component_weight <= 1', name='check_weight_range'),
    )
    
    @property
    def evidence_list(self):
        """Get evidence as list"""
        return json.loads(self.evidence) if self.evidence else []
    
    def __repr__(self):
        return f'<ComponentScore {self.component_name}: {self.normalized_score}>'


class FeedbackRecord(BaseModel):
    """
    LLM-generated feedback and recommendations
    
    Stores personalized feedback generated by LLMs
    """
    __tablename__ = 'feedback_records'
    
    # Foreign Keys
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidates.id'), nullable=False)
    evaluation_id = db.Column(db.String(36), db.ForeignKey('evaluations.id'), nullable=True)
    job_description_id = db.Column(db.String(36), db.ForeignKey('job_descriptions.id'), nullable=True)
    
    # Feedback Configuration
    feedback_type = db.Column(db.String(50), nullable=False)  # comprehensive, skill_focused, etc.
    feedback_tone = db.Column(db.String(50), nullable=False)  # professional, encouraging, etc.
    llm_provider = db.Column(db.String(50), nullable=False)  # openai, anthropic, local, mock
    model_name = db.Column(db.String(100))
    
    # Generated Content
    executive_summary = db.Column(db.Text)
    strengths = db.Column(db.Text)  # JSON array
    areas_for_improvement = db.Column(db.Text)  # JSON array of improvement areas
    skill_recommendations = db.Column(db.Text)  # JSON array
    experience_suggestions = db.Column(db.Text)  # JSON array
    certification_recommendations = db.Column(db.Text)  # JSON array
    resume_enhancement_tips = db.Column(db.Text)  # JSON array
    career_progression_advice = db.Column(db.Text)  # JSON array
    learning_resources = db.Column(db.Text)  # JSON array of resources
    next_steps = db.Column(db.Text)  # JSON array
    
    # Metadata
    processing_time = db.Column(db.Float)
    token_usage = db.Column(db.Integer)
    cost_estimate = db.Column(db.Numeric(10, 6))
    generation_quality = db.Column(db.String(20))  # excellent, good, fair, poor
    
    # Status
    status = db.Column(db.String(20), default='generated')  # generated, reviewed, approved, archived
    reviewer_notes = db.Column(db.Text)
    
    # Indexes
    __table_args__ = (
        Index('idx_feedback_candidate', 'candidate_id'),
        Index('idx_feedback_evaluation', 'evaluation_id'),
        Index('idx_feedback_type', 'feedback_type'),
        Index('idx_feedback_provider', 'llm_provider'),
        Index('idx_feedback_date', 'created_at'),
        Index('idx_feedback_status', 'status'),
    )
    
    @property
    def feedback_content(self):
        """Get complete feedback as structured dict"""
        return {
            'executive_summary': self.executive_summary,
            'strengths': json.loads(self.strengths) if self.strengths else [],
            'areas_for_improvement': json.loads(self.areas_for_improvement) if self.areas_for_improvement else [],
            'skill_recommendations': json.loads(self.skill_recommendations) if self.skill_recommendations else [],
            'experience_suggestions': json.loads(self.experience_suggestions) if self.experience_suggestions else [],
            'certification_recommendations': json.loads(self.certification_recommendations) if self.certification_recommendations else [],
            'resume_enhancement_tips': json.loads(self.resume_enhancement_tips) if self.resume_enhancement_tips else [],
            'career_progression_advice': json.loads(self.career_progression_advice) if self.career_progression_advice else [],
            'learning_resources': json.loads(self.learning_resources) if self.learning_resources else [],
            'next_steps': json.loads(self.next_steps) if self.next_steps else []
        }
    
    def __repr__(self):
        return f'<FeedbackRecord {self.id}: {self.feedback_type} for {self.candidate_id}>'


class AuditLog(BaseModel):
    """
    System activity tracking and audit trail
    
    Logs all system activities for compliance and debugging
    """
    __tablename__ = 'audit_logs'
    
    # Activity Information
    action = db.Column(db.String(100), nullable=False)  # create, update, delete, evaluate, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # candidate, job_description, evaluation, etc.
    entity_id = db.Column(db.String(36), nullable=False)
    
    # User/System Information
    user_id = db.Column(db.String(100))  # user ID or 'system'
    user_type = db.Column(db.String(20), default='system')  # user, system, api
    source_ip = db.Column(db.String(45))  # supports IPv6
    user_agent = db.Column(db.String(500))
    
    # Change Information
    old_values = db.Column(db.Text)  # JSON object
    new_values = db.Column(db.Text)  # JSON object
    changes_summary = db.Column(db.Text)
    
    # Request Information
    request_id = db.Column(db.String(100))
    session_id = db.Column(db.String(100))
    api_endpoint = db.Column(db.String(200))
    http_method = db.Column(db.String(10))
    
    # Result Information
    success = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_action', 'action'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_date', 'created_at'),
        Index('idx_audit_success', 'success'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type}:{self.entity_id}>'


class SystemMetrics(BaseModel):
    """
    System performance metrics and analytics
    
    Stores aggregated metrics for monitoring and analytics
    """
    __tablename__ = 'system_metrics'
    
    # Metric Information
    metric_type = db.Column(db.String(50), nullable=False)  # evaluations, feedback, performance, etc.
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20))  # count, seconds, percentage, etc.
    
    # Time Information
    period_start = db.Column(db.DateTime(timezone=True), nullable=False)
    period_end = db.Column(db.DateTime(timezone=True), nullable=False)
    granularity = db.Column(db.String(20), nullable=False)  # hourly, daily, weekly, monthly
    
    # Dimensions
    dimensions = db.Column(db.Text)  # JSON object with metric dimensions
    
    # Additional Data
    metric_metadata = db.Column(db.Text)  # JSON object with additional metric data
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_type', 'metric_type'),
        Index('idx_metrics_name', 'metric_name'),
        Index('idx_metrics_period', 'period_start', 'period_end'),
        Index('idx_metrics_granularity', 'granularity'),
        UniqueConstraint('metric_type', 'metric_name', 'period_start', 'granularity',
                        name='unique_metric_period'),
    )
    
    def __repr__(self):
        return f'<SystemMetrics {self.metric_name}: {self.metric_value} {self.metric_unit}>'


# Database utility functions
def init_database(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Create tables if they don't exist (for SQLite)
        if 'sqlite' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            db.create_all()


def get_database_stats():
    """Get database statistics"""
    return {
        'candidates_count': Candidate.query.filter_by(is_active=True).count(),
        'job_descriptions_count': JobDescription.query.filter_by(is_active=True).count(),
        'evaluations_count': Evaluation.query.count(),
        'feedback_records_count': FeedbackRecord.query.count(),
        'component_scores_count': ComponentScore.query.count(),
        'audit_logs_count': AuditLog.query.count(),
        'system_metrics_count': SystemMetrics.query.count()
    }


class EmailRecord(BaseModel):
    """Email sending records and tracking"""
    __tablename__ = 'email_records'
    
    # Email identification
    message_id = db.Column(db.String(255), unique=True, nullable=False, comment="Unique message ID from email service")
    
    # Relationships
    evaluation_id = db.Column(db.String(36), db.ForeignKey('evaluations.id'), nullable=True, comment="Related evaluation ID")
    evaluation = db.relationship('Evaluation', backref=db.backref('email_records', lazy=True))
    
    # Recipient information
    candidate_email = db.Column(db.String(255), nullable=False, comment="Recipient email address")
    candidate_name = db.Column(db.String(255), nullable=True, comment="Recipient name")
    
    # Email content
    subject = db.Column(db.Text, nullable=False, comment="Email subject line")
    template_used = db.Column(db.String(100), nullable=True, comment="Email template used")
    
    # Evaluation context
    relevance_score = db.Column(db.Float, default=0.0, comment="Relevance score for this evaluation")
    
    # Delivery tracking
    status = db.Column(db.String(20), default='pending', comment="Email delivery status")
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True, comment="When email was sent")
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=True, comment="When email was delivered")
    opened_at = db.Column(db.DateTime(timezone=True), nullable=True, comment="When email was opened")
    clicked_at = db.Column(db.DateTime(timezone=True), nullable=True, comment="When links were clicked")
    
    # Error handling
    error_message = db.Column(db.Text, nullable=True, comment="Error message if sending failed")
    retry_count = db.Column(db.Integer, default=0, comment="Number of retry attempts")
    max_retries = db.Column(db.Integer, default=3, comment="Maximum retry attempts")
    
    # Provider information
    email_provider = db.Column(db.String(50), nullable=True, comment="Email service provider used")
    provider_message_id = db.Column(db.String(255), nullable=True, comment="Provider-specific message ID")
    
    # Metadata
    email_metadata = db.Column(JSON, nullable=True, comment="Additional email metadata")
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = [
            'pending', 'queued', 'sending', 'sent', 'delivered', 
            'failed', 'bounced', 'blocked', 'unsubscribed'
        ]
        if status not in valid_statuses:
            raise ValueError(f"Invalid email status: {status}")
        return status
    
    @validates('candidate_email')
    def validate_email(self, key, email):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError(f"Invalid email address: {email}")
        return email
    
    @validates('relevance_score')
    def validate_relevance_score(self, key, score):
        if score is not None and (score < 0 or score > 100):
            raise ValueError("Relevance score must be between 0 and 100")
        return score
    
    @hybrid_property
    def is_delivered(self):
        """Check if email was successfully delivered"""
        return self.status in ['sent', 'delivered']
    
    @hybrid_property
    def is_failed(self):
        """Check if email delivery failed"""
        return self.status in ['failed', 'bounced', 'blocked']
    
    @hybrid_property
    def needs_retry(self):
        """Check if email needs retry"""
        return self.is_failed and self.retry_count < self.max_retries
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'evaluation_id': self.evaluation_id,
            'candidate_email': self.candidate_email,
            'candidate_name': self.candidate_name,
            'subject': self.subject,
            'template_used': self.template_used,
            'relevance_score': self.relevance_score,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'email_provider': self.email_provider,
            'provider_message_id': self.provider_message_id,
            'email_metadata': self.email_metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<EmailRecord {self.message_id} to {self.candidate_email}>'
    
    # Table constraints and indexes
    __table_args__ = (
        Index('idx_email_message_id', 'message_id'),
        Index('idx_email_candidate_email', 'candidate_email'),
        Index('idx_email_status', 'status'),
        Index('idx_email_sent_at', 'sent_at'),
        Index('idx_email_evaluation_id', 'evaluation_id'),
        CheckConstraint('relevance_score >= 0 AND relevance_score <= 100', name='chk_email_relevance_score'),
        CheckConstraint('retry_count >= 0', name='chk_email_retry_count'),
        {'comment': 'Email sending records and delivery tracking'}
    )


# Sample data creation functions for testing
def create_sample_data():
    """Create sample data for testing"""
    try:
        # Sample candidate
        candidate = Candidate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            location="San Francisco, CA",
            resume_filename="john_doe_resume.pdf",
            resume_file_path="/uploads/john_doe_resume.pdf",
            professional_summary="Experienced software developer with 5 years in web development",
            total_experience_years=5.0,
            current_position="Senior Developer",
            current_company="Tech Corp"
        )
        candidate.skills_list = ["Python", "JavaScript", "React", "SQL", "AWS"]
        
        # Sample job description
        job = JobDescription(
            title="Senior Full Stack Developer",
            company_name="Innovation Inc",
            department="Engineering",
            location="San Francisco, CA",
            employment_type="full_time",
            description="Looking for an experienced full stack developer...",
            minimum_experience=3,
            maximum_experience=8,
            salary_min=120000,
            salary_max=180000
        )
        job.required_skills_list = ["Python", "JavaScript", "React", "SQL", "AWS", "Docker"]
        
        db.session.add(candidate)
        db.session.add(job)
        db.session.commit()
        
        # Sample evaluation
        evaluation = Evaluation(
            candidate_id=candidate.id,
            job_description_id=job.id,
            overall_score=78.5,
            suitability_verdict="HIGH",
            confidence_level="HIGH",
            confidence_score=0.85,
            processing_time=2.3,
            semantic_similarity_score=0.82,
            experience_match_score=0.75,
            skill_coverage_score=0.80
        )
        evaluation.strengths_list = [
            "Strong technical skills in required technologies",
            "Relevant experience in web development",
            "Good educational background"
        ]
        
        db.session.add(evaluation)
        db.session.commit()
        
        return {
            'candidate_id': candidate.id,
            'job_id': job.id,
            'evaluation_id': evaluation.id,
            'message': 'Sample data created successfully'
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Failed to create sample data: {str(e)}'}


if __name__ == "__main__":
    print("Resume Relevance System - Database Schema")
    print("==========================================")
    print()
    print("Database Tables:")
    print("- candidates: Candidate information and resume data")
    print("- job_descriptions: Job requirements and specifications") 
    print("- evaluations: Resume evaluation results and scores")
    print("- component_scores: Detailed component-wise scoring")
    print("- feedback_records: LLM-generated feedback and recommendations")
    print("- audit_logs: System activity tracking")
    print("- system_metrics: Performance metrics and analytics")
    print()
    print("Features:")
    print("✓ PostgreSQL and SQLite support")
    print("✓ Comprehensive relationships and constraints")
    print("✓ Proper indexing for performance")
    print("✓ JSON field support for flexible data")
    print("✓ Audit trail and metrics tracking")
    print("✓ Data validation and business rules")
    print()
    print("Ready for integration with Flask application!")
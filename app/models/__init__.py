"""
Database Models Module

This module provides high-level database operations and model management
for the Resume Relevance System. It includes model classes, relationships,
and business logic methods.

Features:
- SQLAlchemy ORM models with Flask integration
- Business logic methods for common operations
- Data validation and serialization
- Query helpers and utilities
- Relationship management

Author: Automated Resume Relevance System
Version: 1.0.0
"""

from .database_schema import (
    db, migrate, BaseModel, Candidate, JobDescription, Evaluation,
    ComponentScore, FeedbackRecord, AuditLog, SystemMetrics, EmailRecord,
    init_database, get_database_stats, create_sample_data
)
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
import json
from typing import List, Dict, Optional, Any, Tuple


class CandidateManager:
    """Manager class for candidate operations"""
    
    @staticmethod
    def create_candidate(candidate_data: Dict[str, Any]) -> Candidate:
        """
        Create a new candidate with resume data
        
        Args:
            candidate_data: Dictionary containing candidate information
            
        Returns:
            Candidate: Created candidate object
        """
        candidate = Candidate()
        
        # Basic information
        candidate.first_name = candidate_data.get('first_name', '').strip()
        candidate.last_name = candidate_data.get('last_name', '').strip()
        candidate.email = candidate_data.get('email', '').strip().lower()
        candidate.phone = candidate_data.get('phone', '').strip()
        candidate.location = candidate_data.get('location', '').strip()
        
        # Resume information
        candidate.resume_filename = candidate_data.get('resume_filename', '')
        candidate.resume_file_path = candidate_data.get('resume_file_path', '')
        candidate.resume_file_size = candidate_data.get('resume_file_size')
        candidate.resume_mime_type = candidate_data.get('resume_mime_type')
        
        # Parse resume data
        if 'parsed_resume_data' in candidate_data:
            candidate.parsed_data = candidate_data['parsed_resume_data']
        
        # Skills and experience
        if 'skills' in candidate_data:
            candidate.skills_list = candidate_data['skills']
        
        if 'work_experience' in candidate_data:
            candidate.work_experience = json.dumps(candidate_data['work_experience'])
        
        if 'education' in candidate_data:
            candidate.education = json.dumps(candidate_data['education'])
        
        if 'certifications' in candidate_data:
            candidate.certifications = json.dumps(candidate_data['certifications'])
        
        # Profile information
        candidate.professional_summary = candidate_data.get('professional_summary')
        candidate.total_experience_years = candidate_data.get('total_experience_years')
        candidate.current_position = candidate_data.get('current_position')
        candidate.current_company = candidate_data.get('current_company')
        
        # Metadata
        candidate.source = candidate_data.get('source', 'web_upload')
        candidate.notes = candidate_data.get('notes')
        
        if 'tags' in candidate_data:
            candidate.tags = json.dumps(candidate_data['tags'])
        
        db.session.add(candidate)
        db.session.commit()
        
        return candidate
    
    @staticmethod
    def get_candidate_by_id(candidate_id: str) -> Optional[Candidate]:
        """Get candidate by ID"""
        return Candidate.query.filter_by(id=candidate_id, is_active=True).first()
    
    @staticmethod
    def get_candidate_by_email(email: str) -> Optional[Candidate]:
        """Get candidate by email"""
        return Candidate.query.filter_by(email=email.lower(), is_active=True).first()
    
    @staticmethod
    def search_candidates(query: str, limit: int = 50) -> List[Candidate]:
        """
        Search candidates by name, email, or skills
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching candidates
        """
        search_term = f"%{query.lower()}%"
        
        return Candidate.query.filter(
            and_(
                Candidate.is_active == True,
                or_(
                    func.lower(Candidate.first_name).like(search_term),
                    func.lower(Candidate.last_name).like(search_term),
                    func.lower(Candidate.email).like(search_term),
                    func.lower(Candidate.current_position).like(search_term),
                    func.lower(Candidate.current_company).like(search_term),
                    func.lower(Candidate.skills).like(search_term)
                )
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_candidates_with_evaluations(limit: int = 100) -> List[Candidate]:
        """Get candidates with their evaluation history"""
        return Candidate.query.filter_by(is_active=True)\
            .options(joinedload(Candidate.evaluations))\
            .limit(limit).all()
    
    @staticmethod
    def update_candidate(candidate_id: str, update_data: Dict[str, Any]) -> Optional[Candidate]:
        """Update candidate information"""
        candidate = CandidateManager.get_candidate_by_id(candidate_id)
        if not candidate:
            return None
        
        candidate.update_from_dict(update_data)
        db.session.commit()
        return candidate
    
    @staticmethod
    def deactivate_candidate(candidate_id: str) -> bool:
        """Deactivate candidate (soft delete)"""
        candidate = CandidateManager.get_candidate_by_id(candidate_id)
        if not candidate:
            return False
        
        candidate.is_active = False
        candidate.updated_at = datetime.utcnow()
        db.session.commit()
        return True


class JobDescriptionManager:
    """Manager class for job description operations"""
    
    @staticmethod
    def create_job_description(job_data: Dict[str, Any]) -> JobDescription:
        """Create a new job description"""
        job = JobDescription()
        
        # Basic information
        job.title = job_data.get('title', '').strip()
        job.company_name = job_data.get('company_name', '').strip()
        job.department = job_data.get('department', '').strip()
        job.location = job_data.get('location', '').strip()
        job.employment_type = job_data.get('employment_type', 'full_time')
        job.remote_option = job_data.get('remote_option', 'on_site')
        
        # Job details
        job.description = job_data.get('description', '')
        
        if 'responsibilities' in job_data:
            job.responsibilities = json.dumps(job_data['responsibilities'])
        
        if 'requirements' in job_data:
            job.requirements = json.dumps(job_data['requirements'])
        
        # Skills and experience
        if 'required_skills' in job_data:
            job.required_skills_list = job_data['required_skills']
        
        if 'preferred_skills' in job_data:
            job.preferred_skills = json.dumps(job_data['preferred_skills'])
        
        job.minimum_experience = job_data.get('minimum_experience')
        job.maximum_experience = job_data.get('maximum_experience')
        
        if 'education_requirements' in job_data:
            job.education_requirements = json.dumps(job_data['education_requirements'])
        
        if 'certifications_required' in job_data:
            job.certifications_required = json.dumps(job_data['certifications_required'])
        
        # Compensation
        job.salary_min = job_data.get('salary_min')
        job.salary_max = job_data.get('salary_max')
        job.currency = job_data.get('currency', 'USD')
        
        if 'benefits' in job_data:
            job.benefits = json.dumps(job_data['benefits'])
        
        # Job posting information
        job.application_deadline = job_data.get('application_deadline')
        job.job_posting_url = job_data.get('job_posting_url')
        job.internal_job_id = job_data.get('internal_job_id')
        
        # Metadata
        job.status = job_data.get('status', 'active')
        job.priority = job_data.get('priority', 'medium')
        job.notes = job_data.get('notes')
        
        if 'tags' in job_data:
            job.tags = json.dumps(job_data['tags'])
        
        db.session.add(job)
        db.session.commit()
        
        return job
    
    @staticmethod
    def get_job_by_id(job_id: str) -> Optional[JobDescription]:
        """Get job description by ID"""
        return JobDescription.query.filter_by(id=job_id, is_active=True).first()
    
    @staticmethod
    def get_active_jobs(limit: int = 100) -> List[JobDescription]:
        """Get all active job descriptions"""
        return JobDescription.query.filter_by(is_active=True, status='active')\
            .order_by(desc(JobDescription.created_at))\
            .limit(limit).all()
    
    @staticmethod
    def search_jobs(query: str, limit: int = 50) -> List[JobDescription]:
        """Search job descriptions by title, company, or skills"""
        search_term = f"%{query.lower()}%"
        
        return JobDescription.query.filter(
            and_(
                JobDescription.is_active == True,
                or_(
                    func.lower(JobDescription.title).like(search_term),
                    func.lower(JobDescription.company_name).like(search_term),
                    func.lower(JobDescription.description).like(search_term),
                    func.lower(JobDescription.required_skills).like(search_term)
                )
            )
        ).limit(limit).all()


class EvaluationManager:
    """Manager class for evaluation operations"""
    
    @staticmethod
    def create_evaluation(evaluation_data: Dict[str, Any]) -> Evaluation:
        """Create a new evaluation record"""
        evaluation = Evaluation()
        
        # Foreign keys
        evaluation.candidate_id = evaluation_data['candidate_id']
        evaluation.job_description_id = evaluation_data['job_description_id']
        
        # Evaluation metadata
        evaluation.evaluation_type = evaluation_data.get('evaluation_type', 'comprehensive')
        evaluation.evaluation_version = evaluation_data.get('evaluation_version', '2.0.0')
        evaluation.evaluation_method = evaluation_data.get('evaluation_method', 'advanced_scorer')
        
        # Overall scores
        evaluation.overall_score = evaluation_data['overall_score']
        evaluation.suitability_verdict = evaluation_data['suitability_verdict']
        evaluation.confidence_level = evaluation_data['confidence_level']
        evaluation.confidence_score = evaluation_data.get('confidence_score')
        
        # Processing information
        evaluation.processing_time = evaluation_data.get('processing_time')
        evaluation.analysis_method = evaluation_data.get('analysis_method')
        evaluation.model_version = evaluation_data.get('model_version')
        
        # Detailed results
        if 'component_scores' in evaluation_data:
            evaluation.component_scores_dict = evaluation_data['component_scores']
        
        if 'strengths' in evaluation_data:
            evaluation.strengths = json.dumps(evaluation_data['strengths'])
        
        if 'weaknesses' in evaluation_data:
            evaluation.weaknesses = json.dumps(evaluation_data['weaknesses'])
        
        if 'recommendations' in evaluation_data:
            evaluation.recommendations = json.dumps(evaluation_data['recommendations'])
        
        # Analysis details
        evaluation.semantic_similarity_score = evaluation_data.get('semantic_similarity_score')
        evaluation.experience_match_score = evaluation_data.get('experience_match_score')
        evaluation.skill_coverage_score = evaluation_data.get('skill_coverage_score')
        
        if 'keyword_matches' in evaluation_data:
            evaluation.keyword_matches = json.dumps(evaluation_data['keyword_matches'])
        
        # Context
        evaluation.evaluation_notes = evaluation_data.get('evaluation_notes')
        evaluation.evaluator_id = evaluation_data.get('evaluator_id', 'system')
        evaluation.evaluation_source = evaluation_data.get('evaluation_source', 'system')
        
        db.session.add(evaluation)
        db.session.flush()  # Get the ID before creating component scores
        
        # Create component scores if provided
        if 'component_breakdown' in evaluation_data:
            for component in evaluation_data['component_breakdown']:
                component_score = ComponentScore(  # type: ignore
                    evaluation_id=evaluation.id,
                    component_name=component.get('name', ''),
                    component_type=component.get('type', 'general'),
                    component_weight=component.get('weight', 0.0),
                    raw_score=component.get('score', 0.0),
                    weighted_score=component.get('score', 0.0) * component.get('weight', 0.0),
                    normalized_score=component.get('score', 0.0),
                    evidence=json.dumps(component.get('evidence', [])),
                    methodology=component.get('methodology', ''),
                    confidence=component.get('confidence', 0.0)
                )
                db.session.add(component_score)
        
        db.session.commit()
        return evaluation
    
    @staticmethod
    def get_evaluation_by_id(evaluation_id: str) -> Optional[Evaluation]:
        """Get evaluation by ID with component scores"""
        return Evaluation.query.filter_by(id=evaluation_id)\
            .options(joinedload(Evaluation.component_scores_rel))\
            .first()
    
    @staticmethod
    def get_candidate_evaluations(candidate_id: str, limit: int = 50) -> List[Evaluation]:
        """Get all evaluations for a candidate"""
        return Evaluation.query.filter_by(candidate_id=candidate_id)\
            .order_by(desc(Evaluation.created_at))\
            .limit(limit).all()
    
    @staticmethod
    def get_job_evaluations(job_id: str, limit: int = 100) -> List[Evaluation]:
        """Get all evaluations for a job"""
        return Evaluation.query.filter_by(job_description_id=job_id)\
            .order_by(desc(Evaluation.overall_score))\
            .limit(limit).all()
    
    @staticmethod
    def get_top_candidates(job_id: str, limit: int = 10) -> List[Tuple[Evaluation, Candidate]]:
        """Get top candidates for a job based on evaluation scores"""
        return db.session.query(Evaluation, Candidate)\
            .join(Candidate)\
            .filter(Evaluation.job_description_id == job_id)\
            .filter(Candidate.is_active == True)\
            .order_by(desc(Evaluation.overall_score))\
            .limit(limit).all()
    
    @staticmethod
    def get_evaluation_statistics(job_id: str = None) -> Dict[str, Any]:
        """Get evaluation statistics"""
        query = Evaluation.query
        if job_id:
            query = query.filter_by(job_description_id=job_id)
        
        evaluations = query.all()
        
        if not evaluations:
            return {'count': 0}
        
        scores = [e.overall_score for e in evaluations]
        verdicts = [e.suitability_verdict for e in evaluations]
        
        return {
            'count': len(evaluations),
            'average_score': sum(scores) / len(scores),
            'median_score': sorted(scores)[len(scores) // 2],
            'min_score': min(scores),
            'max_score': max(scores),
            'high_suitability': len([v for v in verdicts if v == 'HIGH']),
            'medium_suitability': len([v for v in verdicts if v == 'MEDIUM']),
            'low_suitability': len([v for v in verdicts if v == 'LOW']),
            'score_distribution': {
                'excellent (90+)': len([s for s in scores if s >= 90]),
                'good (70-89)': len([s for s in scores if 70 <= s < 90]),
                'fair (50-69)': len([s for s in scores if 50 <= s < 70]),
                'poor (<50)': len([s for s in scores if s < 50])
            }
        }


class FeedbackManager:
    """Manager class for feedback operations"""
    
    @staticmethod
    def create_feedback_record(feedback_data: Dict[str, Any]) -> FeedbackRecord:
        """Create a new feedback record"""
        feedback = FeedbackRecord()
        
        # Foreign keys
        feedback.candidate_id = feedback_data['candidate_id']
        feedback.evaluation_id = feedback_data.get('evaluation_id')
        feedback.job_description_id = feedback_data.get('job_description_id')
        
        # Configuration
        feedback.feedback_type = feedback_data['feedback_type']
        feedback.feedback_tone = feedback_data['feedback_tone']
        feedback.llm_provider = feedback_data['llm_provider']
        feedback.model_name = feedback_data.get('model_name')
        
        # Content
        feedback.executive_summary = feedback_data.get('executive_summary')
        
        if 'strengths' in feedback_data:
            feedback.strengths = json.dumps(feedback_data['strengths'])
        
        if 'areas_for_improvement' in feedback_data:
            feedback.areas_for_improvement = json.dumps(feedback_data['areas_for_improvement'])
        
        if 'skill_recommendations' in feedback_data:
            feedback.skill_recommendations = json.dumps(feedback_data['skill_recommendations'])
        
        if 'experience_suggestions' in feedback_data:
            feedback.experience_suggestions = json.dumps(feedback_data['experience_suggestions'])
        
        if 'certification_recommendations' in feedback_data:
            feedback.certification_recommendations = json.dumps(feedback_data['certification_recommendations'])
        
        if 'resume_enhancement_tips' in feedback_data:
            feedback.resume_enhancement_tips = json.dumps(feedback_data['resume_enhancement_tips'])
        
        if 'career_progression_advice' in feedback_data:
            feedback.career_progression_advice = json.dumps(feedback_data['career_progression_advice'])
        
        if 'learning_resources' in feedback_data:
            feedback.learning_resources = json.dumps(feedback_data['learning_resources'])
        
        if 'next_steps' in feedback_data:
            feedback.next_steps = json.dumps(feedback_data['next_steps'])
        
        # Metadata
        feedback.processing_time = feedback_data.get('processing_time')
        feedback.token_usage = feedback_data.get('token_usage')
        feedback.cost_estimate = feedback_data.get('cost_estimate')
        feedback.generation_quality = feedback_data.get('generation_quality', 'good')
        
        db.session.add(feedback)
        db.session.commit()
        return feedback
    
    @staticmethod
    def get_candidate_feedback(candidate_id: str, limit: int = 10) -> List[FeedbackRecord]:
        """Get all feedback for a candidate"""
        return FeedbackRecord.query.filter_by(candidate_id=candidate_id)\
            .order_by(desc(FeedbackRecord.created_at))\
            .limit(limit).all()


class AuditManager:
    """Manager class for audit operations"""
    
    @staticmethod
    def log_activity(action: str, entity_type: str, entity_id: str, 
                    user_id: str = 'system', success: bool = True,
                    old_values: Dict = None, new_values: Dict = None,
                    error_message: str = None, **kwargs) -> AuditLog:
        """Log system activity"""
        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            success=success,
            error_message=error_message
        )
        
        if old_values:
            audit_log.old_values = json.dumps(old_values)
        
        if new_values:
            audit_log.new_values = json.dumps(new_values)
        
        # Add additional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(audit_log, key):
                setattr(audit_log, key, value)
        
        db.session.add(audit_log)
        db.session.commit()
        return audit_log
    
    @staticmethod
    def get_entity_audit_trail(entity_type: str, entity_id: str, limit: int = 50) -> List[AuditLog]:
        """Get audit trail for a specific entity"""
        return AuditLog.query.filter_by(entity_type=entity_type, entity_id=entity_id)\
            .order_by(desc(AuditLog.created_at))\
            .limit(limit).all()


# Export all models and managers
__all__ = [
    'db', 'migrate', 'init_database', 'get_database_stats', 'create_sample_data',
    'BaseModel', 'Candidate', 'JobDescription', 'Evaluation', 
    'ComponentScore', 'FeedbackRecord', 'AuditLog', 'SystemMetrics',
    'CandidateManager', 'JobDescriptionManager', 'EvaluationManager',
    'FeedbackManager', 'AuditManager'
]
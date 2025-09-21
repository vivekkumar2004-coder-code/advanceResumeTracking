"""
Database API Routes

This module provides API endpoints for database operations including
saving and retrieving evaluation results, managing candidates, job descriptions,
and feedback records.

Features:
- Candidate management endpoints
- Job description management
- Evaluation storage and retrieval
- Feedback management
- Search and analytics
- Audit trail access

Author: Automated Resume Relevance System
Version: 1.0.0
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import json
import traceback
from sqlalchemy import text

from ..models import (
    db, Candidate, JobDescription, Evaluation, FeedbackRecord, AuditLog,
    CandidateManager, JobDescriptionManager, EvaluationManager,
    FeedbackManager, AuditManager
)

# Create blueprint
db_routes = Blueprint('database', __name__)


# Error handlers
def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Handle API errors consistently"""
    error_id = str(uuid.uuid4())
    error_message = f"{context}: {str(error)}" if context else str(error)
    
    # Log error
    current_app.logger.error(f"API Error {error_id}: {error_message}")
    current_app.logger.error(f"Traceback: {traceback.format_exc()}")
    
    return {
        'error': True,
        'error_id': error_id,
        'message': error_message,
        'timestamp': datetime.utcnow().isoformat()
    }


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Optional[Dict[str, Any]]:
    """Validate required fields in request data"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return {
            'error': True,
            'message': f"Missing required fields: {', '.join(missing_fields)}",
            'missing_fields': missing_fields
        }
    
    return None


# ================================
# CANDIDATE MANAGEMENT ENDPOINTS
# ================================

@db_routes.route('/candidates', methods=['POST'])
def create_candidate():
    """
    Create a new candidate record
    
    POST /api/database/candidates
    
    Body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "resume_filename": "resume.pdf",
        "resume_file_path": "/uploads/resume.pdf",
        "skills": ["Python", "Machine Learning"],
        "work_experience": [...],
        "education": [...],
        ...
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify(validation_error), 400
        
        # Check if candidate already exists
        existing_candidate = CandidateManager.get_candidate_by_email(data['email'])
        if existing_candidate:
            return jsonify({
                'error': True,
                'message': 'Candidate with this email already exists',
                'existing_candidate_id': existing_candidate.id
            }), 409
        
        # Create candidate
        candidate = CandidateManager.create_candidate(data)
        
        # Log activity
        AuditManager.log_activity(
            action='CREATE',
            entity_type='candidate',
            entity_id=candidate.id,
            user_id=request.headers.get('X-User-ID', 'api_user'),
            new_values={'email': candidate.email, 'name': f"{candidate.first_name} {candidate.last_name}"}
        )
        
        return jsonify({
            'success': True,
            'message': 'Candidate created successfully',
            'candidate_id': candidate.id,
            'candidate': candidate.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to create candidate")), 500


@db_routes.route('/candidates/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id: str):
    """Get candidate by ID"""
    try:
        candidate = CandidateManager.get_candidate_by_id(candidate_id)
        if not candidate:
            return jsonify({'error': True, 'message': 'Candidate not found'}), 404
        
        return jsonify({
            'success': True,
            'candidate': candidate.to_dict()
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get candidate {candidate_id}")), 500


@db_routes.route('/candidates/search', methods=['GET'])
def search_candidates():
    """
    Search candidates
    
    GET /api/database/candidates/search?q=john&limit=50
    """
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 50)), 100)
        
        if not query:
            return jsonify({'error': True, 'message': 'Search query is required'}), 400
        
        candidates = CandidateManager.search_candidates(query, limit)
        
        return jsonify({
            'success': True,
            'count': len(candidates),
            'candidates': [candidate.to_dict() for candidate in candidates]
        })
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to search candidates")), 500


@db_routes.route('/candidates/<candidate_id>/evaluations', methods=['GET'])
def get_candidate_evaluations(candidate_id: str):
    """Get all evaluations for a candidate"""
    try:
        candidate = CandidateManager.get_candidate_by_id(candidate_id)
        if not candidate:
            return jsonify({'error': True, 'message': 'Candidate not found'}), 404
        
        limit = min(int(request.args.get('limit', 50)), 100)
        evaluations = EvaluationManager.get_candidate_evaluations(candidate_id, limit)
        
        return jsonify({
            'success': True,
            'candidate_id': candidate_id,
            'count': len(evaluations),
            'evaluations': [eval.to_dict() for eval in evaluations]
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get evaluations for candidate {candidate_id}")), 500


# ================================
# JOB DESCRIPTION ENDPOINTS
# ================================

@db_routes.route('/jobs', methods=['POST'])
def create_job_description():
    """
    Create a new job description
    
    POST /api/database/jobs
    
    Body:
    {
        "title": "Senior Python Developer",
        "company_name": "Tech Corp",
        "description": "...",
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "minimum_experience": 3,
        ...
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'company_name', 'description']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify(validation_error), 400
        
        # Create job description
        job = JobDescriptionManager.create_job_description(data)
        
        # Log activity
        AuditManager.log_activity(
            action='CREATE',
            entity_type='job_description',
            entity_id=job.id,
            user_id=request.headers.get('X-User-ID', 'api_user'),
            new_values={'title': job.title, 'company': job.company_name}
        )
        
        return jsonify({
            'success': True,
            'message': 'Job description created successfully',
            'job_id': job.id,
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to create job description")), 500


@db_routes.route('/jobs/<job_id>', methods=['GET'])
def get_job_description(job_id: str):
    """Get job description by ID"""
    try:
        job = JobDescriptionManager.get_job_by_id(job_id)
        if not job:
            return jsonify({'error': True, 'message': 'Job description not found'}), 404
        
        return jsonify({
            'success': True,
            'job': job.to_dict()
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get job description {job_id}")), 500


@db_routes.route('/jobs', methods=['GET'])
def get_active_jobs():
    """Get all active job descriptions"""
    try:
        limit = min(int(request.args.get('limit', 100)), 200)
        jobs = JobDescriptionManager.get_active_jobs(limit)
        
        return jsonify({
            'success': True,
            'count': len(jobs),
            'jobs': [job.to_dict() for job in jobs]
        })
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to get active jobs")), 500


@db_routes.route('/jobs/<job_id>/evaluations', methods=['GET'])
def get_job_evaluations(job_id: str):
    """Get all evaluations for a job"""
    try:
        job = JobDescriptionManager.get_job_by_id(job_id)
        if not job:
            return jsonify({'error': True, 'message': 'Job description not found'}), 404
        
        limit = min(int(request.args.get('limit', 100)), 200)
        evaluations = EvaluationManager.get_job_evaluations(job_id, limit)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'count': len(evaluations),
            'evaluations': [eval.to_dict() for eval in evaluations]
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get evaluations for job {job_id}")), 500


@db_routes.route('/jobs/<job_id>/top-candidates', methods=['GET'])
def get_top_candidates(job_id: str):
    """Get top candidates for a job based on evaluation scores"""
    try:
        job = JobDescriptionManager.get_job_by_id(job_id)
        if not job:
            return jsonify({'error': True, 'message': 'Job description not found'}), 404
        
        limit = min(int(request.args.get('limit', 10)), 50)
        top_candidates = EvaluationManager.get_top_candidates(job_id, limit)
        
        results = []
        for evaluation, candidate in top_candidates:
            results.append({
                'candidate': candidate.to_dict(),
                'evaluation': evaluation.to_dict(),
                'score': evaluation.overall_score,
                'suitability': evaluation.suitability_verdict
            })
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'count': len(results),
            'top_candidates': results
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get top candidates for job {job_id}")), 500


# ================================
# EVALUATION ENDPOINTS
# ================================

@db_routes.route('/evaluations', methods=['POST'])
def save_evaluation_result():
    """
    Save an evaluation result to the database
    
    POST /api/database/evaluations
    
    Body:
    {
        "candidate_id": "...",
        "job_description_id": "...",
        "overall_score": 85.5,
        "suitability_verdict": "HIGH",
        "confidence_level": "high",
        "component_scores": {...},
        "strengths": [...],
        "weaknesses": [...],
        ...
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['candidate_id', 'job_description_id', 'overall_score', 'suitability_verdict', 'confidence_level']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify(validation_error), 400
        
        # Verify candidate and job exist
        candidate = CandidateManager.get_candidate_by_id(data['candidate_id'])
        if not candidate:
            return jsonify({'error': True, 'message': 'Candidate not found'}), 404
        
        job = JobDescriptionManager.get_job_by_id(data['job_description_id'])
        if not job:
            return jsonify({'error': True, 'message': 'Job description not found'}), 404
        
        # Create evaluation
        evaluation = EvaluationManager.create_evaluation(data)
        
        # Log activity
        AuditManager.log_activity(
            action='CREATE',
            entity_type='evaluation',
            entity_id=evaluation.id,
            user_id=request.headers.get('X-User-ID', 'api_user'),
            new_values={
                'candidate_id': data['candidate_id'],
                'job_id': data['job_description_id'],
                'score': data['overall_score']
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Evaluation saved successfully',
            'evaluation_id': evaluation.id,
            'evaluation': evaluation.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to save evaluation")), 500


@db_routes.route('/evaluations/<evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id: str):
    """Get evaluation by ID with component scores"""
    try:
        evaluation = EvaluationManager.get_evaluation_by_id(evaluation_id)
        if not evaluation:
            return jsonify({'error': True, 'message': 'Evaluation not found'}), 404
        
        return jsonify({
            'success': True,
            'evaluation': evaluation.to_dict()
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get evaluation {evaluation_id}")), 500


@db_routes.route('/evaluations/statistics', methods=['GET'])
def get_evaluation_statistics():
    """
    Get evaluation statistics
    
    GET /api/database/evaluations/statistics?job_id=...
    """
    try:
        job_id = request.args.get('job_id')
        
        if job_id:
            # Verify job exists
            job = JobDescriptionManager.get_job_by_id(job_id)
            if not job:
                return jsonify({'error': True, 'message': 'Job description not found'}), 404
        
        stats = EvaluationManager.get_evaluation_statistics(job_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to get evaluation statistics")), 500


# ================================
# FEEDBACK ENDPOINTS
# ================================

@db_routes.route('/feedback', methods=['POST'])
def save_feedback_record():
    """
    Save feedback record to database
    
    POST /api/database/feedback
    
    Body:
    {
        "candidate_id": "...",
        "evaluation_id": "...",
        "feedback_type": "comprehensive",
        "feedback_tone": "professional",
        "llm_provider": "openai",
        "executive_summary": "...",
        "strengths": [...],
        "areas_for_improvement": [...],
        ...
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['candidate_id', 'feedback_type', 'feedback_tone', 'llm_provider']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify(validation_error), 400
        
        # Verify candidate exists
        candidate = CandidateManager.get_candidate_by_id(data['candidate_id'])
        if not candidate:
            return jsonify({'error': True, 'message': 'Candidate not found'}), 404
        
        # Verify evaluation exists if provided
        if 'evaluation_id' in data and data['evaluation_id']:
            evaluation = EvaluationManager.get_evaluation_by_id(data['evaluation_id'])
            if not evaluation:
                return jsonify({'error': True, 'message': 'Evaluation not found'}), 404
        
        # Create feedback record
        feedback = FeedbackManager.create_feedback_record(data)
        
        # Log activity
        AuditManager.log_activity(
            action='CREATE',
            entity_type='feedback',
            entity_id=feedback.id,
            user_id=request.headers.get('X-User-ID', 'api_user'),
            new_values={
                'candidate_id': data['candidate_id'],
                'feedback_type': data['feedback_type'],
                'provider': data['llm_provider']
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Feedback saved successfully',
            'feedback_id': feedback.id,
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to save feedback")), 500


@db_routes.route('/candidates/<candidate_id>/feedback', methods=['GET'])
def get_candidate_feedback(candidate_id: str):
    """Get all feedback records for a candidate"""
    try:
        candidate = CandidateManager.get_candidate_by_id(candidate_id)
        if not candidate:
            return jsonify({'error': True, 'message': 'Candidate not found'}), 404
        
        limit = min(int(request.args.get('limit', 10)), 50)
        feedback_records = FeedbackManager.get_candidate_feedback(candidate_id, limit)
        
        return jsonify({
            'success': True,
            'candidate_id': candidate_id,
            'count': len(feedback_records),
            'feedback_records': [feedback.to_dict() for feedback in feedback_records]
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get feedback for candidate {candidate_id}")), 500


# ================================
# AUDIT AND ANALYTICS ENDPOINTS
# ================================

@db_routes.route('/audit/<entity_type>/<entity_id>', methods=['GET'])
def get_audit_trail(entity_type: str, entity_id: str):
    """Get audit trail for an entity"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        audit_logs = AuditManager.get_entity_audit_trail(entity_type, entity_id, limit)
        
        return jsonify({
            'success': True,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'count': len(audit_logs),
            'audit_trail': [log.to_dict() for log in audit_logs]
        })
        
    except Exception as e:
        return jsonify(handle_error(e, f"Failed to get audit trail for {entity_type}:{entity_id}")), 500


@db_routes.route('/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get analytics dashboard data"""
    try:
        # Get counts
        total_candidates = Candidate.query.filter_by(is_active=True).count()
        total_jobs = JobDescription.query.filter_by(is_active=True).count()
        total_evaluations = Evaluation.query.count()
        total_feedback = FeedbackRecord.query.count()
        
        # Get recent activity
        recent_evaluations = Evaluation.query.order_by(Evaluation.created_at.desc()).limit(10).all()
        recent_candidates = Candidate.query.filter_by(is_active=True).order_by(Candidate.created_at.desc()).limit(10).all()
        
        # Get score distribution
        evaluations = Evaluation.query.all()
        score_stats = EvaluationManager.get_evaluation_statistics()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'totals': {
                    'candidates': total_candidates,
                    'jobs': total_jobs,
                    'evaluations': total_evaluations,
                    'feedback_records': total_feedback
                },
                'recent_evaluations': [eval.to_dict() for eval in recent_evaluations],
                'recent_candidates': [candidate.to_dict() for candidate in recent_candidates],
                'score_statistics': score_stats,
                'updated_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify(handle_error(e, "Failed to get analytics dashboard")), 500


# ================================
# HEALTH CHECK
# ================================

@db_routes.route('/health', methods=['GET'])
def health_check():
    """Database health check endpoint"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        
        # Get basic stats
        stats = {
            'database_connected': True,
            'total_candidates': Candidate.query.count(),
            'total_jobs': JobDescription.query.count(),
            'total_evaluations': Evaluation.query.count(),
            'total_feedback': FeedbackRecord.query.count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'stats': stats
        })
        
    except Exception as e:
        return jsonify(handle_error(e, "Database health check failed")), 500


# Register error handlers
@db_routes.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': True,
        'message': 'Endpoint not found',
        'status_code': 404
    }), 404


@db_routes.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': True,
        'message': 'Method not allowed',
        'status_code': 405
    }), 405


@db_routes.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': True,
        'message': 'Internal server error',
        'status_code': 500
    }), 500


# Export blueprint
__all__ = ['db_routes']
from flask import Blueprint, request, jsonify
import os
import time
import logging
from datetime import datetime
from ..utils.relevance_analyzer import (
    analyze_resume_relevance, analyze_resume_relevance_advanced, 
    batch_analyze_resumes_advanced, get_scoring_summary,
    generate_personalized_feedback, generate_skill_focused_feedback,
    generate_experience_focused_feedback, generate_certification_focused_feedback,
    batch_generate_candidate_feedback, compare_candidate_feedback
)
from app.utils.file_handler import get_file_path, extract_text_from_file
from app.utils.resume_parser import parse_resume_file
from app.utils.semantic_similarity import create_enhanced_similarity_engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('evaluation', __name__, url_prefix='/api')

def log_request(endpoint_name, data=None):
    """Log incoming requests for debugging"""
    try:
        logger.info(f"API Request to {endpoint_name}: {data}")
    except Exception as e:
        logger.error(f"Error logging request: {e}")

def handle_api_error(error, endpoint_name, status_code=500):
    """Centralized error handling for API endpoints"""
    error_msg = str(error)
    logger.error(f"Error in {endpoint_name}: {error_msg}")
    return jsonify({
        'error': f'{endpoint_name} failed: {error_msg}',
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint_name
    }), status_code

def validate_file_ids(resume_id=None, job_description_id=None):
    """Validate that file IDs are provided and files exist"""
    errors = []
    
    if resume_id:
        resume_path = get_file_path(resume_id, 'resumes')
        if not resume_path:
            errors.append(f'Resume file not found: {resume_id}')
        elif not os.path.exists(resume_path):
            errors.append(f'Resume file does not exist: {resume_path}')
    
    if job_description_id:
        job_desc_path = get_file_path(job_description_id, 'job_descriptions')
        if not job_desc_path:
            errors.append(f'Job description file not found: {job_description_id}')
        elif not os.path.exists(job_desc_path):
            errors.append(f'Job description file does not exist: {job_desc_path}')
    
    return errors

@bp.route('/evaluate', methods=['POST'])
def evaluate_resume():
    """Evaluate resume relevance against a job description"""
    start_time = time.time()
    
    try:
        data = request.json
        log_request('evaluate', data)
        
        if not data:
            logger.warning("No data provided in evaluate request")
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description_id = data.get('job_description_id')
        
        if not resume_id or not job_description_id:
            logger.warning(f"Missing required IDs: resume_id={resume_id}, job_description_id={job_description_id}")
            return jsonify({'error': 'Both resume_id and job_description_id are required'}), 400
        
        # Validate files exist
        validation_errors = validate_file_ids(resume_id, job_description_id)
        if validation_errors:
            logger.warning(f"File validation errors: {validation_errors}")
            return jsonify({'error': '; '.join(validation_errors)}), 404
        
        # Get file paths
        resume_path = get_file_path(resume_id, 'resumes')
        job_desc_path = get_file_path(job_description_id, 'job_descriptions')
        
        logger.info(f"Processing files: resume={resume_path}, job_desc={job_desc_path}")
        
        # Extract text from files
        resume_text = extract_text_from_file(resume_path, enhanced=False)
        job_desc_text = extract_text_from_file(job_desc_path, enhanced=False)
        
        if not resume_text or not job_desc_text:
            logger.error(f"Text extraction failed: resume_text={bool(resume_text)}, job_desc_text={bool(job_desc_text)}")
            return jsonify({'error': 'Failed to extract text from files'}), 500
        
        logger.info(f"Text extracted successfully: resume={len(resume_text)} chars, job_desc={len(job_desc_text)} chars")
        
        # Analyze relevance
        analysis_result = analyze_resume_relevance(resume_text, job_desc_text)
        
        # Add metadata to response
        analysis_result.update({
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat(),
            'resume_id': resume_id,
            'job_description_id': job_description_id
        })
        
        logger.info(f"Analysis completed successfully in {analysis_result['processing_time']}s")
        return jsonify(analysis_result), 200
        
    except Exception as e:
        return handle_api_error(e, 'evaluate')

@bp.route('/evaluate-enhanced', methods=['POST'])
def evaluate_resume_enhanced():
    """Evaluate resume with detailed entity extraction and parsing"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description_id = data.get('job_description_id')
        
        if not resume_id or not job_description_id:
            return jsonify({'error': 'Both resume_id and job_description_id are required'}), 400
        
        # Get file paths
        resume_path = get_file_path(resume_id, 'resumes')
        job_desc_path = get_file_path(job_description_id, 'job_descriptions')
        
        if not resume_path or not job_desc_path:
            return jsonify({'error': 'One or more files not found'}), 404
        
        # Enhanced parsing for resume
        resume_data = extract_text_from_file(resume_path, enhanced=True)
        job_desc_text = extract_text_from_file(job_desc_path, enhanced=False)
        
        if not resume_data or not job_desc_text:
            return jsonify({'error': 'Failed to extract text from files'}), 500
        
        # Handle enhanced parsing results
        if isinstance(resume_data, dict) and 'raw_text' in resume_data:
            resume_text = resume_data['raw_text']
            resume_entities = resume_data.get('entities', {})
            resume_sections = resume_data.get('sections', {})
        else:
            resume_text = str(resume_data)
            resume_entities = {}
            resume_sections = {}
        
        # Perform standard relevance analysis
        analysis_result = analyze_resume_relevance(resume_text, job_desc_text)
        
        # Enhance with detailed entity information
        enhanced_analysis = {
            **analysis_result,
            'detailed_parsing': {
                'resume_entities': resume_entities,
                'resume_sections': {k: v[:200] + '...' if len(v) > 200 else v 
                                  for k, v in resume_sections.items()},  # Truncate for response size
                'parsing_metadata': resume_data.get('metadata', {}) if isinstance(resume_data, dict) else {}
            }
        }
        
        # Add detailed skill analysis if entities were extracted
        if resume_entities and 'skills' in resume_entities:
            extracted_skills = resume_entities['skills'].get('technical_skills', [])
            enhanced_analysis['extracted_technical_skills'] = extracted_skills
            enhanced_analysis['skill_extraction_confidence'] = 'high' if len(extracted_skills) > 5 else 'medium'
        
        # Add experience analysis
        if resume_entities and 'experience' in resume_entities:
            experience_details = resume_entities['experience']
            enhanced_analysis['experience_summary'] = {
                'total_positions': len(experience_details),
                'positions': [
                    {
                        'title': exp.get('title', 'Unknown'),
                        'duration': exp.get('duration', 'Not specified')
                    } for exp in experience_details[:3]  # Show first 3 positions
                ]
            }
        
        # Add certification analysis
        if resume_entities and 'certifications' in resume_entities:
            certifications = resume_entities['certifications']
            enhanced_analysis['certifications_found'] = certifications[:5]  # Show first 5
        
        return jsonify(enhanced_analysis), 200
    
    except Exception as e:
        return jsonify({'error': f'Enhanced evaluation failed: {str(e)}'}), 500

@bp.route('/batch-evaluate', methods=['POST'])
def batch_evaluate_resumes():
    """Evaluate multiple resumes against a job description"""
    start_time = time.time()
    
    try:
        data = request.json
        log_request('batch-evaluate', data)
        
        if not data:
            logger.warning("No data provided in batch-evaluate request")
            return jsonify({'error': 'No data provided'}), 400
        
        resume_ids = data.get('resume_ids', [])
        job_description_id = data.get('job_description_id')
        
        if not resume_ids or not job_description_id:
            logger.warning(f"Missing required data: resume_ids={len(resume_ids) if resume_ids else 0}, job_description_id={job_description_id}")
            return jsonify({'error': 'Both resume_ids and job_description_id are required'}), 400
        
        if not isinstance(resume_ids, list):
            logger.warning(f"resume_ids must be a list, got: {type(resume_ids)}")
            return jsonify({'error': 'resume_ids must be a list'}), 400
        
        # Validate job description exists
        validation_errors = validate_file_ids(job_description_id=job_description_id)
        if validation_errors:
            logger.warning(f"Job description validation failed: {validation_errors}")
            return jsonify({'error': '; '.join(validation_errors)}), 404
        
        # Get job description text
        job_desc_path = get_file_path(job_description_id, 'job_descriptions')
        job_desc_text = extract_text_from_file(job_desc_path)
        
        if not job_desc_text:
            logger.error("Failed to extract text from job description")
            return jsonify({'error': 'Failed to extract text from job description'}), 500
        
        logger.info(f"Starting batch evaluation of {len(resume_ids)} resumes against job description {job_description_id}")
        
        results = []
        successful_evaluations = 0
        
        for i, resume_id in enumerate(resume_ids):
            try:
                logger.debug(f"Processing resume {i+1}/{len(resume_ids)}: {resume_id}")
                
                resume_path = get_file_path(resume_id, 'resumes')
                if not resume_path:
                    logger.warning(f"Resume not found: {resume_id}")
                    results.append({
                        'resume_id': resume_id,
                        'error': 'Resume not found'
                    })
                    continue
                
                if not os.path.exists(resume_path):
                    logger.warning(f"Resume file does not exist: {resume_path}")
                    results.append({
                        'resume_id': resume_id,
                        'error': 'Resume file does not exist'
                    })
                    continue
                
                resume_text = extract_text_from_file(resume_path)
                if not resume_text:
                    logger.warning(f"Failed to extract text from resume: {resume_id}")
                    results.append({
                        'resume_id': resume_id,
                        'error': 'Failed to extract text from resume'
                    })
                    continue
                
                analysis_result = analyze_resume_relevance(resume_text, job_desc_text)
                analysis_result['resume_id'] = resume_id
                results.append(analysis_result)
                successful_evaluations += 1
                
                logger.debug(f"Successfully analyzed resume {resume_id}: score={analysis_result.get('relevance_score', 0)}")
                
            except Exception as e:
                logger.error(f"Error processing resume {resume_id}: {e}")
                results.append({
                    'resume_id': resume_id,
                    'error': f'Evaluation failed: {str(e)}'
                })
        
        # Sort results by relevance score (highest first)
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        processing_time = round(time.time() - start_time, 2)
        
        response_data = {
            'job_description_id': job_description_id,
            'total_resumes': len(resume_ids),
            'successful_evaluations': successful_evaluations,
            'failed_evaluations': len(resume_ids) - successful_evaluations,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        logger.info(f"Batch evaluation completed: {successful_evaluations}/{len(resume_ids)} successful in {processing_time}s")
        return jsonify(response_data), 200
        
    except Exception as e:
        return handle_api_error(e, 'batch-evaluate')

@bp.route('/analyze-keywords', methods=['POST'])
def analyze_keywords():
    """Extract and analyze keywords from a job description"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        job_description_id = data.get('job_description_id')
        
        if not job_description_id:
            return jsonify({'error': 'job_description_id is required'}), 400
        
        # Get job description text
        job_desc_path = get_file_path(job_description_id, 'job_descriptions')
        if not job_desc_path:
            return jsonify({'error': 'Job description not found'}), 404
        
        job_desc_text = extract_text_from_file(job_desc_path)
        if not job_desc_text:
            return jsonify({'error': 'Failed to extract text from job description'}), 500
        
        # Extract keywords and requirements
        from app.utils.keyword_extractor import extract_keywords_and_requirements
        keywords_analysis = extract_keywords_and_requirements(job_desc_text)
        
        return jsonify({
            'job_description_id': job_description_id,
            **keywords_analysis
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Keyword analysis failed: {str(e)}'}), 500


@bp.route('/evaluate-semantic', methods=['POST'])
def evaluate_resume_semantic():
    """
    Enhanced resume evaluation using semantic similarity and skill normalization
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description_data = data.get('job_description')
        
        if not resume_id:
            return jsonify({'error': 'resume_id is required'}), 400
        
        if not job_description_data:
            return jsonify({'error': 'job_description data is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, 'resumes')
        if not resume_path:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Parse resume with enhanced parsing and skill normalization
        resume_data = parse_resume_file(resume_path)
        
        if 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data["error"]}'}), 500
        
        # Initialize semantic similarity engine
        similarity_engine = create_enhanced_similarity_engine()
        
        # Prepare resume data for similarity calculation
        resume_analysis_data = {
            'skills': resume_data['entities']['skills'].get('technical_skills', []) + 
                     resume_data['entities']['skills'].get('soft_skills', []),
            'certifications': resume_data['entities']['certifications'],
            'experience': resume_data['entities'].get('experience', []),
            'full_text': resume_data['raw_text']
        }
        
        # Calculate comprehensive similarity
        similarity_result = similarity_engine.calculate_comprehensive_similarity(
            resume_analysis_data, job_description_data
        )
        
        # Prepare response with enhanced analysis
        response = {
            'resume_id': resume_id,
            'overall_similarity_score': similarity_result['overall_similarity_score'],
            'match_quality': similarity_result['detailed_analysis']['match_quality'],
            'component_scores': similarity_result['component_scores'],
            'skill_analysis': {
                'matched_skills': similarity_result['skill_matching_details']['matched_skills'],
                'missing_skills': similarity_result['skill_matching_details']['missing_skills'],
                'additional_skills': similarity_result['skill_matching_details']['additional_skills'],
                'coverage_score': similarity_result['skill_matching_details']['coverage_score']
            },
            'certification_analysis': similarity_result['certification_analysis'],
            'experience_analysis': similarity_result['experience_analysis'],
            'key_insights': similarity_result['detailed_analysis']['key_insights'],
            'recommendations': similarity_result['recommendations'],
            'normalized_skills_data': resume_data['entities'].get('normalized_skills'),
            'normalized_certifications_data': resume_data['entities'].get('normalized_certifications')
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Enhanced evaluation failed: {str(e)}'}), 500


@bp.route('/skill-recommendations', methods=['POST'])
def get_skill_recommendations():
    """
    Get skill recommendations based on resume analysis and target role
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        target_role = data.get('target_role')
        
        if not resume_id:
            return jsonify({'error': 'resume_id is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, 'resumes')
        if not resume_path:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Parse resume with enhanced parsing
        resume_data = parse_resume_file(resume_path)
        
        if 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data["error"]}'}), 500
        
        # Initialize skill normalizer
        from app.utils.skill_normalizer import create_skill_normalizer
        normalizer = create_skill_normalizer()
        
        # Get current skills
        current_skills = resume_data['entities']['skills'].get('technical_skills', []) + \
                        resume_data['entities']['skills'].get('soft_skills', [])
        
        # Get skill recommendations
        recommendations = normalizer.get_skill_recommendations(current_skills, target_role)
        
        return jsonify({
            'resume_id': resume_id,
            'target_role': target_role,
            'current_skill_analysis': recommendations['current_skill_analysis'],
            'skill_gap_analysis': recommendations['skill_gap_analysis'],
            'recommended_skills': recommendations['recommended_skills'],
            'missing_categories': recommendations['missing_categories']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Skill recommendation failed: {str(e)}'}), 500

@bp.route('/evaluate-transformer', methods=['POST'])
def evaluate_resume_transformer():
    """Evaluate resume using enhanced transformer-based similarity analysis"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, 'resumes')
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Create enhanced similarity engine with transformers enabled
        similarity_engine = create_enhanced_similarity_engine(
            use_transformers=True,
            transformer_model=data.get('transformer_model', 'all-MiniLM-L6-v2')
        )
        
        # Calculate enhanced similarity
        similarity_result = similarity_engine.calculate_comprehensive_similarity(
            resume_data, job_description
        )
        
        # Get transformer-specific analysis
        resume_skills = resume_data.get('skills', [])
        job_skills = job_description.get('required_skills', []) + job_description.get('preferred_skills', [])
        
        enhanced_skill_analysis = similarity_engine.calculate_skill_similarity_enhanced(
            resume_skills, job_skills
        )
        
        return jsonify({
            'resume_id': resume_id,
            'transformer_enabled': True,
            'model_used': data.get('transformer_model', 'all-MiniLM-L6-v2'),
            'similarity_analysis': similarity_result,
            'enhanced_skill_analysis': enhanced_skill_analysis,
            'analysis_timestamp': similarity_result.get('analysis_timestamp')
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Transformer evaluation failed: {str(e)}'}), 500

@bp.route('/rank-candidates', methods=['POST'])
def rank_candidates():
    """Rank multiple candidates using transformer-based similarity"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        candidate_ids = data.get('candidate_ids', [])
        job_description = data.get('job_description', {})
        
        if not candidate_ids:
            return jsonify({'error': 'Candidate IDs are required'}), 400
        
        # Parse all candidate resumes
        candidates = []
        parsing_errors = []
        
        for candidate_id in candidate_ids:
            resume_path = get_file_path(candidate_id, 'resumes')
            if resume_path and os.path.exists(resume_path):
                resume_data = parse_resume_file(resume_path)
                if resume_data and 'error' not in resume_data:
                    resume_data['candidate_id'] = candidate_id
                    candidates.append(resume_data)
                else:
                    parsing_errors.append({
                        'candidate_id': candidate_id,
                        'error': resume_data.get('error', 'Failed to parse resume')
                    })
            else:
                parsing_errors.append({
                    'candidate_id': candidate_id,
                    'error': 'Resume file not found'
                })
        
        if not candidates:
            return jsonify({
                'error': 'No valid candidates found',
                'parsing_errors': parsing_errors
            }), 404
        
        # Create enhanced similarity engine
        similarity_engine = create_enhanced_similarity_engine(
            use_transformers=True,
            transformer_model=data.get('transformer_model', 'all-MiniLM-L6-v2')
        )
        
        # Rank candidates
        ranked_candidates = similarity_engine.rank_candidates(candidates, job_description)
        
        return jsonify({
            'total_candidates': len(ranked_candidates),
            'successful_parses': len(candidates),
            'parsing_errors': parsing_errors,
            'job_description': job_description,
            'ranked_candidates': ranked_candidates[:10],  # Top 10
            'transformer_model': data.get('transformer_model', 'all-MiniLM-L6-v2'),
            'ranking_method': 'transformer_enhanced'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Candidate ranking failed: {str(e)}'}), 500

@bp.route('/evaluate-advanced', methods=['POST'])
def evaluate_resume_advanced():
    """Advanced multi-component resume evaluation with confidence and explainability"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        include_explanations = data.get('include_explanations', True)
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, 'resumes')
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Perform advanced analysis
        analysis_result = analyze_resume_relevance_advanced(
            resume_data, 
            job_description, 
            include_explanations=include_explanations
        )
        
        # Get scoring summary
        summary = get_scoring_summary(analysis_result)
        
        return jsonify({
            'resume_id': resume_id,
            'analysis_type': 'advanced_multi_component',
            'summary': summary,
            'detailed_analysis': analysis_result,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Advanced evaluation failed: {str(e)}'}), 500

@bp.route('/score-breakdown', methods=['POST'])
def get_score_breakdown():
    """Get detailed breakdown of scoring components and evidence"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, 'resumes')
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Perform advanced analysis with full explanations
        analysis_result = analyze_resume_relevance_advanced(
            resume_data, 
            job_description, 
            include_explanations=True
        )
        
        # Extract detailed component breakdown
        component_details = []
        for comp in analysis_result.get('component_breakdown', []):
            component_details.append({
                'component_name': comp['name'],
                'score': comp['score'],
                'weight': comp['weight'],
                'weighted_contribution': comp['score'] * comp['weight'],
                'confidence': comp['confidence'],
                'evidence': comp['evidence'],
                'methodology': comp['methodology']
            })
        
        return jsonify({
            'resume_id': resume_id,
            'overall_score': analysis_result.get('overall_score', 0),
            'suitability_verdict': analysis_result.get('suitability_verdict', 'Unknown'),
            'confidence_analysis': {
                'confidence_level': analysis_result.get('confidence_level', 'Unknown'),
                'confidence_score': analysis_result.get('confidence_score', 0),
                'factors': "Confidence based on data completeness, score consistency, evidence strength, and methodology reliability"
            },
            'component_breakdown': component_details,
            'performance_insights': {
                'strengths': analysis_result.get('strengths', []),
                'weaknesses': analysis_result.get('weaknesses', []),
                'recommendations': analysis_result.get('recommendations', [])
            },
            'methodology_info': {
                'analysis_type': analysis_result.get('analysis_type', 'advanced'),
                'version': analysis_result.get('methodology_version', '2.0.0'),
                'processing_time': analysis_result.get('processing_time', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Score breakdown failed: {str(e)}'}), 500

@bp.route('/compare-candidates-advanced', methods=['POST'])
def compare_candidates_advanced():
    """Advanced comparison of multiple candidates with detailed scoring"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        candidate_ids = data.get('candidate_ids', [])
        job_description = data.get('job_description', {})
        include_explanations = data.get('include_explanations', False)
        
        if not candidate_ids or len(candidate_ids) < 2:
            return jsonify({'error': 'At least 2 candidate IDs are required'}), 400
        
        # Parse all candidate resumes
        candidates_data = []
        parsing_errors = []
        
        for candidate_id in candidate_ids:
            resume_path = get_file_path(candidate_id, "resumes")
            if resume_path and os.path.exists(resume_path):
                resume_data = parse_resume_file(resume_path)
                if resume_data and 'error' not in resume_data:
                    resume_data['candidate_id'] = candidate_id
                    candidates_data.append(resume_data)
                else:
                    parsing_errors.append({
                        'candidate_id': candidate_id,
                        'error': resume_data.get('error', 'Failed to parse resume')
                    })
            else:
                parsing_errors.append({
                    'candidate_id': candidate_id,
                    'error': 'Resume file not found'
                })
        
        if not candidates_data:
            return jsonify({
                'error': 'No valid candidates found',
                'parsing_errors': parsing_errors
            }), 404
        
        # Analyze all candidates
        candidate_analyses = []
        
        for candidate_data in candidates_data:
            analysis = analyze_resume_relevance_advanced(
                candidate_data, 
                job_description, 
                include_explanations=include_explanations
            )
            
            candidate_analyses.append({
                'candidate_id': candidate_data['candidate_id'],
                'analysis': analysis,
                'summary': get_scoring_summary(analysis)
            })
        
        # Sort by overall score
        candidate_analyses.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)
        
        # Generate comparison insights
        scores = [c['analysis']['overall_score'] for c in candidate_analyses]
        score_range = max(scores) - min(scores) if scores else 0
        
        comparison_insights = []
        if score_range > 20:
            comparison_insights.append(f"Wide range of candidate quality (score range: {score_range:.1f} points)")
        elif score_range > 10:
            comparison_insights.append(f"Moderate variation in candidate quality (score range: {score_range:.1f} points)")
        else:
            comparison_insights.append(f"Similar candidate quality levels (score range: {score_range:.1f} points)")
        
        # Find best and worst performing areas across candidates
        all_components = {}
        for c in candidate_analyses:
            for comp in c['analysis'].get('component_breakdown', []):
                comp_name = comp['name']
                if comp_name not in all_components:
                    all_components[comp_name] = []
                all_components[comp_name].append(comp['score'])
        
        component_analysis = {}
        for comp_name, scores in all_components.items():
            component_analysis[comp_name] = {
                'average_score': sum(scores) / len(scores),
                'score_range': max(scores) - min(scores),
                'best_performer': max(scores),
                'worst_performer': min(scores)
            }
        
        return jsonify({
            'comparison_summary': {
                'total_candidates': len(candidate_analyses),
                'successful_analyses': len(candidate_analyses),
                'parsing_errors': len(parsing_errors),
                'score_range': score_range,
                'average_score': sum(scores) / len(scores) if scores else 0
            },
            'ranked_candidates': candidate_analyses,
            'component_comparison': component_analysis,
            'insights': comparison_insights,
            'parsing_errors': parsing_errors,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Advanced candidate comparison failed: {str(e)}'}), 500


# =============================================================================
# FEEDBACK GENERATION ENDPOINTS
# =============================================================================

@bp.route('/generate-feedback', methods=['POST'])
def generate_candidate_feedback_endpoint():
    """Generate comprehensive personalized feedback for a candidate"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        candidate_name = data.get('candidate_name')
        feedback_type = data.get('feedback_type', 'comprehensive')
        feedback_tone = data.get('feedback_tone', 'professional')
        llm_provider = data.get('llm_provider', 'mock')
        include_resources = data.get('include_resources', True)
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, "resumes")
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Generate feedback
        feedback = generate_personalized_feedback(
            resume_data=resume_data,
            job_description=job_description,
            candidate_name=candidate_name,
            feedback_type=feedback_type,
            feedback_tone=feedback_tone,
            llm_provider=llm_provider,
            include_resources=include_resources
        )
        
        return jsonify({
            'resume_id': resume_id,
            'candidate_name': candidate_name,
            'feedback_type': feedback_type,
            'feedback_tone': feedback_tone,
            'llm_provider': llm_provider,
            'feedback': feedback,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Feedback generation failed: {str(e)}'}), 500


@bp.route('/generate-skill-feedback', methods=['POST'])
def generate_skill_feedback_endpoint():
    """Generate skill-focused feedback for a candidate"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        candidate_name = data.get('candidate_name')
        llm_provider = data.get('llm_provider', 'mock')
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, "resumes")
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Generate skill-focused feedback
        feedback = generate_skill_focused_feedback(
            resume_data=resume_data,
            job_description=job_description,
            candidate_name=candidate_name,
            llm_provider=llm_provider
        )
        
        return jsonify({
            'resume_id': resume_id,
            'candidate_name': candidate_name,
            'feedback_type': 'skill_focused',
            'feedback': feedback,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Skill feedback generation failed: {str(e)}'}), 500


@bp.route('/generate-experience-feedback', methods=['POST'])
def generate_experience_feedback_endpoint():
    """Generate experience-focused feedback for a candidate"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        candidate_name = data.get('candidate_name')
        llm_provider = data.get('llm_provider', 'mock')
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, "resumes")
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Generate experience-focused feedback
        feedback = generate_experience_focused_feedback(
            resume_data=resume_data,
            job_description=job_description,
            candidate_name=candidate_name,
            llm_provider=llm_provider
        )
        
        return jsonify({
            'resume_id': resume_id,
            'candidate_name': candidate_name,
            'feedback_type': 'experience_focused',
            'feedback': feedback,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Experience feedback generation failed: {str(e)}'}), 500


@bp.route('/generate-certification-feedback', methods=['POST'])
def generate_certification_feedback_endpoint():
    """Generate certification and training focused feedback for a candidate"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resume_id')
        job_description = data.get('job_description', {})
        candidate_name = data.get('candidate_name')
        llm_provider = data.get('llm_provider', 'mock')
        
        if not resume_id:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        # Get resume file path
        resume_path = get_file_path(resume_id, "resumes")
        if not resume_path or not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Parse resume
        resume_data = parse_resume_file(resume_path)
        if not resume_data or 'error' in resume_data:
            return jsonify({'error': f'Resume parsing failed: {resume_data.get("error", "Unknown error")}'}), 500
        
        # Generate certification-focused feedback
        feedback = generate_certification_focused_feedback(
            resume_data=resume_data,
            job_description=job_description,
            candidate_name=candidate_name,
            llm_provider=llm_provider
        )
        
        return jsonify({
            'resume_id': resume_id,
            'candidate_name': candidate_name,
            'feedback_type': 'certification_focused',
            'feedback': feedback,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Certification feedback generation failed: {str(e)}'}), 500


@bp.route('/batch-generate-feedback', methods=['POST'])
def batch_generate_feedback_endpoint():
    """Generate feedback for multiple candidates in batch"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        candidate_ids = data.get('candidate_ids', [])
        job_description = data.get('job_description', {})
        feedback_type = data.get('feedback_type', 'comprehensive')
        llm_provider = data.get('llm_provider', 'mock')
        
        if not candidate_ids:
            return jsonify({'error': 'Candidate IDs are required'}), 400
        
        # Prepare candidates data
        candidates_data = []
        parsing_errors = []
        
        for candidate_id in candidate_ids:
            resume_path = get_file_path(candidate_id, "resumes")
            if resume_path and os.path.exists(resume_path):
                resume_data = parse_resume_file(resume_path)
                if resume_data and 'error' not in resume_data:
                    candidates_data.append({
                        'candidate_id': candidate_id,
                        'candidate_name': resume_data.get('name', f'Candidate {candidate_id}'),
                        'resume_data': resume_data
                    })
                else:
                    parsing_errors.append({
                        'candidate_id': candidate_id,
                        'error': resume_data.get('error', 'Failed to parse resume')
                    })
            else:
                parsing_errors.append({
                    'candidate_id': candidate_id,
                    'error': 'Resume file not found'
                })
        
        if not candidates_data:
            return jsonify({
                'error': 'No valid candidates found',
                'parsing_errors': parsing_errors
            }), 404
        
        # Generate batch feedback
        feedback_results = batch_generate_candidate_feedback(
            candidates_data=candidates_data,
            job_description=job_description,
            feedback_type=feedback_type,
            llm_provider=llm_provider
        )
        
        return jsonify({
            'total_candidates': len(candidate_ids),
            'successful_analyses': len([r for r in feedback_results if r['status'] == 'success']),
            'failed_analyses': len([r for r in feedback_results if r['status'] == 'failed']),
            'feedback_type': feedback_type,
            'llm_provider': llm_provider,
            'results': feedback_results,
            'parsing_errors': parsing_errors,
            'job_description': job_description
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Batch feedback generation failed: {str(e)}'}), 500


@bp.route('/compare-feedback', methods=['POST'])
def compare_candidate_feedback_endpoint():
    """Generate comparative feedback analysis for multiple candidates"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        candidate_ids = data.get('candidate_ids', [])
        job_description = data.get('job_description', {})
        llm_provider = data.get('llm_provider', 'mock')
        
        if not candidate_ids or len(candidate_ids) < 2:
            return jsonify({'error': 'At least 2 candidate IDs are required for comparison'}), 400
        
        # Prepare candidates data
        candidates_data = []
        parsing_errors = []
        
        for candidate_id in candidate_ids:
            resume_path = get_file_path(candidate_id, "resumes")
            if resume_path and os.path.exists(resume_path):
                resume_data = parse_resume_file(resume_path)
                if resume_data and 'error' not in resume_data:
                    candidates_data.append({
                        'candidate_id': candidate_id,
                        'candidate_name': resume_data.get('name', f'Candidate {candidate_id}'),
                        'resume_data': resume_data
                    })
                else:
                    parsing_errors.append({
                        'candidate_id': candidate_id,
                        'error': resume_data.get('error', 'Failed to parse resume')
                    })
            else:
                parsing_errors.append({
                    'candidate_id': candidate_id,
                    'error': 'Resume file not found'
                })
        
        if len(candidates_data) < 2:
            return jsonify({
                'error': 'At least 2 valid candidates required for comparison',
                'parsing_errors': parsing_errors
            }), 400
        
        # Generate comparative feedback
        comparison_results = compare_candidate_feedback(
            candidates_data=candidates_data,
            job_description=job_description,
            llm_provider=llm_provider
        )
        
        return jsonify({
            'comparison_type': 'candidate_feedback_analysis',
            'total_candidates_requested': len(candidate_ids),
            'candidates_analyzed': len(candidates_data),
            'llm_provider': llm_provider,
            'comparison_results': comparison_results,
            'parsing_errors': parsing_errors
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Comparative feedback generation failed: {str(e)}'}), 500


@bp.route('/feedback-options', methods=['GET'])
def get_feedback_options():
    """Get available feedback configuration options"""
    try:
        return jsonify({
            'feedback_types': [
                {
                    'name': 'comprehensive',
                    'description': 'Complete analysis covering all aspects of candidacy',
                    'suitable_for': 'General evaluation and detailed assessment'
                },
                {
                    'name': 'skill_focused',
                    'description': 'Focused analysis of technical and professional skills',
                    'suitable_for': 'Technical roles and skill development planning'
                },
                {
                    'name': 'experience_focused',
                    'description': 'Analysis of work experience and career progression',
                    'suitable_for': 'Experience requirements and career advancement'
                },
                {
                    'name': 'certification_focused',
                    'description': 'Analysis of certifications and training requirements',
                    'suitable_for': 'Roles requiring specific credentials or certifications'
                }
            ],
            'feedback_tones': [
                {
                    'name': 'professional',
                    'description': 'Formal, direct, and business-focused tone'
                },
                {
                    'name': 'encouraging',
                    'description': 'Supportive, positive, and motivational tone'
                },
                {
                    'name': 'constructive',
                    'description': 'Balanced, honest, and solution-oriented tone'
                },
                {
                    'name': 'detailed',
                    'description': 'Thorough, analytical, and comprehensive tone'
                },
                {
                    'name': 'concise',
                    'description': 'Brief, focused, and to-the-point tone'
                }
            ],
            'llm_providers': [
                {
                    'name': 'mock',
                    'description': 'Mock provider for testing and development',
                    'cost': 'Free',
                    'quality': 'Basic'
                },
                {
                    'name': 'openai',
                    'description': 'OpenAI GPT models (requires API key)',
                    'cost': 'Paid',
                    'quality': 'High'
                },
                {
                    'name': 'anthropic',
                    'description': 'Anthropic Claude models (requires API key)',
                    'cost': 'Paid',
                    'quality': 'High'
                },
                {
                    'name': 'local',
                    'description': 'Local LLM deployment (requires setup)',
                    'cost': 'Infrastructure',
                    'quality': 'Variable'
                }
            ],
            'configuration_tips': [
                'Use "mock" provider for testing without API costs',
                'Set environment variables OPENAI_API_KEY or ANTHROPIC_API_KEY for paid providers',
                'Choose "comprehensive" for general feedback, specialized types for focused analysis',
                'Adjust tone based on candidate experience level and company culture'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get feedback options: {str(e)}'}), 500


@bp.route('/feedback-health', methods=['GET'])
def get_feedback_system_health():
    """Get health status of the feedback generation system"""
    try:
        # Import configuration manager
        from ..utils.feedback_config import config_manager, get_system_health
        
        health_status = get_system_health()
        providers_info = config_manager.get_available_providers()
        recommended_provider = config_manager.get_recommended_provider()
        
        return jsonify({
            'system_health': health_status,
            'providers': providers_info,
            'recommended_provider': recommended_provider,
            'configuration': {
                'default_feedback_type': config_manager.feedback_config.default_feedback_type,
                'default_tone': config_manager.feedback_config.default_tone,
                'fallback_enabled': config_manager.feedback_config.fallback_enabled,
                'caching_enabled': config_manager.feedback_config.enable_caching
            },
            'api_endpoints': [
                '/api/generate-feedback',
                '/api/generate-skill-feedback',
                '/api/generate-experience-feedback',
                '/api/generate-certification-feedback',
                '/api/batch-generate-feedback',
                '/api/compare-feedback',
                '/api/feedback-options',
                '/api/feedback-health'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get system health: {str(e)}'}), 500


@bp.route('/feedback-test', methods=['POST'])
def test_feedback_generation():
    """Test feedback generation with sample data"""
    try:
        data = request.json or {}
        test_provider = data.get('provider', 'mock')
        feedback_type = data.get('feedback_type', 'comprehensive')
        
        # Sample test data
        sample_resume = {
            'name': 'Test Candidate',
            'skills': ['Python', 'SQL', 'Data Analysis'],
            'work_experience': [
                {
                    'title': 'Data Analyst',
                    'company': 'Tech Corp',
                    'duration': '2 years',
                    'responsibilities': ['Analyzed data', 'Created reports']
                }
            ],
            'education': [
                {
                    'degree': 'BS Computer Science',
                    'institution': 'University',
                    'year': '2020'
                }
            ],
            'certifications': []
        }
        
        sample_job = {
            'title': 'Senior Data Scientist',
            'company_name': 'Innovation Inc',
            'required_skills': ['Python', 'Machine Learning', 'SQL', 'Statistics'],
            'preferred_skills': ['Deep Learning', 'Cloud Computing'],
            'experience_requirements': '3+ years in data science',
            'certifications': ['AWS Certified Solutions Architect']
        }
        
        # Generate test feedback
        from ..utils.relevance_analyzer import generate_personalized_feedback
        
        start_time = time.time()
        feedback = generate_personalized_feedback(
            resume_data=sample_resume,
            job_description=sample_job,
            candidate_name='Test Candidate',
            feedback_type=feedback_type,
            llm_provider=test_provider
        )
        processing_time = time.time() - start_time
        
        return jsonify({
            'test_status': 'success',
            'provider_used': test_provider,
            'feedback_type': feedback_type,
            'processing_time': processing_time,
            'sample_data': {
                'resume': sample_resume,
                'job_description': sample_job
            },
            'generated_feedback': feedback,
            'metadata': {
                'test_timestamp': datetime.now().isoformat(),
                'system_info': 'Automated Resume Relevance System - Feedback Test'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'test_status': 'failed',
            'error': str(e),
            'recommendation': 'Check system health and provider configuration'
        }), 500

@bp.route('/evaluate/dual-upload', methods=['POST'])
def evaluate_dual_upload():
    """Enhanced endpoint for simultaneous resume and job description analysis"""
    start_time = time.time()
    
    try:
        data = request.json
        log_request('evaluate-dual-upload', data)
        
        if not data:
            logger.warning("No data provided in dual upload evaluate request")
            return jsonify({'error': 'No data provided'}), 400
        
        resume_ids = data.get('resume_ids', [])
        job_description_ids = data.get('job_description_ids', [])
        analysis_options = data.get('options', {})
        
        # Support single file or multiple files
        if isinstance(resume_ids, str):
            resume_ids = [resume_ids]
        if isinstance(job_description_ids, str):
            job_description_ids = [job_description_ids]
        
        if not resume_ids or not job_description_ids:
            logger.warning(f"Missing required IDs: resume_ids={resume_ids}, job_description_ids={job_description_ids}")
            return jsonify({'error': 'Both resume_ids and job_description_ids are required'}), 400
        
        # Validate all files exist
        all_validation_errors = []
        for resume_id in resume_ids:
            all_validation_errors.extend(validate_file_ids(resume_id=resume_id))
        for job_desc_id in job_description_ids:
            all_validation_errors.extend(validate_file_ids(job_description_id=job_desc_id))
        
        if all_validation_errors:
            logger.warning(f"File validation errors: {all_validation_errors}")
            return jsonify({'error': '; '.join(all_validation_errors)}), 404
        
        # Process all combinations or specific pairs
        results = []
        processing_matrix = []
        
        # Create processing matrix
        if len(resume_ids) == 1 and len(job_description_ids) == 1:
            # Single pair analysis
            processing_matrix = [(resume_ids[0], job_description_ids[0])]
        elif analysis_options.get('cross_analysis', True):
            # Cross analysis - all resumes against all job descriptions
            for resume_id in resume_ids:
                for job_desc_id in job_description_ids:
                    processing_matrix.append((resume_id, job_desc_id))
        else:
            # Paired analysis - match by index
            for i, resume_id in enumerate(resume_ids):
                if i < len(job_description_ids):
                    processing_matrix.append((resume_id, job_description_ids[i]))
        
        logger.info(f"Processing {len(processing_matrix)} resume-job combinations")
        
        # Process each combination
        for resume_id, job_desc_id in processing_matrix:
            try:
                # Get file paths
                resume_path = get_file_path(resume_id, 'resumes')
                job_desc_path = get_file_path(job_desc_id, 'job_descriptions')
                
                # Validate paths
                if not resume_path or not job_desc_path:
                    logger.error(f"File paths not found for {resume_id}-{job_desc_id}")
                    results.append({
                        'resume_id': resume_id,
                        'job_description_id': job_desc_id,
                        'error': 'File paths not found',
                        'status': 'failed'
                    })
                    continue
                
                logger.info(f"Processing combination: resume={resume_id}, job_desc={job_desc_id}")
                
                # Extract text from files
                resume_text = extract_text_from_file(resume_path, enhanced=True)
                job_desc_text = extract_text_from_file(job_desc_path, enhanced=True)
                
                if not resume_text or not job_desc_text:
                    logger.error(f"Text extraction failed for {resume_id}-{job_desc_id}")
                    results.append({
                        'resume_id': resume_id,
                        'job_description_id': job_desc_id,
                        'error': 'Failed to extract text from files',
                        'status': 'failed'
                    })
                    continue
                
                # Parse resume for enhanced analysis
                parsed_resume = parse_resume_file(resume_path) if resume_path else None
                
                # Prepare resume data for analysis
                resume_data = {
                    'text': resume_text,
                    'parsed_data': parsed_resume or {}
                }
                
                # Use advanced analysis
                analysis_result = analyze_resume_relevance_advanced(
                    resume_data=resume_data,
                    job_description=job_desc_text,
                    include_explanations=analysis_options.get('detailed_feedback', True)
                )
                
                # Enhanced result with additional metadata
                enhanced_result = {
                    'resume_id': resume_id,
                    'job_description_id': job_desc_id,
                    'status': 'success',
                    'analysis': analysis_result,
                    'metadata': {
                        'resume_filename': os.path.basename(resume_path) if resume_path else 'unknown',
                        'job_desc_filename': os.path.basename(job_desc_path) if job_desc_path else 'unknown',
                        'processing_time': time.time() - start_time,
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                }
                
                # Add personalized feedback if requested
                if analysis_options.get('include_feedback', True):
                    try:
                        feedback = generate_personalized_feedback(
                            analysis_result, 
                            resume_text, 
                            job_desc_text,
                            feedback_type=analysis_options.get('feedback_type', 'comprehensive')
                        )
                        enhanced_result['feedback'] = feedback
                    except Exception as feedback_error:
                        logger.warning(f"Feedback generation failed: {feedback_error}")
                        enhanced_result['feedback_error'] = str(feedback_error)
                
                results.append(enhanced_result)
                logger.info(f"Successfully processed {resume_id}-{job_desc_id}")
                
            except Exception as combination_error:
                logger.error(f"Error processing {resume_id}-{job_desc_id}: {combination_error}")
                results.append({
                    'resume_id': resume_id,
                    'job_description_id': job_desc_id,
                    'error': str(combination_error),
                    'status': 'failed'
                })
        
        # Generate summary statistics
        successful_analyses = [r for r in results if r.get('status') == 'success']
        failed_analyses = [r for r in results if r.get('status') == 'failed']
        
        summary = {
            'total_combinations': len(processing_matrix),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(failed_analyses),
            'success_rate': len(successful_analyses) / len(processing_matrix) * 100 if processing_matrix else 0,
            'total_processing_time': time.time() - start_time
        }
        
        # Add comparative analysis for multiple results
        if len(successful_analyses) > 1 and analysis_options.get('include_comparison', True):
            try:
                comparison_data = {
                    'highest_score': max(successful_analyses, key=lambda x: x['analysis']['overall_score']),
                    'lowest_score': min(successful_analyses, key=lambda x: x['analysis']['overall_score']),
                    'average_score': sum(r['analysis']['overall_score'] for r in successful_analyses) / len(successful_analyses),
                    'score_distribution': {
                        'high': len([r for r in successful_analyses if r['analysis']['overall_score'] >= 0.8]),
                        'medium': len([r for r in successful_analyses if 0.5 <= r['analysis']['overall_score'] < 0.8]),
                        'low': len([r for r in successful_analyses if r['analysis']['overall_score'] < 0.5])
                    }
                }
                summary['comparison'] = comparison_data
            except Exception as comp_error:
                logger.warning(f"Comparison analysis failed: {comp_error}")
        
        # Final response
        response_data = {
            'message': 'Dual upload analysis completed',
            'summary': summary,
            'results': results,
            'processing_options': analysis_options,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Dual upload analysis completed: {summary['successful_analyses']}/{summary['total_combinations']} successful")
        return jsonify(response_data), 200
        
    except Exception as e:
        total_time = time.time() - start_time
        return handle_api_error(e, f'evaluate-dual-upload (after {total_time:.2f}s)')

@bp.route('/evaluate/batch-feedback', methods=['POST'])  
def generate_batch_feedback():
    """Generate feedback for multiple resume-job combinations"""
    start_time = time.time()
    
    try:
        data = request.json
        log_request('batch-feedback', data)
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        combinations = data.get('combinations', [])
        feedback_options = data.get('options', {})
        
        if not combinations:
            return jsonify({'error': 'No combinations provided'}), 400
        
        feedback_results = []
        
        for combo in combinations:
            try:
                resume_id = combo.get('resume_id')
                job_desc_id = combo.get('job_description_id')
                existing_analysis = combo.get('analysis')
                
                if not all([resume_id, job_desc_id]):
                    feedback_results.append({
                        'resume_id': resume_id,
                        'job_description_id': job_desc_id,
                        'error': 'Missing resume_id or job_description_id',
                        'status': 'failed'
                    })
                    continue
                
                # Get file paths and text
                resume_path = get_file_path(resume_id, 'resumes')
                job_desc_path = get_file_path(job_desc_id, 'job_descriptions')
                
                if not resume_path or not job_desc_path:
                    feedback_results.append({
                        'resume_id': resume_id,
                        'job_description_id': job_desc_id,
                        'error': 'File not found',
                        'status': 'failed'
                    })
                    continue
                
                resume_text = extract_text_from_file(resume_path, enhanced=True)
                job_desc_text = extract_text_from_file(job_desc_path, enhanced=True)
                
                # Generate different types of feedback
                feedback_types = feedback_options.get('feedback_types', ['comprehensive'])
                all_feedback = {}
                
                for feedback_type in feedback_types:
                    if feedback_type == 'skill_focused':
                        feedback = generate_skill_focused_feedback(existing_analysis, resume_text, job_desc_text)
                    elif feedback_type == 'experience_focused':
                        feedback = generate_experience_focused_feedback(existing_analysis, resume_text, job_desc_text)
                    elif feedback_type == 'certification_focused':
                        feedback = generate_certification_focused_feedback(existing_analysis, resume_text, job_desc_text)
                    else:
                        feedback = generate_personalized_feedback(existing_analysis, resume_text, job_desc_text)
                    
                    all_feedback[feedback_type] = feedback
                
                feedback_results.append({
                    'resume_id': resume_id,
                    'job_description_id': job_desc_id,
                    'feedback': all_feedback,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as combo_error:
                logger.error(f"Error generating feedback for {resume_id}-{job_desc_id}: {combo_error}")
                feedback_results.append({
                    'resume_id': resume_id,
                    'job_description_id': job_desc_id,
                    'error': str(combo_error),
                    'status': 'failed'
                })
        
        # Summary
        successful_feedback = len([r for r in feedback_results if r.get('status') == 'success'])
        
        response_data = {
            'message': 'Batch feedback generation completed',
            'summary': {
                'total_combinations': len(combinations),
                'successful_generations': successful_feedback,
                'failed_generations': len(combinations) - successful_feedback,
                'processing_time': time.time() - start_time
            },
            'results': feedback_results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Batch feedback completed: {successful_feedback}/{len(combinations)} successful")
        return jsonify(response_data), 200
        
    except Exception as e:
        return handle_api_error(e, 'batch-feedback')
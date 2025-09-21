from flask import Blueprint, request, jsonify, current_app
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.file_handler import allowed_file, save_file, get_file_type

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('upload', __name__, url_prefix='/api')

def log_upload_request(endpoint_name, file_info=None, text_info=None):
    """Log upload requests for debugging"""
    try:
        if file_info:
            logger.info(f"File upload to {endpoint_name}: {file_info}")
        elif text_info:
            logger.info(f"Text upload to {endpoint_name}: {text_info}")
        else:
            logger.info(f"Upload request to {endpoint_name}")
    except Exception as e:
        logger.error(f"Error logging upload request: {e}")

def handle_upload_error(error, endpoint_name, status_code=500):
    """Centralized error handling for upload endpoints"""
    error_msg = str(error)
    logger.error(f"Upload error in {endpoint_name}: {error_msg}")
    return jsonify({
        'error': f'Upload failed: {error_msg}',
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint_name
    }), status_code

def validate_file_upload(file, allowed_extensions):
    """Validate uploaded file"""
    errors = []
    
    if not file:
        errors.append("No file provided")
    elif file.filename == '' or file.filename is None:
        errors.append("No file selected")
    elif not allowed_file(file.filename, allowed_extensions):
        errors.append(f"Invalid file type. Allowed types: {', '.join(allowed_extensions).upper()}")
    elif file.content_length and file.content_length > 50 * 1024 * 1024:  # 50MB limit
        errors.append("File size exceeds 50MB limit")
    
    return errors

@bp.route('/upload/resume', methods=['POST'])
def upload_resume():
    """Upload a resume file (PDF, DOC, DOCX, TXT)"""
    try:
        if 'file' not in request.files:
            logger.warning("Resume upload attempted without file")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_info = {
            'filename': file.filename,
            'content_type': file.content_type,
            'size': file.content_length
        }
        log_upload_request('resume', file_info=file_info)
        
        # Validate file
        allowed_extensions = ['pdf', 'doc', 'docx', 'txt']
        validation_errors = validate_file_upload(file, allowed_extensions)
        if validation_errors:
            logger.warning(f"Resume upload validation failed: {validation_errors}")
            return jsonify({'error': '; '.join(validation_errors)}), 400
        
        # Check upload folder exists
        if not current_app.config.get('UPLOAD_FOLDER'):
            logger.error("UPLOAD_FOLDER not configured")
            return jsonify({'error': 'Server configuration error'}), 500
        
        # Save file
        filename = save_file(file, 'resumes', current_app.config['UPLOAD_FOLDER'])
        
        if not filename:
            logger.error("File save operation returned no filename")
            return jsonify({'error': 'Failed to save file'}), 500
        
        file_id = filename.split('.')[0]  # Use filename without extension as ID
        
        response_data = {
            'message': 'Resume uploaded successfully',
            'filename': filename,
            'file_type': get_file_type(filename),
            'file_id': file_id,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Resume uploaded successfully: {filename} (ID: {file_id})")
        return jsonify(response_data), 200
        
    except Exception as e:
        return handle_upload_error(e, 'resume')

@bp.route('/upload/job-description', methods=['POST'])
def upload_job_description():
    """Upload a job description file (PDF, DOC, DOCX, TXT) or accept text input"""
    try:
        # Check if it's a file upload
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            
            file_info = {
                'filename': file.filename,
                'content_type': file.content_type,
                'size': file.content_length
            }
            log_upload_request('job-description', file_info=file_info)
            
            # Validate file
            allowed_extensions = ['pdf', 'doc', 'docx', 'txt']
            validation_errors = validate_file_upload(file, allowed_extensions)
            if validation_errors:
                logger.warning(f"Job description file upload validation failed: {validation_errors}")
                return jsonify({'error': '; '.join(validation_errors)}), 400
            
            # Check upload folder exists
            if not current_app.config.get('UPLOAD_FOLDER'):
                logger.error("UPLOAD_FOLDER not configured")
                return jsonify({'error': 'Server configuration error'}), 500
            
            filename = save_file(file, 'job_descriptions', current_app.config['UPLOAD_FOLDER'])
            
            if not filename:
                logger.error("Job description file save operation returned no filename")
                return jsonify({'error': 'Failed to save file'}), 500
            
            file_id = filename.split('.')[0]
            
            response_data = {
                'message': 'Job description uploaded successfully',
                'filename': filename,
                'file_type': get_file_type(filename),
                'file_id': file_id,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Job description file uploaded successfully: {filename} (ID: {file_id})")
            return jsonify(response_data), 200
        
        # Check if it's text input
        elif request.is_json and request.json and 'text' in request.json:
            text_content = request.json['text']
            
            text_info = {
                'text_length': len(text_content) if text_content else 0,
                'is_empty': not text_content or not text_content.strip()
            }
            log_upload_request('job-description', text_info=text_info)
            
            if not text_content or not text_content.strip():
                logger.warning("Empty job description text provided")
                return jsonify({'error': 'Job description text cannot be empty'}), 400
            
            if len(text_content.strip()) < 50:
                logger.warning(f"Job description text too short: {len(text_content)} chars")
                return jsonify({'error': 'Job description text must be at least 50 characters'}), 400
            
            if len(text_content) > 100000:  # 100KB limit for text
                logger.warning(f"Job description text too long: {len(text_content)} chars")
                return jsonify({'error': 'Job description text exceeds 100KB limit'}), 400
            
            # Check upload folder exists
            if not current_app.config.get('UPLOAD_FOLDER'):
                logger.error("UPLOAD_FOLDER not configured")
                return jsonify({'error': 'Server configuration error'}), 500
            
            # Save text as a file
            filename = save_file(text_content, 'job_descriptions', current_app.config['UPLOAD_FOLDER'], is_text=True)
            
            if not filename:
                logger.error("Job description text save operation returned no filename")
                return jsonify({'error': 'Failed to save text'}), 500
            
            file_id = filename.split('.')[0]
            
            response_data = {
                'message': 'Job description saved successfully',
                'filename': filename,
                'file_type': 'txt',
                'file_id': file_id,
                'text_length': len(text_content),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Job description text saved successfully: {filename} (ID: {file_id}, length: {len(text_content)} chars)")
            return jsonify(response_data), 200
        
        else:
            logger.warning("Job description upload attempted without file or text")
            return jsonify({'error': 'No file or text provided'}), 400
            
    except Exception as e:
        return handle_upload_error(e, 'job-description')

@bp.route('/files', methods=['GET'])
def list_files():
    """List all uploaded files"""
    try:
        logger.info("Listing all uploaded files")
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            logger.error("UPLOAD_FOLDER not configured")
            return jsonify({'error': 'Server configuration error'}), 500
        
        files = {
            'resumes': [],
            'job_descriptions': []
        }
        
        # List resumes
        try:
            resumes_path = os.path.join(upload_folder, 'resumes')
            if os.path.exists(resumes_path):
                for filename in os.listdir(resumes_path):
                    if filename.startswith('.'):  # Skip hidden files
                        continue
                    
                    file_path = os.path.join(resumes_path, filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        files['resumes'].append({
                            'filename': filename,
                            'file_id': filename.split('.')[0],
                            'file_type': get_file_type(filename),
                            'size': file_stats.st_size,
                            'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                        })
                logger.info(f"Found {len(files['resumes'])} resume files")
            else:
                logger.warning(f"Resumes directory does not exist: {resumes_path}")
        except Exception as e:
            logger.error(f"Error listing resumes: {e}")
            files['resumes_error'] = str(e)
        
        # List job descriptions
        try:
            job_desc_path = os.path.join(upload_folder, 'job_descriptions')
            if os.path.exists(job_desc_path):
                for filename in os.listdir(job_desc_path):
                    if filename.startswith('.'):  # Skip hidden files
                        continue
                    
                    file_path = os.path.join(job_desc_path, filename)
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        files['job_descriptions'].append({
                            'filename': filename,
                            'file_id': filename.split('.')[0],
                            'file_type': get_file_type(filename),
                            'size': file_stats.st_size,
                            'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                        })
                logger.info(f"Found {len(files['job_descriptions'])} job description files")
            else:
                logger.warning(f"Job descriptions directory does not exist: {job_desc_path}")
        except Exception as e:
            logger.error(f"Error listing job descriptions: {e}")
            files['job_descriptions_error'] = str(e)
        
        # Add summary information
        files['summary'] = {
            'total_resumes': len(files['resumes']),
            'total_job_descriptions': len(files['job_descriptions']),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"File listing completed: {files['summary']['total_resumes']} resumes, {files['summary']['total_job_descriptions']} job descriptions")
        return jsonify(files), 200
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({
            'error': f'Failed to list files: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/upload/dual', methods=['POST'])
def upload_dual_files():
    """Enhanced endpoint for simultaneous resume and job description uploads"""
    try:
        logger.info("Dual upload request received")
        
        # Check upload folder exists
        if not current_app.config.get('UPLOAD_FOLDER'):
            logger.error("UPLOAD_FOLDER not configured")
            return jsonify({'error': 'Server configuration error'}), 500
        
        uploaded_files = {
            'resumes': [],
            'job_descriptions': [],
            'errors': []
        }
        
        # Process resume files
        if 'resume_files' in request.files:
            resume_files = request.files.getlist('resume_files')
            logger.info(f"Processing {len(resume_files)} resume files")
            
            for file in resume_files:
                try:
                    if file.filename == '':
                        continue
                        
                    # Validate resume file
                    allowed_extensions = ['pdf', 'doc', 'docx', 'txt']
                    validation_errors = validate_file_upload(file, allowed_extensions)
                    if validation_errors:
                        uploaded_files['errors'].extend([f"Resume {file.filename}: {error}" for error in validation_errors])
                        continue
                    
                    # Save resume file
                    filename = save_file(file, 'resumes', current_app.config['UPLOAD_FOLDER'])
                    if filename:
                        file_id = filename.split('.')[0]
                        uploaded_files['resumes'].append({
                            'filename': filename,
                            'file_id': file_id,
                            'file_type': get_file_type(filename),
                            'original_name': file.filename,
                            'size': file.content_length,
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.info(f"Resume uploaded successfully: {filename}")
                    else:
                        uploaded_files['errors'].append(f"Failed to save resume: {file.filename}")
                        
                except Exception as file_error:
                    uploaded_files['errors'].append(f"Resume upload error ({file.filename}): {str(file_error)}")
                    logger.error(f"Error uploading resume {file.filename}: {file_error}")
        
        # Process job description files
        if 'job_description_files' in request.files:
            job_desc_files = request.files.getlist('job_description_files')
            logger.info(f"Processing {len(job_desc_files)} job description files")
            
            for file in job_desc_files:
                try:
                    if file.filename == '':
                        continue
                        
                    # Validate job description file
                    allowed_extensions = ['pdf', 'doc', 'docx', 'txt']
                    validation_errors = validate_file_upload(file, allowed_extensions)
                    if validation_errors:
                        uploaded_files['errors'].extend([f"Job Description {file.filename}: {error}" for error in validation_errors])
                        continue
                    
                    # Save job description file
                    filename = save_file(file, 'job_descriptions', current_app.config['UPLOAD_FOLDER'])
                    if filename:
                        file_id = filename.split('.')[0]
                        uploaded_files['job_descriptions'].append({
                            'filename': filename,
                            'file_id': file_id,
                            'file_type': get_file_type(filename),
                            'original_name': file.filename,
                            'size': file.content_length,
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.info(f"Job description uploaded successfully: {filename}")
                    else:
                        uploaded_files['errors'].append(f"Failed to save job description: {file.filename}")
                        
                except Exception as file_error:
                    uploaded_files['errors'].append(f"Job description upload error ({file.filename}): {str(file_error)}")
                    logger.error(f"Error uploading job description {file.filename}: {file_error}")
        
        # Process job description text inputs
        if request.form:
            job_desc_texts = request.form.getlist('job_description_texts')
            for i, text_content in enumerate(job_desc_texts):
                try:
                    if not text_content or not text_content.strip():
                        continue
                    
                    if len(text_content.strip()) < 50:
                        uploaded_files['errors'].append(f"Job description text {i+1} too short (minimum 50 characters)")
                        continue
                    
                    if len(text_content) > 100000:
                        uploaded_files['errors'].append(f"Job description text {i+1} too long (maximum 100KB)")
                        continue
                    
                    # Save text as file
                    filename = save_file(text_content, 'job_descriptions', current_app.config['UPLOAD_FOLDER'], is_text=True)
                    if filename:
                        file_id = filename.split('.')[0]
                        uploaded_files['job_descriptions'].append({
                            'filename': filename,
                            'file_id': file_id,
                            'file_type': 'txt',
                            'original_name': f'job_description_text_{i+1}.txt',
                            'size': len(text_content),
                            'text_length': len(text_content),
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.info(f"Job description text {i+1} saved successfully: {filename}")
                    else:
                        uploaded_files['errors'].append(f"Failed to save job description text {i+1}")
                        
                except Exception as text_error:
                    uploaded_files['errors'].append(f"Job description text {i+1} error: {str(text_error)}")
                    logger.error(f"Error saving job description text {i+1}: {text_error}")
        
        # Prepare response
        total_resumes = len(uploaded_files['resumes'])
        total_job_descriptions = len(uploaded_files['job_descriptions'])
        total_errors = len(uploaded_files['errors'])
        
        # Determine response status
        if total_resumes == 0 and total_job_descriptions == 0:
            if total_errors > 0:
                return jsonify({
                    'error': 'No files uploaded successfully',
                    'details': uploaded_files,
                    'timestamp': datetime.now().isoformat()
                }), 400
            else:
                return jsonify({'error': 'No files provided'}), 400
        
        # Success response
        response_data = {
            'message': f'Dual upload completed: {total_resumes} resumes, {total_job_descriptions} job descriptions',
            'summary': {
                'total_resumes': total_resumes,
                'total_job_descriptions': total_job_descriptions,
                'total_errors': total_errors,
                'success_rate': ((total_resumes + total_job_descriptions) / 
                               (total_resumes + total_job_descriptions + total_errors) * 100) if (total_resumes + total_job_descriptions + total_errors) > 0 else 0
            },
            'files': uploaded_files,
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if total_errors == 0 else 207  # 207 = Multi-Status (partial success)
        
        logger.info(f"Dual upload completed: {total_resumes} resumes, {total_job_descriptions} job descriptions, {total_errors} errors")
        return jsonify(response_data), status_code
        
    except Exception as e:
        return handle_upload_error(e, 'dual-upload')

@bp.route('/upload/batch-process', methods=['POST'])
def batch_process_and_analyze():
    """Upload files and immediately trigger analysis in one request"""
    try:
        logger.info("Batch process and analyze request received")
        
        # First, perform the dual upload
        upload_response = upload_dual_files()
        upload_data = upload_response[0].get_json() if upload_response[0].status_code in [200, 207] else None
        
        if not upload_data or 'files' not in upload_data:
            return upload_response  # Return upload errors
        
        uploaded_files = upload_data['files']
        resume_ids = [r['file_id'] for r in uploaded_files['resumes']]
        job_desc_ids = [j['file_id'] for j in uploaded_files['job_descriptions']]
        
        if not resume_ids or not job_desc_ids:
            return jsonify({
                'error': 'Need at least one resume and one job description for analysis',
                'upload_results': upload_data
            }), 400
        
        # Get analysis options from request
        analysis_options = {
            'include_skills': request.form.get('include_skills', 'true').lower() == 'true',
            'include_experience': request.form.get('include_experience', 'true').lower() == 'true', 
            'include_semantic': request.form.get('include_semantic', 'true').lower() == 'true',
            'include_keywords': request.form.get('include_keywords', 'true').lower() == 'true',
            'generate_recommendations': request.form.get('generate_recommendations', 'true').lower() == 'true',
            'detailed_feedback': request.form.get('detailed_feedback', 'true').lower() == 'true',
            'include_feedback': request.form.get('include_feedback', 'true').lower() == 'true',
            'include_comparison': request.form.get('include_comparison', 'true').lower() == 'true',
            'cross_analysis': request.form.get('cross_analysis', 'true').lower() == 'true'
        }
        
        # Trigger analysis using the new dual evaluation endpoint
        from app.routes.evaluation_routes import bp as eval_bp
        
        # Create analysis request data
        analysis_data = {
            'resume_ids': resume_ids,
            'job_description_ids': job_desc_ids,
            'options': analysis_options
        }
        
        # Import and call the evaluation function directly
        from app.routes.evaluation_routes import evaluate_dual_upload
        
        # Create a mock request context for analysis
        from flask import Flask
        from unittest.mock import patch
        
        with patch('flask.request') as mock_request:
            mock_request.json = analysis_data
            analysis_response = evaluate_dual_upload()
            
        analysis_result = analysis_response[0].get_json() if analysis_response[0].status_code == 200 else None
        
        # Combined response
        response_data = {
            'message': 'Batch process and analysis completed',
            'upload_results': upload_data,
            'analysis_results': analysis_result,
            'processing_summary': {
                'files_uploaded': {
                    'resumes': len(resume_ids),
                    'job_descriptions': len(job_desc_ids)
                },
                'analyses_completed': analysis_result['summary']['successful_analyses'] if analysis_result else 0,
                'total_processing_time': (upload_data.get('summary', {}).get('processing_time', 0) + 
                                        analysis_result['summary']['total_processing_time'] if analysis_result else 0)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if analysis_result and analysis_result['summary']['failed_analyses'] == 0 else 207
        
        logger.info(f"Batch process completed: {len(resume_ids)} resumes, {len(job_desc_ids)} job descriptions analyzed")
        return jsonify(response_data), status_code
        
    except Exception as e:
        return handle_upload_error(e, 'batch-process')
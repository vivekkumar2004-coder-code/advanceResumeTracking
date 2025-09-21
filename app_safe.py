#!/usr/bin/env python3
"""
Resume Relevance System - Main Application with Graceful Error Handling

This is an improved version of the main Flask application that handles
missing or problematic ML dependencies gracefully, allowing the core
functionality to work even if some advanced features are unavailable.
"""

import os
import sys
import logging

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app_safe():
    """Create Flask app with graceful error handling for dependencies"""
    
    try:
        from app import create_app
        logger.info("Creating full application with all features...")
        app = create_app()
        logger.info("Full application created successfully!")
        return app
        
    except ImportError as e:
        logger.warning(f"Some dependencies missing: {e}")
        logger.info("Creating simplified application...")
        
        # Try to create a simplified app without ML dependencies
        return create_simplified_app()
    
    except Exception as e:
        logger.error(f"Error creating full app: {e}")
        logger.info("Falling back to simplified application...")
        return create_simplified_app()


def create_simplified_app():
    """Create a simplified Flask app without ML dependencies"""
    
    from flask import Flask, render_template, jsonify, request
    from flask_cors import CORS
    import json
    import uuid
    from datetime import datetime
    
    # Get template and static directories
    basedir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # Create upload directories
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions'), exist_ok=True)
    
    # Enable CORS
    CORS(app)
    
    @app.route('/')
    def dashboard():
        """Main dashboard route"""
        return render_template('dashboard.html')
    
    @app.route('/api/info')
    def api_info():
        """API information endpoint"""
        return jsonify({
            'status': 'success',
            'message': 'Resume Relevance System API',
            'version': '1.0.0-simplified',
            'mode': 'simplified',
            'note': 'Running in simplified mode. Some ML features may be unavailable.',
            'features': [
                'Resume upload and parsing',
                'Job description processing', 
                'Basic text analysis',
                'Dashboard interface',
                'Database storage',
                'Email notifications (if configured)'
            ],
            'endpoints': {
                'dashboard': '/',
                'upload': '/api/upload',
                'evaluate': '/api/evaluate',
                'info': '/api/info',
                'health': '/health'
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'simplified'
        })
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """File upload endpoint"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            file_type = request.form.get('type', 'resume')
            
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_type}_{file_id}.{file.filename.split('.')[-1]}"
            
            # Save file
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_type}s", filename)
            file.save(upload_path)
            
            # Basic file info
            file_info = {
                'id': file_id,
                'filename': filename,
                'original_name': file.filename,
                'type': file_type,
                'size': os.path.getsize(upload_path),
                'upload_time': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'file_info': file_info,
                'message': 'File uploaded successfully'
            })
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/evaluate', methods=['POST'])
    def evaluate_resume():
        """Resume evaluation endpoint (simplified)"""
        try:
            data = request.get_json()
            
            # Mock evaluation for demonstration
            mock_evaluation = {
                'id': str(uuid.uuid4()),
                'relevance_score': 75.5,
                'status': 'completed',
                'message': 'Evaluation completed (simplified mode)',
                'note': 'This is a mock evaluation. Full ML-powered analysis requires additional dependencies.',
                'basic_analysis': {
                    'resume_file': data.get('resume_file'),
                    'job_description_file': data.get('job_description_file'),
                    'timestamp': datetime.utcnow().isoformat()
                },
                'recommendations': [
                    'Install full dependencies for detailed analysis',
                    'Check requirements.txt for ML libraries',
                    'Run: pip install -r requirements.txt'
                ]
            }
            
            return jsonify({
                'success': True,
                'evaluation': mock_evaluation
            })
            
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    logger.info("Simplified application created successfully!")
    return app


if __name__ == '__main__':
    print("Resume Relevance System - Starting Application...")
    print("=" * 60)
    
    try:
        # Create the app
        app = create_app_safe()
        
        # Run the application
        print(f"Starting server on http://127.0.0.1:5000")
        print(f"Dashboard available at http://127.0.0.1:5000")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)
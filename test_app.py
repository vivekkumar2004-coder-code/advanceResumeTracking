#!/usr/bin/env python3
"""
Simple Flask App Test

Test the Flask app startup without heavy ML dependencies.
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os


def create_simple_app():
    """Create a simplified Flask app for testing"""
    # Get the parent directory (project root) to find templates
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Enable CORS
    CORS(app)
    
    @app.route('/')
    def dashboard():
        """Dashboard route"""
        return render_template('dashboard.html')
    
    @app.route('/api/info')
    def api_info():
        """API info endpoint"""
        return jsonify({
            'status': 'success',
            'message': 'Flask app is running successfully',
            'version': '1.0.0',
            'endpoints': {
                'dashboard': '/',
                'info': '/api/info'
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Application is running'
        })
    
    return app


if __name__ == '__main__':
    app = create_simple_app()
    print("Simple Flask app created successfully!")
    app.run(debug=True, host='0.0.0.0', port=5001)
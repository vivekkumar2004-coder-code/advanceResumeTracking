from flask import Flask, render_template
from flask_cors import CORS
import os
import logging
from app.routes import upload_routes, evaluation_routes
from app.routes.database_routes import db_routes
from app.routes.email_routes import email_bp
from app.utils.database_manager import db_manager


def create_app():
    """Create and configure Flask application"""
    # Get the parent directory (project root) to find templates
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(app.instance_path), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Database configuration
    app.config['DATABASE_TYPE'] = os.environ.get('DATABASE_TYPE', 'sqlite')
    app.config['DB_PATH'] = os.environ.get('DB_PATH', 'data/resume_relevance.db')
    
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    try:
        db_manager.init_app(app)
        app.logger.info("Database manager initialized successfully")
        
        # Create tables if they don't exist
        with app.app_context():
            db_manager.create_tables()
            app.logger.info("Database tables verified/created")
            
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Register blueprints
    app.register_blueprint(upload_routes.bp)
    app.register_blueprint(evaluation_routes.bp)
    app.register_blueprint(db_routes, url_prefix='/api/database')
    app.register_blueprint(email_bp)
    
    # Dashboard route
    @app.route('/')
    @app.route('/dashboard')
    def dashboard():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        """Application health check"""
        db_health = db_manager.test_connection()
        
        return {
            'status': 'healthy' if db_health.get('connected', False) else 'unhealthy',
            'database': db_health,
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'timestamp': db_health.get('timestamp', '')
        }
    
    # Add database info endpoint
    @app.route('/api/info')
    def app_info():
        """Application and database information"""
        return {
            'application': 'Resume Relevance System',
            'version': '2.0.0',
            'features': [
                'Resume parsing and analysis',
                'Job description matching',
                'LLM-based feedback generation',
                'Advanced scoring system',
                'Database persistence',
                'RESTful API',
                'Automated email notifications',
                'Email template management',
                'Delivery tracking'
            ],
            'database': db_manager.get_database_info(),
            'endpoints': {
                'upload': '/api/upload',
                'evaluate': '/api/evaluate',
                'database': '/api/database',
                'email': '/api/email',
                'health': '/health',
                'info': '/api/info'
            }
        }
    
    app.logger.info("Flask application created and configured successfully")
    return app
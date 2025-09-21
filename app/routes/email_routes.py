"""
Email Routes

This module provides Flask routes for email functionality including
sending evaluation emails, configuring email settings, and tracking
email delivery status.
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from ..utils.email_sender import email_sender, EmailMessage, EmailStatus
from ..utils.email_config import email_config, EmailProvider, EmailConfig
from ..utils.database_manager import db_manager

logger = logging.getLogger(__name__)

email_bp = Blueprint('email', __name__, url_prefix='/api/email')

@email_bp.route('/send-evaluation', methods=['POST'])
def send_evaluation_email():
    """Send personalized evaluation email to candidate"""
    try:
        data = request.get_json()
        
        # Required fields
        required_fields = ['evaluation_id', 'candidate_email']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        evaluation_id = data['evaluation_id']
        candidate_email = data['candidate_email']
        
        # Get evaluation data from database
        evaluation_result = db_manager.get_evaluation_by_id(evaluation_id)
        if not evaluation_result:
            return jsonify({
                'success': False,
                'error': 'Evaluation not found'
            }), 404
        
        # Prepare candidate info
        candidate_info = {
            'name': data.get('candidate_name', 'Candidate'),
            'email': candidate_email,
            'phone': data.get('candidate_phone', ''),
            'linkedin': data.get('candidate_linkedin', ''),
            'portfolio': data.get('candidate_portfolio', '')
        }
        
        # Prepare job info
        job_info = {
            'title': evaluation_result.get('job_title', 'Software Engineer'),
            'company': data.get('company_name', 'Our Company'),
            'location': data.get('job_location', ''),
            'employment_type': data.get('employment_type', 'Full-time'),
            'description': evaluation_result.get('job_description', ''),
            'requirements': evaluation_result.get('job_requirements', []),
            'salary_range': data.get('salary_range', ''),
            'contact_email': data.get('contact_email', ''),
            'application_deadline': data.get('application_deadline', '')
        }
        
        # Optional company info
        company_info = {
            'name': data.get('company_name', 'Our Company'),
            'website': data.get('company_website', ''),
            'logo_url': data.get('company_logo_url', ''),
            'description': data.get('company_description', ''),
            'culture': data.get('company_culture', ''),
            'benefits': data.get('company_benefits', [])
        }
        
        # Send email
        result = email_sender.send_evaluation_email(
            evaluation_result=evaluation_result,
            candidate_info=candidate_info,
            job_info=job_info,
            company_info=company_info
        )
        
        # Save email record to database if successful
        if result['success']:
            try:
                db_manager.save_email_record({
                    'message_id': result['message_id'],
                    'evaluation_id': evaluation_id,
                    'candidate_email': candidate_email,
                    'candidate_name': candidate_info['name'],
                    'relevance_score': result.get('relevance_score', 0),
                    'template_used': result.get('template_used', ''),
                    'sent_at': result.get('sent_at'),
                    'status': 'sent'
                })
            except Exception as e:
                logger.error(f"Failed to save email record: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in send_evaluation_email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/send-custom', methods=['POST'])
def send_custom_email():
    """Send custom email message"""
    try:
        data = request.get_json()
        
        # Required fields
        required_fields = ['to_email', 'subject']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Create email message
        message = EmailMessage(
            to_email=data['to_email'],
            to_name=data.get('to_name', ''),
            subject=data['subject'],
            html_content=data.get('html_content', ''),
            text_content=data.get('text_content', ''),
            reply_to=data.get('reply_to'),
            priority=data.get('priority', 2),
            attachments=data.get('attachments', [])
        )
        
        # Send immediately or queue
        immediate = data.get('immediate', False)
        result = email_sender.send_email(message, immediate=immediate)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in send_custom_email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/status/<message_id>', methods=['GET'])
def get_email_status(message_id: str):
    """Get email delivery status"""
    try:
        status = email_sender.get_email_status(message_id)
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting email status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/config', methods=['GET'])
def get_email_config():
    """Get current email configuration"""
    try:
        config = email_config.get_config()
        
        # Return safe configuration (no sensitive data)
        safe_config = {
            'enabled': config.enabled,
            'provider': config.provider.value,
            'sender_email': config.sender_email,
            'sender_name': config.sender_name,
            'reply_to': config.reply_to,
            'max_emails_per_hour': config.max_emails_per_hour,
            'max_emails_per_day': config.max_emails_per_day,
            'retry_attempts': config.retry_attempts,
            'retry_delay': config.retry_delay,
            'smtp_server': config.smtp_server if config.provider == EmailProvider.SMTP else None,
            'smtp_port': config.smtp_port if config.provider == EmailProvider.SMTP else None,
            'smtp_use_ssl': config.smtp_use_ssl if config.provider == EmailProvider.SMTP else None,
            'smtp_use_tls': config.smtp_use_tls if config.provider == EmailProvider.SMTP else None
        }
        
        return jsonify({
            'success': True,
            'config': safe_config
        })
        
    except Exception as e:
        logger.error(f"Error getting email config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/config', methods=['POST'])
def update_email_config():
    """Update email configuration"""
    try:
        data = request.get_json()
        
        # Create new configuration
        try:
            provider = EmailProvider(data.get('provider', 'smtp'))
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid email provider'
            }), 400
        
        config = EmailConfig(
            enabled=data.get('enabled', True),
            provider=provider,
            sender_email=data.get('sender_email', ''),
            sender_name=data.get('sender_name', ''),
            reply_to=data.get('reply_to'),
            max_emails_per_hour=data.get('max_emails_per_hour', 100),
            max_emails_per_day=data.get('max_emails_per_day', 1000),
            retry_attempts=data.get('retry_attempts', 3),
            retry_delay=data.get('retry_delay', 60),
            
            # Provider-specific settings
            smtp_server=data.get('smtp_server'),
            smtp_port=data.get('smtp_port', 587),
            smtp_username=data.get('smtp_username'),
            smtp_password=data.get('smtp_password'),
            smtp_use_ssl=data.get('smtp_use_ssl', False),
            smtp_use_tls=data.get('smtp_use_tls', True),
            
            api_key=data.get('api_key'),
            api_secret=data.get('api_secret'),
            region=data.get('region', 'us-east-1')
        )
        
        # Validate configuration
        validation_result = email_config.validate_config(config)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': validation_result['error']
            }), 400
        
        # Update configuration
        email_config.update_config(config)
        
        # Reinitialize email sender with new config
        email_sender.__init__(config)
        
        return jsonify({
            'success': True,
            'message': 'Email configuration updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating email config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/test', methods=['POST'])
def test_email_config():
    """Test email configuration by sending a test email"""
    try:
        data = request.get_json()
        test_email = data.get('test_email')
        
        if not test_email:
            return jsonify({
                'success': False,
                'error': 'Test email address is required'
            }), 400
        
        # Create test message
        message = EmailMessage(
            to_email=test_email,
            subject="Resume Analysis System - Test Email",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">Email Configuration Test</h2>
                <p>This is a test email from your Resume Analysis System.</p>
                <p>If you received this email, your email configuration is working correctly!</p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>Test Details:</strong><br>
                    Provider: {provider}<br>
                    Sent at: {timestamp}
                </div>
                <p>Best regards,<br>Resume Analysis System</p>
            </div>
            """.format(
                provider=email_config.get_config().provider.value,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            text_content=f"""
Email Configuration Test

This is a test email from your Resume Analysis System.
If you received this email, your email configuration is working correctly!

Provider: {email_config.get_config().provider.value}
Sent at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
Resume Analysis System
            """
        )
        
        # Send test email immediately
        result = email_sender.send_email(message, immediate=True)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error testing email config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/templates', methods=['GET'])
def get_email_templates():
    """Get available email templates"""
    try:
        templates = email_sender.template_manager.get_available_templates()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error getting email templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/preview', methods=['POST'])
def preview_email():
    """Preview email template with sample data"""
    try:
        data = request.get_json()
        template_name = data.get('template_name', 'medium_relevance')
        
        # Sample data for preview
        sample_evaluation = {
            'relevance_score': 85.5,
            'matched_skills': ['Python', 'Machine Learning', 'Flask'],
            'missing_skills': ['Docker', 'Kubernetes'],
            'skill_match_percentage': 85.5,
            'experience_match': True,
            'education_match': True,
            'feedback': "Strong technical background with relevant experience."
        }
        
        sample_candidate = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1 (555) 123-4567',
            'linkedin': 'https://linkedin.com/in/johndoe'
        }
        
        sample_job = {
            'title': 'Senior Python Developer',
            'company': 'Tech Innovations Inc.',
            'location': 'San Francisco, CA',
            'employment_type': 'Full-time',
            'description': 'We are looking for a Senior Python Developer...'
        }
        
        sample_company = {
            'name': 'Tech Innovations Inc.',
            'website': 'https://techinnovations.com',
            'description': 'Leading technology company focused on innovation.'
        }
        
        # Generate preview
        preview_data = email_sender.template_manager.generate_personalized_email(
            sample_evaluation, sample_candidate, sample_job, sample_company
        )
        
        return jsonify({
            'success': True,
            'preview': preview_data
        })
        
    except Exception as e:
        logger.error(f"Error previewing email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/history', methods=['GET'])
def get_email_history():
    """Get email sending history"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        
        # Get email history from database
        history = db_manager.get_email_history(
            page=page,
            per_page=per_page,
            status_filter=status_filter
        )
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting email history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_bp.route('/stats', methods=['GET'])
def get_email_stats():
    """Get email sending statistics"""
    try:
        # Get date range from query parameters
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days by default
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        
        # Get statistics from database
        stats = db_manager.get_email_stats(start_date, end_date)
        
        # Add current queue status
        stats['queue_size'] = email_sender.email_queue.qsize()
        stats['processing_active'] = email_sender.is_processing
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting email stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@email_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

@email_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@email_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
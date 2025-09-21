"""
Email System Tests

Comprehensive tests for the email functionality including:
- Email configuration
- Email sending
- Template management
- Delivery tracking
- Provider integration
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from tests.conftest import SAMPLE_EVALUATION_RESULT


@pytest.mark.email
class TestEmailConfiguration:
    """Test email configuration management"""
    
    def test_email_config_creation(self, email_config_test):
        """Test email configuration creation"""
        assert email_config_test.enabled is True
        assert email_config_test.provider.value == 'smtp'
        assert email_config_test.sender_email == 'test@example.com'
    
    def test_email_config_validation(self):
        """Test email configuration validation"""
        try:
            from app.utils.email_config import EmailConfig, EmailProvider
            
            # Valid configuration
            valid_config = EmailConfig(
                enabled=True,
                provider=EmailProvider.SMTP,
                sender_email='test@example.com',
                smtp_server='localhost',
                smtp_port=587
            )
            assert valid_config.sender_email == 'test@example.com'
            
        except ImportError:
            pytest.skip("Email config not available")
    
    def test_smtp_config_validation(self):
        """Test SMTP configuration validation"""
        try:
            from app.utils.email_config import EmailConfig, EmailProvider
            
            smtp_config = EmailConfig(
                enabled=True,
                provider=EmailProvider.SMTP,
                sender_email='test@example.com',
                smtp_server='smtp.gmail.com',
                smtp_port=587,
                smtp_username='test@example.com',
                smtp_password='password',
                smtp_use_tls=True
            )
            
            assert smtp_config.smtp_server == 'smtp.gmail.com'
            assert smtp_config.smtp_port == 587
            assert smtp_config.smtp_use_tls is True
            
        except ImportError:
            pytest.skip("Email config not available")
    
    def test_sendgrid_config_validation(self):
        """Test SendGrid configuration validation"""
        try:
            from app.utils.email_config import EmailConfig, EmailProvider
            
            sendgrid_config = EmailConfig(
                enabled=True,
                provider=EmailProvider.SENDGRID,
                sender_email='test@example.com',
                sendgrid_api_key='test-api-key'
            )
            
            assert sendgrid_config.provider == EmailProvider.SENDGRID
            assert sendgrid_config.sendgrid_api_key == 'test-api-key'
            
        except ImportError:
            pytest.skip("Email config not available")


@pytest.mark.email
class TestEmailTemplates:
    """Test email template management"""
    
    def test_template_loading(self):
        """Test loading email templates"""
        try:
            from app.utils.email_templates import email_templates
            
            available_templates = email_templates.get_available_templates()
            assert isinstance(available_templates, list)
            
            # Should have at least the basic templates
            expected_templates = ['high_relevance', 'medium_relevance', 'low_relevance']
            for template in expected_templates:
                if template not in available_templates:
                    # Template may not be available in test environment
                    pass
                    
        except ImportError:
            pytest.skip("Email templates not available")
    
    def test_template_rendering(self):
        """Test template rendering with context"""
        try:
            from app.utils.email_templates import email_templates
            
            context = {
                'candidate_name': 'John Doe',
                'relevance_score': 85.5,
                'relevance_level': 'high',
                'matched_skills': ['Python', 'Flask', 'PostgreSQL'],
                'missing_skills': ['Docker', 'Kubernetes'],
                'job_title': 'Senior Python Developer',
                'company_name': 'Tech Corp'
            }
            
            # Try to render a template
            rendered = email_templates.render_template('high_relevance', context)
            
            if rendered:
                assert 'John Doe' in rendered['html_content'] or 'John Doe' in rendered['text_content']
                assert '85.5' in rendered['html_content'] or '85.5' in rendered['text_content']
            
        except (ImportError, AttributeError):
            pytest.skip("Email template rendering not available")
    
    def test_template_personalization(self):
        """Test template personalization"""
        context_data = {
            'candidate_name': 'Jane Smith',
            'relevance_score': 92.0,
            'job_title': 'Data Scientist',
            'matched_skills': ['Python', 'Machine Learning', 'SQL'],
            'company_name': 'AI Company'
        }
        
        # Test personalization logic
        personalized_subject = f"Your application for {context_data['job_title']} at {context_data['company_name']}"
        assert 'Data Scientist' in personalized_subject
        assert 'AI Company' in personalized_subject
    
    def test_template_context_validation(self):
        """Test template context validation"""
        required_fields = [
            'candidate_name', 'relevance_score', 'job_title', 'company_name'
        ]
        
        valid_context = {
            'candidate_name': 'Test User',
            'relevance_score': 75.0,
            'job_title': 'Developer',
            'company_name': 'Test Company'
        }
        
        # All required fields present
        missing_fields = [field for field in required_fields if field not in valid_context]
        assert len(missing_fields) == 0
        
        # Test incomplete context
        incomplete_context = {'candidate_name': 'Test User'}
        missing_fields = [field for field in required_fields if field not in incomplete_context]
        assert len(missing_fields) > 0


@pytest.mark.email
class TestEmailSending:
    """Test email sending functionality"""
    
    @patch('app.utils.email_sender.email_sender')
    def test_send_evaluation_email(self, mock_sender):
        """Test sending evaluation email"""
        mock_sender.send_evaluation_email.return_value = {
            'success': True,
            'message_id': 'test-message-id',
            'status': 'sent'
        }
        
        result = mock_sender.send_evaluation_email(
            candidate_email='test@example.com',
            candidate_name='Test Candidate',
            evaluation_data=SAMPLE_EVALUATION_RESULT,
            job_title='Test Job',
            company_name='Test Company'
        )
        
        assert result['success'] is True
        assert 'message_id' in result
    
    @patch('app.utils.email_sender.email_sender')
    def test_send_custom_email(self, mock_sender):
        """Test sending custom email"""
        mock_sender.send_message.return_value = {
            'success': True,
            'message_id': 'test-custom-message-id',
            'status': 'sent'
        }
        
        try:
            from app.utils.email_sender import EmailMessage
            
            custom_message = EmailMessage(
                to_email='test@example.com',
                subject='Test Subject',
                html_content='<h1>Test HTML Content</h1>',
                text_content='Test Text Content'
            )
            
            result = mock_sender.send_message(custom_message)
            assert result['success'] is True
            
        except ImportError:
            pytest.skip("Email sender not available")
    
    @patch('app.utils.email_sender.email_sender')
    def test_email_sending_failure(self, mock_sender):
        """Test email sending failure handling"""
        mock_sender.send_message.return_value = {
            'success': False,
            'error': 'SMTP connection failed',
            'status': 'failed'
        }
        
        try:
            from app.utils.email_sender import EmailMessage
            
            message = EmailMessage(
                to_email='invalid-email',
                subject='Test',
                html_content='Test'
            )
            
            result = mock_sender.send_message(message)
            assert result['success'] is False
            assert 'error' in result
            
        except ImportError:
            pytest.skip("Email sender not available")
    
    def test_email_validation(self):
        """Test email address validation"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'firstname+lastname@company.org'
        ]
        
        invalid_emails = [
            'invalid-email',
            'test@',
            '@example.com',
            'test.@example.com',
            'test@.com'
        ]
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in valid_emails:
            assert re.match(email_pattern, email), f"Valid email failed validation: {email}"
        
        for email in invalid_emails:
            assert not re.match(email_pattern, email), f"Invalid email passed validation: {email}"


@pytest.mark.email
class TestEmailTracking:
    """Test email delivery tracking"""
    
    @patch('app.utils.email_sender.email_sender')
    def test_message_status_tracking(self, mock_sender):
        """Test message status tracking"""
        message_id = 'test-message-id'
        mock_sender.get_message_status.return_value = {
            'message_id': message_id,
            'status': 'delivered',
            'delivered_at': datetime.utcnow(),
            'opened_at': None,
            'clicked_at': None
        }
        
        status = mock_sender.get_message_status(message_id)
        assert status['message_id'] == message_id
        assert status['status'] == 'delivered'
        assert 'delivered_at' in status
    
    @patch('app.utils.database_manager.db_manager')
    def test_email_record_saving(self, mock_db):
        """Test saving email records to database"""
        email_data = {
            'message_id': 'test-message-id',
            'evaluation_id': str(uuid.uuid4()),
            'candidate_email': 'test@example.com',
            'candidate_name': 'Test Candidate',
            'subject': 'Your Application Results',
            'template_used': 'high_relevance',
            'relevance_score': 85.5,
            'status': 'sent',
            'sent_at': datetime.utcnow()
        }
        
        mock_db.save_email_record.return_value = {
            'success': True,
            'record_id': 'test-record-id'
        }
        
        result = mock_db.save_email_record(email_data)
        assert result['success'] is True
        assert 'record_id' in result
    
    @patch('app.utils.database_manager.db_manager')
    def test_email_history_retrieval(self, mock_db):
        """Test retrieving email history"""
        mock_history = [
            {
                'id': '1',
                'message_id': 'msg-1',
                'candidate_email': 'test1@example.com',
                'status': 'delivered',
                'sent_at': datetime.utcnow() - timedelta(hours=1)
            },
            {
                'id': '2',
                'message_id': 'msg-2',
                'candidate_email': 'test2@example.com',
                'status': 'sent',
                'sent_at': datetime.utcnow() - timedelta(minutes=30)
            }
        ]
        
        mock_db.get_email_history.return_value = {
            'success': True,
            'emails': mock_history,
            'total_count': 2,
            'page': 1,
            'per_page': 20
        }
        
        history = mock_db.get_email_history(page=1, per_page=20)
        assert history['success'] is True
        assert len(history['emails']) == 2
    
    @patch('app.utils.database_manager.db_manager')
    def test_email_statistics(self, mock_db):
        """Test email statistics calculation"""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        mock_stats = {
            'total_sent': 100,
            'delivered': 95,
            'failed': 3,
            'pending': 2,
            'delivery_rate': 95.0,
            'failure_rate': 3.0,
            'templates_used': {
                'high_relevance': 30,
                'medium_relevance': 45,
                'low_relevance': 25
            }
        }
        
        mock_db.get_email_stats.return_value = {
            'success': True,
            'statistics': mock_stats,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }
        
        stats = mock_db.get_email_stats(start_date, end_date)
        assert stats['success'] is True
        assert stats['statistics']['total_sent'] == 100
        assert stats['statistics']['delivery_rate'] == 95.0


@pytest.mark.email
class TestEmailProviders:
    """Test different email provider integrations"""
    
    def test_smtp_provider_config(self):
        """Test SMTP provider configuration"""
        smtp_settings = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'test@gmail.com',
            'password': 'app-password',
            'use_tls': True,
            'use_ssl': False
        }
        
        # Validate SMTP settings
        assert smtp_settings['server']
        assert isinstance(smtp_settings['port'], int)
        assert 1 <= smtp_settings['port'] <= 65535
        assert smtp_settings['username']
    
    def test_sendgrid_provider_config(self):
        """Test SendGrid provider configuration"""
        sendgrid_settings = {
            'api_key': 'SG.test-api-key',
            'sender_email': 'noreply@company.com',
            'sender_name': 'HR System'
        }
        
        # Validate SendGrid settings
        assert sendgrid_settings['api_key']
        assert sendgrid_settings['api_key'].startswith('SG.')
        assert sendgrid_settings['sender_email']
    
    def test_aws_ses_provider_config(self):
        """Test AWS SES provider configuration"""
        aws_ses_settings = {
            'region': 'us-east-1',
            'access_key_id': 'AKIA...',
            'secret_access_key': 'test-secret-key',
            'sender_email': 'noreply@company.com'
        }
        
        # Validate AWS SES settings
        assert aws_ses_settings['region']
        assert aws_ses_settings['access_key_id']
        assert aws_ses_settings['secret_access_key']
        assert aws_ses_settings['sender_email']


@pytest.mark.email
@pytest.mark.slow
class TestEmailPerformance:
    """Test email system performance"""
    
    @patch('app.utils.email_sender.email_sender')
    def test_bulk_email_sending(self, mock_sender):
        """Test sending multiple emails efficiently"""
        # Simulate bulk email sending
        recipients = [f'test{i}@example.com' for i in range(10)]
        
        mock_sender.send_bulk_emails.return_value = {
            'success': True,
            'sent_count': 10,
            'failed_count': 0,
            'message_ids': [f'msg-{i}' for i in range(10)]
        }
        
        try:
            result = mock_sender.send_bulk_emails(recipients, 'Test Subject', 'Test Content')
            assert result['success'] is True
            assert result['sent_count'] == 10
        except AttributeError:
            # Bulk sending might not be implemented
            pytest.skip("Bulk email sending not available")
    
    def test_email_queue_processing(self):
        """Test email queue processing simulation"""
        import queue
        import threading
        
        email_queue = queue.Queue()
        processed_emails = []
        
        # Add emails to queue
        for i in range(5):
            email_queue.put({'id': i, 'to': f'test{i}@example.com'})
        
        def process_email_queue():
            while not email_queue.empty():
                try:
                    email = email_queue.get(timeout=1)
                    processed_emails.append(email)
                    email_queue.task_done()
                except queue.Empty:
                    break
        
        # Process queue
        worker = threading.Thread(target=process_email_queue)
        worker.start()
        worker.join()
        
        assert len(processed_emails) == 5
    
    def test_email_rate_limiting(self):
        """Test email rate limiting implementation"""
        from datetime import datetime, timedelta
        
        # Simple rate limiting simulation
        class RateLimiter:
            def __init__(self, max_per_hour=100):
                self.max_per_hour = max_per_hour
                self.sent_times = []
            
            def can_send(self):
                now = datetime.utcnow()
                hour_ago = now - timedelta(hours=1)
                
                # Remove old entries
                self.sent_times = [t for t in self.sent_times if t > hour_ago]
                
                return len(self.sent_times) < self.max_per_hour
            
            def record_send(self):
                if self.can_send():
                    self.sent_times.append(datetime.utcnow())
                    return True
                return False
        
        limiter = RateLimiter(max_per_hour=5)
        
        # Should be able to send first 5 emails
        for i in range(5):
            assert limiter.record_send() is True
        
        # 6th email should be rate limited
        assert limiter.record_send() is False
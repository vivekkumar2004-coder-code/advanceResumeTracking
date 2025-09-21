"""
Email Service Configuration Module

This module provides configuration for various email services including SMTP
and API-based services like SendGrid, AWS SES, and others.
"""

import os
import logging
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class EmailProvider(Enum):
    """Supported email providers"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    MAILGUN = "mailgun"
    OUTLOOK = "outlook"
    GMAIL = "gmail"

@dataclass
class EmailConfig:
    """Email configuration data class"""
    provider: EmailProvider
    enabled: bool = True
    
    # SMTP Configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # API Configuration
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    region: Optional[str] = None
    
    # Sender Information
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    reply_to: Optional[str] = None
    
    # Rate Limiting
    max_emails_per_hour: int = 100
    max_emails_per_day: int = 1000
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    
    def validate(self) -> bool:
        """Validate configuration based on provider"""
        if not self.enabled:
            return True
            
        if not self.sender_email:
            logger.error("Sender email is required")
            return False
            
        if self.provider == EmailProvider.SMTP:
            required_fields = [self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]
            if not all(required_fields):
                logger.error("SMTP configuration incomplete")
                return False
                
        elif self.provider in [EmailProvider.SENDGRID, EmailProvider.MAILGUN]:
            if not self.api_key:
                logger.error(f"{self.provider.value} API key is required")
                return False
                
        elif self.provider == EmailProvider.AWS_SES:
            if not all([self.api_key, self.api_secret, self.region]):
                logger.error("AWS SES configuration incomplete")
                return False
                
        return True

class EmailConfigManager:
    """Manages email configuration from environment variables and settings"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> EmailConfig:
        """Load email configuration from environment variables"""
        provider_str = os.getenv('EMAIL_PROVIDER', 'smtp').lower()
        
        try:
            provider = EmailProvider(provider_str)
        except ValueError:
            logger.warning(f"Unknown email provider: {provider_str}, defaulting to SMTP")
            provider = EmailProvider.SMTP
        
        config = EmailConfig(
            provider=provider,
            enabled=os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
            
            # SMTP Settings
            smtp_server=os.getenv('SMTP_SERVER'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            smtp_use_ssl=os.getenv('SMTP_USE_SSL', 'false').lower() == 'true',
            smtp_username=os.getenv('SMTP_USERNAME'),
            smtp_password=os.getenv('SMTP_PASSWORD'),
            
            # API Settings
            api_key=os.getenv('EMAIL_API_KEY'),
            api_secret=os.getenv('EMAIL_API_SECRET'),
            region=os.getenv('EMAIL_REGION', 'us-east-1'),
            
            # Sender Settings
            sender_email=os.getenv('EMAIL_SENDER'),
            sender_name=os.getenv('EMAIL_SENDER_NAME', 'Resume Analysis System'),
            reply_to=os.getenv('EMAIL_REPLY_TO'),
            
            # Rate Limiting
            max_emails_per_hour=int(os.getenv('EMAIL_MAX_PER_HOUR', '100')),
            max_emails_per_day=int(os.getenv('EMAIL_MAX_PER_DAY', '1000')),
            
            # Retry Settings
            max_retries=int(os.getenv('EMAIL_MAX_RETRIES', '3')),
            retry_delay=int(os.getenv('EMAIL_RETRY_DELAY', '60'))
        )
        
        return config
    
    def get_config(self) -> EmailConfig:
        """Get current email configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update email configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def test_configuration(self) -> Dict[str, Any]:
        """Test email configuration validity"""
        result = {
            'valid': False,
            'provider': self.config.provider.value,
            'enabled': self.config.enabled,
            'errors': []
        }
        
        if not self.config.enabled:
            result['errors'].append('Email service is disabled')
            return result
            
        if not self.config.validate():
            result['errors'].append('Configuration validation failed')
            return result
            
        # Additional provider-specific tests
        try:
            if self.config.provider == EmailProvider.SMTP:
                self._test_smtp_connection()
            elif self.config.provider == EmailProvider.SENDGRID:
                self._test_sendgrid_connection()
            # Add more provider tests as needed
            
            result['valid'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
            
        return result
    
    def _test_smtp_connection(self) -> None:
        """Test SMTP connection"""
        import smtplib
        from email.mime.text import MIMEText
        
        try:
            if self.config.smtp_use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
            else:
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                if self.config.smtp_use_tls:
                    server.starttls()
            
            if self.config.smtp_username and self.config.smtp_password:
                server.login(self.config.smtp_username, self.config.smtp_password)
            
            server.quit()
            logger.info("SMTP connection test successful")
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            raise
    
    def _test_sendgrid_connection(self) -> None:
        """Test SendGrid API connection"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.config.api_key)
            
            # Test with a simple API call
            response = sg.client.user.profile.get()
            if response.status_code == 200:
                logger.info("SendGrid connection test successful")
            else:
                raise Exception(f"SendGrid API returned status code: {response.status_code}")
                
        except ImportError:
            raise Exception("SendGrid library not installed. Install with: pip install sendgrid")
        except Exception as e:
            logger.error(f"SendGrid connection test failed: {e}")
            raise

# Predefined configurations for common providers
COMMON_CONFIGS = {
    'gmail': {
        'provider': EmailProvider.SMTP,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_use_tls': True,
        'smtp_use_ssl': False
    },
    'outlook': {
        'provider': EmailProvider.SMTP,
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'smtp_use_tls': True,
        'smtp_use_ssl': False
    },
    'yahoo': {
        'provider': EmailProvider.SMTP,
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'smtp_use_tls': True,
        'smtp_use_ssl': False
    },
    'sendgrid': {
        'provider': EmailProvider.SENDGRID,
        'smtp_server': 'smtp.sendgrid.net',
        'smtp_port': 587,
        'smtp_use_tls': True,
        'smtp_username': 'apikey'
    }
}

# Global email config manager instance
email_config = EmailConfigManager()
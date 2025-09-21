"""
Email Sending Service

This module provides email sending functionality with support for multiple
providers (SMTP, SendGrid, AWS SES, etc.) and includes retry logic, 
queue management, and delivery tracking.
"""

import smtplib
import ssl
import logging
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from queue import Queue, Empty

from .email_config import EmailConfig, EmailProvider, email_config
from .email_templates import EmailTemplateManager, email_templates

logger = logging.getLogger(__name__)

class EmailStatus(Enum):
    """Email delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRYING = "retrying"

@dataclass
class EmailMessage:
    """Email message data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    to_email: str = ""
    to_name: str = ""
    from_email: str = ""
    from_name: str = ""
    reply_to: Optional[str] = None
    subject: str = ""
    html_content: str = ""
    text_content: str = ""
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    status: EmailStatus = EmailStatus.PENDING
    priority: int = 1  # 1 = high, 2 = medium, 3 = low
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    # Tracking
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    
    # Context for personalization
    template_context: Dict[str, Any] = field(default_factory=dict)
    template_name: Optional[str] = None

class EmailRateLimiter:
    """Rate limiting for email sending"""
    
    def __init__(self, max_per_hour: int = 100, max_per_day: int = 1000):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.hourly_count = 0
        self.daily_count = 0
        self.hour_reset_time = datetime.now() + timedelta(hours=1)
        self.day_reset_time = datetime.now() + timedelta(days=1)
        self.lock = threading.Lock()
    
    def can_send(self) -> bool:
        """Check if we can send an email based on rate limits"""
        with self.lock:
            now = datetime.now()
            
            # Reset counters if time periods have passed
            if now >= self.hour_reset_time:
                self.hourly_count = 0
                self.hour_reset_time = now + timedelta(hours=1)
            
            if now >= self.day_reset_time:
                self.daily_count = 0
                self.day_reset_time = now + timedelta(days=1)
            
            return (self.hourly_count < self.max_per_hour and 
                   self.daily_count < self.max_per_day)
    
    def record_send(self) -> None:
        """Record that an email was sent"""
        with self.lock:
            self.hourly_count += 1
            self.daily_count += 1

class EmailSender:
    """Main email sending service"""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or email_config.get_config()
        self.template_manager = EmailTemplateManager()
        self.rate_limiter = EmailRateLimiter(
            self.config.max_emails_per_hour,
            self.config.max_emails_per_day
        )
        
        # Email queue for batch processing
        self.email_queue = Queue()
        self.is_processing = False
        self.processing_thread = None
        
        # Delivery tracking
        self.sent_emails = {}
        self.failed_emails = {}
        
        # Initialize provider-specific clients
        self._init_providers()
    
    def _init_providers(self):
        """Initialize provider-specific clients"""
        self.smtp_client = None
        self.sendgrid_client = None
        self.ses_client = None
        
        if not self.config.enabled:
            logger.info("Email service is disabled")
            return
        
        try:
            if self.config.provider == EmailProvider.SENDGRID:
                self._init_sendgrid()
            elif self.config.provider == EmailProvider.AWS_SES:
                self._init_aws_ses()
            # SMTP is initialized per-send for better connection management
                
        except Exception as e:
            logger.error(f"Failed to initialize email provider {self.config.provider}: {e}")
    
    def _init_sendgrid(self):
        """Initialize SendGrid client"""
        try:
            import sendgrid
            self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=self.config.api_key)
            logger.info("SendGrid client initialized")
        except ImportError:
            logger.error("SendGrid library not installed. Install with: pip install sendgrid")
            raise
    
    def _init_aws_ses(self):
        """Initialize AWS SES client"""
        try:
            import boto3
            self.ses_client = boto3.client(
                'ses',
                aws_access_key_id=self.config.api_key,
                aws_secret_access_key=self.config.api_secret,
                region_name=self.config.region
            )
            logger.info("AWS SES client initialized")
        except ImportError:
            logger.error("Boto3 library not installed. Install with: pip install boto3")
            raise
    
    def send_email(self, message: EmailMessage, immediate: bool = False) -> Dict[str, Any]:
        """Send an email message"""
        if not self.config.enabled:
            return {
                'success': False,
                'message_id': message.id,
                'error': 'Email service is disabled'
            }
        
        # Validate message
        if not self._validate_message(message):
            return {
                'success': False,
                'message_id': message.id,
                'error': 'Message validation failed'
            }
        
        # Set sender info if not provided
        if not message.from_email:
            message.from_email = self.config.sender_email
        if not message.from_name:
            message.from_name = self.config.sender_name
        if not message.reply_to:
            message.reply_to = self.config.reply_to
        
        if immediate:
            return self._send_immediately(message)
        else:
            return self._queue_email(message)
    
    def _validate_message(self, message: EmailMessage) -> bool:
        """Validate email message"""
        if not message.to_email:
            logger.error("Recipient email is required")
            return False
        
        if not message.subject:
            logger.error("Email subject is required")
            return False
        
        if not message.html_content and not message.text_content:
            logger.error("Email content is required")
            return False
        
        return True
    
    def _queue_email(self, message: EmailMessage) -> Dict[str, Any]:
        """Add email to processing queue"""
        message.status = EmailStatus.QUEUED
        self.email_queue.put(message)
        
        # Start processing thread if not running
        if not self.is_processing:
            self.start_processing()
        
        return {
            'success': True,
            'message_id': message.id,
            'status': 'queued'
        }
    
    def _send_immediately(self, message: EmailMessage) -> Dict[str, Any]:
        """Send email immediately"""
        if not self.rate_limiter.can_send():
            return {
                'success': False,
                'message_id': message.id,
                'error': 'Rate limit exceeded'
            }
        
        try:
            message.status = EmailStatus.SENDING
            
            if self.config.provider == EmailProvider.SMTP:
                result = self._send_via_smtp(message)
            elif self.config.provider == EmailProvider.SENDGRID:
                result = self._send_via_sendgrid(message)
            elif self.config.provider == EmailProvider.AWS_SES:
                result = self._send_via_ses(message)
            else:
                raise ValueError(f"Unsupported email provider: {self.config.provider}")
            
            if result['success']:
                message.status = EmailStatus.SENT
                message.sent_at = datetime.now()
                self.rate_limiter.record_send()
                self.sent_emails[message.id] = message
                logger.info(f"Email sent successfully: {message.id}")
            else:
                message.status = EmailStatus.FAILED
                message.last_error = result.get('error')
                self.failed_emails[message.id] = message
                logger.error(f"Email send failed: {message.id} - {message.last_error}")
            
            return result
            
        except Exception as e:
            message.status = EmailStatus.FAILED
            message.last_error = str(e)
            self.failed_emails[message.id] = message
            logger.error(f"Email send error: {message.id} - {e}")
            
            return {
                'success': False,
                'message_id': message.id,
                'error': str(e)
            }
    
    def _send_via_smtp(self, message: EmailMessage) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{message.from_name} <{message.from_email}>"
            msg['To'] = f"{message.to_name} <{message.to_email}>"
            
            if message.reply_to:
                msg['Reply-To'] = message.reply_to
            
            # Add text and HTML parts
            if message.text_content:
                text_part = MIMEText(message.text_content, 'plain')
                msg.attach(text_part)
            
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html')
                msg.attach(html_part)
            
            # Add attachments
            for attachment in message.attachments:
                self._add_attachment(msg, attachment)
            
            # Send email
            if self.config.smtp_use_ssl:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
            else:
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                if self.config.smtp_use_tls:
                    server.starttls()
            
            if self.config.smtp_username and self.config.smtp_password:
                server.login(self.config.smtp_username, self.config.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            return {
                'success': True,
                'message_id': message.id,
                'provider': 'smtp'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message_id': message.id,
                'error': str(e),
                'provider': 'smtp'
            }
    
    def _send_via_sendgrid(self, message: EmailMessage) -> Dict[str, Any]:
        """Send email via SendGrid"""
        try:
            from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent
            
            mail = Mail()
            mail.from_email = From(message.from_email, message.from_name)
            mail.to = [To(message.to_email, message.to_name)]
            mail.subject = Subject(message.subject)
            
            if message.text_content:
                mail.plain_text_content = PlainTextContent(message.text_content)
            
            if message.html_content:
                mail.html_content = HtmlContent(message.html_content)
            
            if message.reply_to:
                mail.reply_to_email = message.reply_to
            
            response = self.sendgrid_client.send(mail)
            
            return {
                'success': response.status_code in [200, 201, 202],
                'message_id': message.id,
                'provider': 'sendgrid',
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'message_id': message.id,
                'error': str(e),
                'provider': 'sendgrid'
            }
    
    def _send_via_ses(self, message: EmailMessage) -> Dict[str, Any]:
        """Send email via AWS SES"""
        try:
            # Prepare destination
            destination = {'ToAddresses': [message.to_email]}
            
            # Prepare message
            email_message = {
                'Subject': {'Data': message.subject, 'Charset': 'UTF-8'}
            }
            
            # Add content
            body = {}
            if message.text_content:
                body['Text'] = {'Data': message.text_content, 'Charset': 'UTF-8'}
            if message.html_content:
                body['Html'] = {'Data': message.html_content, 'Charset': 'UTF-8'}
            
            email_message['Body'] = body
            
            response = self.ses_client.send_email(
                Source=f"{message.from_name} <{message.from_email}>",
                Destination=destination,
                Message=email_message,
                ReplyToAddresses=[message.reply_to] if message.reply_to else []
            )
            
            return {
                'success': True,
                'message_id': message.id,
                'provider': 'aws_ses',
                'ses_message_id': response.get('MessageId')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message_id': message.id,
                'error': str(e),
                'provider': 'aws_ses'
            }
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")
    
    def start_processing(self):
        """Start email queue processing thread"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
        logger.info("Email queue processing started")
    
    def stop_processing(self):
        """Stop email queue processing"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("Email queue processing stopped")
    
    def _process_queue(self):
        """Process email queue in background thread"""
        while self.is_processing:
            try:
                # Get message from queue (non-blocking)
                message = self.email_queue.get(timeout=1)
                
                # Check if message should be sent now
                if message.scheduled_at and datetime.now() < message.scheduled_at:
                    # Re-queue for later
                    self.email_queue.put(message)
                    time.sleep(1)
                    continue
                
                # Try to send the message
                result = self._send_immediately(message)
                
                # Handle retry logic
                if not result['success'] and message.attempts < message.max_attempts:
                    message.attempts += 1
                    message.status = EmailStatus.RETRYING
                    message.last_error = result.get('error')
                    
                    # Re-queue with delay
                    message.scheduled_at = datetime.now() + timedelta(
                        seconds=self.config.retry_delay * message.attempts
                    )
                    self.email_queue.put(message)
                    
                    logger.info(f"Retrying email {message.id} (attempt {message.attempts})")
                
                # Mark task as done
                self.email_queue.task_done()
                
            except Empty:
                # No messages in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing email queue: {e}")
                time.sleep(1)
    
    def send_evaluation_email(self,
                            evaluation_result: Dict[str, Any],
                            candidate_info: Dict[str, Any],
                            job_info: Dict[str, Any],
                            company_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send personalized evaluation email to candidate"""
        try:
            # Generate personalized email content
            email_data = self.template_manager.generate_personalized_email(
                evaluation_result, candidate_info, job_info, company_info
            )
            
            # Create email message
            message = EmailMessage(
                to_email=email_data['to_email'],
                to_name=email_data['to_name'],
                subject=email_data['subject'],
                html_content=email_data['html_content'],
                text_content=email_data['text_content'],
                template_name=email_data['template_used'],
                template_context={
                    'evaluation_result': evaluation_result,
                    'candidate_info': candidate_info,
                    'job_info': job_info,
                    'company_info': company_info or {}
                }
            )
            
            # Send email
            result = self.send_email(message)
            
            return {
                **result,
                'relevance_score': email_data['relevance_score'],
                'template_used': email_data['template_used']
            }
            
        except Exception as e:
            logger.error(f"Error sending evaluation email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get status of sent email"""
        if message_id in self.sent_emails:
            message = self.sent_emails[message_id]
            return {
                'message_id': message_id,
                'status': message.status.value,
                'sent_at': message.sent_at,
                'to_email': message.to_email
            }
        elif message_id in self.failed_emails:
            message = self.failed_emails[message_id]
            return {
                'message_id': message_id,
                'status': message.status.value,
                'error': message.last_error,
                'attempts': message.attempts,
                'to_email': message.to_email
            }
        else:
            return {
                'message_id': message_id,
                'status': 'unknown'
            }

# Global email sender instance
email_sender = EmailSender()
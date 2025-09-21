#!/usr/bin/env python3
"""
Email System Demonstration

This script demonstrates the complete email functionality of the Resume 
Relevance System, including configuration, sending evaluation emails,
and tracking delivery status.

Features demonstrated:
- Email service configuration (SMTP, SendGrid, AWS SES)
- Personalized evaluation emails with templates
- Email queue management and retry logic
- Delivery tracking and analytics
- Template customization and preview
- Integration with evaluation system

Usage:
    python demo_email_system.py [--config] [--send-test] [--send-evaluation] [--stats]

Author: Automated Resume Relevance System
Version: 1.0.0
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.email_config import EmailConfig, EmailProvider, email_config
from app.utils.email_sender import email_sender, EmailMessage, EmailStatus
from app.utils.email_templates import email_templates


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def demonstrate_email_configuration():
    """Demonstrate email service configuration"""
    print_section("EMAIL SERVICE CONFIGURATION")
    
    # Show current configuration
    current_config = email_config.get_config()
    print(f"✓ Current Provider: {current_config.provider.value}")
    print(f"✓ Sender Email: {current_config.sender_email}")
    print(f"✓ Service Enabled: {current_config.enabled}")
    print(f"✓ Max Emails/Hour: {current_config.max_emails_per_hour}")
    
    # Demonstrate different provider configurations
    print("\n📧 Available Email Providers:")
    print("  1. SMTP (Generic email servers)")
    print("  2. SendGrid (Cloud email service)")
    print("  3. AWS SES (Amazon Simple Email Service)")
    print("  4. Mailgun (Email API service)")
    print("  5. Outlook (Microsoft email service)")
    
    # Example SMTP configuration
    print("\n📋 Example SMTP Configuration:")
    smtp_config = EmailConfig(
        enabled=True,
        provider=EmailProvider.SMTP,
        sender_email="hr@company.com",
        sender_name="HR Department",
        reply_to="noreply@company.com",
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="your-email@gmail.com",
        smtp_password="your-app-password",
        smtp_use_tls=True
    )
    
    print(f"  Provider: {smtp_config.provider.value}")
    print(f"  Server: {smtp_config.smtp_server}:{smtp_config.smtp_port}")
    print(f"  Security: {'TLS' if smtp_config.smtp_use_tls else 'SSL' if smtp_config.smtp_use_ssl else 'None'}")
    print(f"  Rate Limits: {smtp_config.max_emails_per_hour}/hour, {smtp_config.max_emails_per_day}/day")
    
    # Test configuration validation
    validation = email_config.validate_config(smtp_config)
    print(f"\n🔍 Configuration Valid: {'✅' if validation['valid'] else '❌'}")
    if not validation['valid']:
        print(f"  Error: {validation['error']}")


def demonstrate_email_templates():
    """Demonstrate email template system"""
    print_section("EMAIL TEMPLATE SYSTEM")
    
    # Show available templates
    templates = email_templates.get_available_templates()
    print(f"✓ Available Templates: {len(templates)}")
    for template in templates:
        print(f"  • {template}")
    
    # Create sample evaluation data
    sample_evaluation = {
        'relevance_score': 87.5,
        'matched_skills': ['Python', 'Flask', 'Machine Learning', 'REST APIs'],
        'missing_skills': ['Docker', 'Kubernetes', 'AWS'],
        'skill_match_percentage': 87.5,
        'experience_match': True,
        'education_match': True,
        'overall_feedback': 'Strong technical background with relevant experience in web development and ML.',
        'strengths': [
            'Excellent Python programming skills',
            'Solid experience with web frameworks',
            'Good understanding of ML concepts'
        ],
        'recommendations': [
            'Consider learning containerization technologies',
            'Explore cloud platforms for deployment',
            'Strengthen DevOps knowledge'
        ]
    }
    
    sample_candidate = {
        'name': 'Alice Johnson',
        'email': 'alice.johnson@example.com',
        'phone': '+1 (555) 987-6543',
        'linkedin': 'https://linkedin.com/in/alicejohnson'
    }
    
    sample_job = {
        'title': 'Senior Python Developer',
        'company': 'Tech Innovations Inc.',
        'location': 'San Francisco, CA',
        'employment_type': 'Full-time',
        'description': 'We are seeking a Senior Python Developer to join our growing team...',
        'salary_range': '$120,000 - $150,000',
        'application_deadline': '2024-02-15'
    }
    
    sample_company = {
        'name': 'Tech Innovations Inc.',
        'website': 'https://techinnovations.com',
        'description': 'Leading technology company focused on AI and automation solutions.'
    }
    
    # Generate personalized email
    print("\n📝 Generating Personalized Email:")
    email_data = email_templates.generate_personalized_email(
        sample_evaluation, sample_candidate, sample_job, sample_company
    )
    
    print(f"  Template Used: {email_data['template_used']}")
    print(f"  Subject: {email_data['subject']}")
    print(f"  To: {email_data['to_name']} <{email_data['to_email']}>")
    print(f"  Relevance Score: {email_data['relevance_score']:.1f}%")
    
    # Show email content preview
    print(f"\n📋 Email Content Preview:")
    print(f"  HTML Length: {len(email_data['html_content'])} characters")
    print(f"  Text Length: {len(email_data['text_content'])} characters")
    print(f"  Contains Skills: {'✅' if 'Python' in email_data['html_content'] else '❌'}")
    print(f"  Contains Score: {'✅' if '87.5' in email_data['html_content'] else '❌'}")


def send_test_email(recipient_email: str = "test@example.com"):
    """Send a test email"""
    print_section("SENDING TEST EMAIL")
    
    print(f"📧 Sending test email to: {recipient_email}")
    
    # Create test message
    test_message = EmailMessage(
        to_email=recipient_email,
        to_name="Test Recipient",
        subject="Resume Analysis System - Test Email",
        html_content="""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Email System Test</h2>
            <p>This is a test email from the Resume Analysis System.</p>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #27ae60;">
                <strong>🎉 Success!</strong><br>
                Your email configuration is working correctly.
            </div>
            <p><strong>System Information:</strong></p>
            <ul>
                <li>Provider: {provider}</li>
                <li>Test Time: {timestamp}</li>
                <li>Message ID: {message_id}</li>
            </ul>
            <p>Best regards,<br><strong>Resume Analysis System</strong></p>
        </div>
        """.format(
            provider=email_config.get_config().provider.value,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message_id="test-" + str(datetime.now().timestamp())
        ),
        text_content=f"""
Email System Test

This is a test email from the Resume Analysis System.

Success! Your email configuration is working correctly.

System Information:
- Provider: {email_config.get_config().provider.value}
- Test Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
Resume Analysis System
        """
    )
    
    # Send email
    if not email_config.get_config().enabled:
        print("❌ Email service is disabled")
        print("   Enable email service in configuration to send test email")
        return
    
    result = email_sender.send_email(test_message, immediate=True)
    
    if result['success']:
        print("✅ Test email sent successfully!")
        print(f"   Message ID: {result['message_id']}")
    else:
        print("❌ Failed to send test email")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    return result


def send_evaluation_email():
    """Send a sample evaluation email"""
    print_section("SENDING EVALUATION EMAIL")
    
    # Sample evaluation data
    evaluation_result = {
        'id': 'eval_' + str(int(datetime.now().timestamp())),
        'relevance_score': 92.3,
        'matched_skills': ['Python', 'Machine Learning', 'Flask', 'PostgreSQL', 'Git'],
        'missing_skills': ['Docker', 'Kubernetes', 'React'],
        'skill_match_percentage': 92.3,
        'experience_match': True,
        'education_match': True,
        'location_match': True,
        'overall_feedback': 'Excellent candidate with strong technical skills and relevant experience.',
        'strengths': [
            'Outstanding Python programming expertise',
            'Extensive experience with machine learning frameworks',
            'Proven track record in web development',
            'Strong database design skills'
        ],
        'recommendations': [
            'Consider learning containerization technologies (Docker)',
            'Explore frontend frameworks like React',
            'Investigate cloud deployment strategies'
        ]
    }
    
    candidate_info = {
        'name': 'Sarah Chen',
        'email': 'sarah.chen@example.com',
        'phone': '+1 (555) 234-5678',
        'linkedin': 'https://linkedin.com/in/sarahchen-dev'
    }
    
    job_info = {
        'title': 'Machine Learning Engineer',
        'company': 'AI Solutions Corp',
        'location': 'Seattle, WA',
        'employment_type': 'Full-time',
        'description': 'Join our AI team to build cutting-edge machine learning solutions...',
        'salary_range': '$130,000 - $160,000',
        'contact_email': 'hiring@aisolutions.com',
        'application_deadline': '2024-02-20'
    }
    
    company_info = {
        'name': 'AI Solutions Corp',
        'website': 'https://aisolutions.com',
        'description': 'Pioneer in artificial intelligence and machine learning technologies.',
        'benefits': ['Health insurance', 'Stock options', 'Flexible work hours', 'Learning budget']
    }
    
    print(f"📧 Sending evaluation email to: {candidate_info['name']} ({candidate_info['email']})")
    print(f"📊 Relevance Score: {evaluation_result['relevance_score']:.1f}%")
    print(f"💼 Position: {job_info['title']} at {job_info['company']}")
    
    if not email_config.get_config().enabled:
        print("❌ Email service is disabled")
        print("   Enable email service in configuration to send evaluation email")
        return
    
    # Send evaluation email
    result = email_sender.send_evaluation_email(
        evaluation_result=evaluation_result,
        candidate_info=candidate_info,
        job_info=job_info,
        company_info=company_info
    )
    
    if result['success']:
        print("✅ Evaluation email sent successfully!")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Template Used: {result.get('template_used', 'N/A')}")
        print(f"   Relevance Score: {result.get('relevance_score', 'N/A')}")
    else:
        print("❌ Failed to send evaluation email")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    return result


def show_email_statistics():
    """Display email sending statistics"""
    print_section("EMAIL STATISTICS")
    
    # Get queue status
    queue_size = email_sender.email_queue.qsize()
    processing_active = email_sender.is_processing
    
    print(f"📊 Email Queue Status:")
    print(f"   Queue Size: {queue_size} emails")
    print(f"   Processing Active: {'✅ Yes' if processing_active else '❌ No'}")
    
    # Get sent/failed email counts
    sent_count = len(email_sender.sent_emails)
    failed_count = len(email_sender.failed_emails)
    
    print(f"\n📈 Email Delivery Stats:")
    print(f"   Successfully Sent: {sent_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Success Rate: {(sent_count / (sent_count + failed_count) * 100):.1f}%" if (sent_count + failed_count) > 0 else "   Success Rate: N/A")
    
    # Show rate limiter status
    rate_limiter = email_sender.rate_limiter
    print(f"\n⏱️  Rate Limiter Status:")
    print(f"   Hourly Count: {rate_limiter.hourly_count}/{rate_limiter.max_per_hour}")
    print(f"   Daily Count: {rate_limiter.daily_count}/{rate_limiter.max_per_day}")
    print(f"   Can Send: {'✅ Yes' if rate_limiter.can_send() else '❌ No (rate limited)'}")
    
    # Show recent emails (if any)
    if email_sender.sent_emails:
        print(f"\n📧 Recent Sent Emails:")
        recent_emails = list(email_sender.sent_emails.values())[-3:]  # Last 3
        for email in recent_emails:
            print(f"   • {email.to_email} - {email.subject[:50]}...")
            print(f"     Sent: {email.sent_at.strftime('%Y-%m-%d %H:%M:%S') if email.sent_at else 'Pending'}")


def demonstrate_email_tracking():
    """Demonstrate email tracking capabilities"""
    print_section("EMAIL TRACKING DEMONSTRATION")
    
    if not email_sender.sent_emails and not email_sender.failed_emails:
        print("📭 No emails have been sent yet.")
        print("   Send a test email first to see tracking information.")
        return
    
    print(f"🔍 Email Tracking Information:")
    
    # Show sent emails
    if email_sender.sent_emails:
        print(f"\n✅ Successfully Sent Emails ({len(email_sender.sent_emails)}):")
        for message_id, email in email_sender.sent_emails.items():
            status = email_sender.get_email_status(message_id)
            print(f"   📧 {message_id[:8]}...")
            print(f"      To: {status['to_email']}")
            print(f"      Status: {status['status']}")
            print(f"      Sent: {status.get('sent_at', 'N/A')}")
    
    # Show failed emails
    if email_sender.failed_emails:
        print(f"\n❌ Failed Emails ({len(email_sender.failed_emails)}):")
        for message_id, email in email_sender.failed_emails.items():
            status = email_sender.get_email_status(message_id)
            print(f"   📧 {message_id[:8]}...")
            print(f"      To: {status['to_email']}")
            print(f"      Status: {status['status']}")
            print(f"      Attempts: {status.get('attempts', 0)}")
            print(f"      Error: {status.get('error', 'N/A')}")


def main():
    """Main demonstration function"""
    parser = argparse.ArgumentParser(description='Email System Demonstration')
    parser.add_argument('--config', action='store_true', help='Show email configuration')
    parser.add_argument('--templates', action='store_true', help='Demonstrate email templates')
    parser.add_argument('--send-test', type=str, help='Send test email to specified address')
    parser.add_argument('--send-evaluation', action='store_true', help='Send sample evaluation email')
    parser.add_argument('--stats', action='store_true', help='Show email statistics')
    parser.add_argument('--tracking', action='store_true', help='Show email tracking information')
    parser.add_argument('--all', action='store_true', help='Run all demonstrations')
    
    args = parser.parse_args()
    
    print("🚀 Resume Relevance System - Email Functionality Demo")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if args.all or args.config:
            demonstrate_email_configuration()
        
        if args.all or args.templates:
            demonstrate_email_templates()
        
        if args.send_test:
            send_test_email(args.send_test)
        
        if args.all or args.send_evaluation:
            send_evaluation_email()
        
        if args.all or args.stats:
            show_email_statistics()
        
        if args.all or args.tracking:
            demonstrate_email_tracking()
        
        if not any(vars(args).values()):
            print("\n📚 Available Options:")
            print("   --config          Show email configuration")
            print("   --templates       Demonstrate email templates") 
            print("   --send-test EMAIL Send test email")
            print("   --send-evaluation Send sample evaluation email")
            print("   --stats           Show email statistics")
            print("   --tracking        Show email tracking")
            print("   --all             Run all demonstrations")
            print("\nExample: python demo_email_system.py --all")
            print("Example: python demo_email_system.py --send-test your-email@example.com")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    print(f"\n✅ Email system demonstration completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
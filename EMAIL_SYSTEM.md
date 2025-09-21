# Email Automation System

## Overview

The Resume Relevance System includes a comprehensive email automation module that sends personalized evaluation emails to candidates after their resumes are processed. This system supports multiple email providers, includes professional templates, and provides delivery tracking and analytics.

## Features

### ✅ Multi-Provider Support

- **SMTP**: Generic email servers (Gmail, Outlook, etc.)
- **SendGrid**: Cloud-based email delivery service
- **AWS SES**: Amazon Simple Email Service
- **Mailgun**: Email API service (configurable)
- **Outlook**: Microsoft email service (configurable)

### ✅ Professional Email Templates

- **High Relevance (90-100%)**: Congratulatory tone with next steps
- **Medium Relevance (60-89%)**: Encouraging tone with improvement suggestions
- **Low Relevance (<60%)**: Constructive feedback with skill recommendations

### ✅ Advanced Features

- **Queue Management**: Background processing with retry logic
- **Rate Limiting**: Configurable hourly/daily email limits
- **Delivery Tracking**: Status monitoring and analytics
- **Personalization**: Dynamic content based on evaluation results
- **Template Engine**: Jinja2-powered flexible templating
- **HTML & Text**: Responsive HTML emails with text fallbacks

## Quick Start

### 1. Configuration

Configure your email service in environment variables or programmatically:

```python
from app.utils.email_config import EmailConfig, EmailProvider, email_config

# SMTP Configuration (Gmail example)
config = EmailConfig(
    enabled=True,
    provider=EmailProvider.SMTP,
    sender_email="your-email@gmail.com",
    sender_name="HR Department",
    reply_to="noreply@company.com",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="your-app-password",  # Use App Password for Gmail
    smtp_use_tls=True,
    max_emails_per_hour=100,
    max_emails_per_day=1000
)

# Update configuration
email_config.update_config(config)
```

### 2. Send Evaluation Email

```python
from app.utils.email_sender import email_sender

# Evaluation data from your resume analysis
evaluation_result = {
    'relevance_score': 85.5,
    'matched_skills': ['Python', 'Machine Learning', 'Flask'],
    'missing_skills': ['Docker', 'Kubernetes'],
    'overall_feedback': 'Strong technical background...'
}

candidate_info = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'phone': '+1 (555) 123-4567'
}

job_info = {
    'title': 'Senior Python Developer',
    'company': 'Tech Company Inc.',
    'location': 'San Francisco, CA'
}

# Send personalized email
result = email_sender.send_evaluation_email(
    evaluation_result=evaluation_result,
    candidate_info=candidate_info,
    job_info=job_info
)

print(f"Email sent: {result['success']}")
print(f"Message ID: {result['message_id']}")
```

### 3. API Integration

```bash
# Send evaluation email via API
curl -X POST http://localhost:5000/api/email/send-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "eval_123",
    "candidate_email": "candidate@example.com",
    "candidate_name": "Jane Smith",
    "company_name": "Your Company"
  }'

# Check email status
curl http://localhost:5000/api/email/status/message_id_here

# Get email statistics
curl http://localhost:5000/api/email/stats
```

## Configuration Guide

### Environment Variables

```bash
# Email Service Settings
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
EMAIL_SENDER_EMAIL=your-email@company.com
EMAIL_SENDER_NAME="HR Department"
EMAIL_REPLY_TO=noreply@company.com

# SMTP Settings (for SMTP provider)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# SendGrid Settings (for SendGrid provider)
SENDGRID_API_KEY=your_sendgrid_api_key

# AWS SES Settings (for AWS SES provider)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Rate Limiting
EMAIL_MAX_PER_HOUR=100
EMAIL_MAX_PER_DAY=1000

# Retry Settings
EMAIL_RETRY_ATTEMPTS=3
EMAIL_RETRY_DELAY=60
```

### Provider-Specific Setup

#### Gmail (SMTP)

1. Enable 2-Factor Authentication
2. Generate App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Use App Password instead of regular password

#### SendGrid

1. Create SendGrid account: [SendGrid](https://sendgrid.com)
2. Generate API Key in dashboard
3. Verify sender identity

#### AWS SES

1. Set up AWS SES in AWS Console
2. Verify email addresses/domains
3. Request production access (if needed)
4. Configure IAM user with SES permissions

## Email Templates

### Template Structure

Templates are located in `templates/emails/` and include:

- `high_relevance.html`: For scores 90-100%
- `medium_relevance.html`: For scores 60-89%
- `low_relevance.html`: For scores below 60%

### Customization

Templates use Jinja2 syntax and receive these variables:

```python
{
    'candidate': {
        'name': 'John Doe',
        'email': 'john@example.com'
    },
    'job': {
        'title': 'Python Developer',
        'company': 'Tech Corp',
        'location': 'San Francisco'
    },
    'evaluation': {
        'relevance_score': 85.5,
        'matched_skills': ['Python', 'Flask'],
        'missing_skills': ['Docker'],
        'strengths': ['Strong Python skills'],
        'recommendations': ['Learn containerization']
    },
    'company': {
        'name': 'Tech Corp',
        'website': 'https://techcorp.com'
    }
}
```

### Example Template Usage

```html
<h2>Hi {{ candidate.name }}!</h2>
<p>
  Your application for <strong>{{ job.title }}</strong> at {{ job.company }} has
  been evaluated.
</p>

<div class="score-section">
  <h3>Your Relevance Score: {{ evaluation.relevance_score }}%</h3>
</div>

<div class="skills-section">
  <h4>Matched Skills:</h4>
  <ul>
    {% for skill in evaluation.matched_skills %}
    <li>{{ skill }}</li>
    {% endfor %}
  </ul>
</div>
```

## API Reference

### Send Evaluation Email

```http
POST /api/email/send-evaluation
Content-Type: application/json

{
    "evaluation_id": "eval_123",
    "candidate_email": "candidate@example.com",
    "candidate_name": "John Doe",
    "company_name": "Tech Corp",
    "job_location": "Remote",
    "salary_range": "$80k-$120k"
}
```

### Send Custom Email

```http
POST /api/email/send-custom
Content-Type: application/json

{
    "to_email": "recipient@example.com",
    "subject": "Custom Subject",
    "html_content": "<h1>Hello!</h1>",
    "immediate": true
}
```

### Get Email Status

```http
GET /api/email/status/{message_id}
```

### Email Configuration

```http
GET /api/email/config
POST /api/email/config
```

### Test Email

```http
POST /api/email/test
Content-Type: application/json

{
    "test_email": "test@example.com"
}
```

### Email Statistics

```http
GET /api/email/stats?start_date=2024-01-01&end_date=2024-02-01
```

### Email History

```http
GET /api/email/history?page=1&per_page=20&status=sent
```

## Database Schema

### EmailRecord Table

```sql
CREATE TABLE email_records (
    id VARCHAR(36) PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    evaluation_id VARCHAR(36),
    candidate_email VARCHAR(255) NOT NULL,
    candidate_name VARCHAR(255),
    subject TEXT NOT NULL,
    template_used VARCHAR(100),
    relevance_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    email_provider VARCHAR(50),
    provider_message_id VARCHAR(255),
    email_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### Common Issues

1. **Authentication Errors**

   - Verify credentials and API keys
   - Check provider-specific authentication methods

2. **Rate Limiting**

   - Monitor email quotas
   - Adjust rate limits in configuration

3. **Template Errors**

   - Validate Jinja2 syntax
   - Ensure all required variables are provided

4. **Delivery Failures**
   - Check recipient email addresses
   - Monitor bounce rates and spam reports

### Retry Logic

The system automatically retries failed emails with exponential backoff:

- Maximum retries: 3 (configurable)
- Retry delay: 60 seconds \* attempt number
- Automatic queue management

## Monitoring & Analytics

### Email Statistics

Track email performance with built-in analytics:

- Total emails sent/failed
- Delivery success rates
- Template usage statistics
- Daily/hourly sending patterns
- Provider performance metrics

### Logging

Email operations are logged with appropriate levels:

```python
import logging
logger = logging.getLogger('email_system')
logger.setLevel(logging.INFO)
```

Log events include:

- Email sent/failed
- Configuration changes
- Rate limit hits
- Template rendering errors

## Security Considerations

### Best Practices

1. **Credential Storage**

   - Use environment variables
   - Never commit credentials to version control
   - Use secure credential management services

2. **Email Content**

   - Sanitize user input in templates
   - Validate email addresses
   - Implement unsubscribe mechanisms

3. **Rate Limiting**

   - Prevent abuse with rate limits
   - Monitor sending patterns
   - Implement IP-based restrictions if needed

4. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for API endpoints
   - Implement proper access controls

## Demo Script

Run the comprehensive demo to test all functionality:

```bash
# Show all features
python demo_email_system.py --all

# Test specific features
python demo_email_system.py --config
python demo_email_system.py --templates
python demo_email_system.py --send-test your-email@example.com
python demo_email_system.py --stats
```

## Troubleshooting

### Gmail SMTP Issues

- Enable 2FA and use App Password
- Allow less secure apps (not recommended)
- Check Gmail SMTP settings

### SendGrid Issues

- Verify API key permissions
- Complete sender authentication
- Check domain verification

### AWS SES Issues

- Verify email addresses in SES console
- Request production access for higher limits
- Configure proper IAM permissions

### Template Issues

- Validate Jinja2 syntax
- Check variable names and structure
- Test templates with sample data

## Integration Examples

### With Flask Route

```python
@app.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.get_json()

    result = email_sender.send_evaluation_email(
        evaluation_result=data['evaluation'],
        candidate_info=data['candidate'],
        job_info=data['job']
    )

    return jsonify(result)
```

### With Background Task

```python
from celery import Celery

@celery.task
def send_async_email(evaluation_data, candidate_data, job_data):
    return email_sender.send_evaluation_email(
        evaluation_result=evaluation_data,
        candidate_info=candidate_data,
        job_info=job_data
    )
```

### With Scheduled Jobs

```python
import schedule
import time

def send_daily_reports():
    # Get pending evaluations
    evaluations = get_pending_evaluations()

    for eval_data in evaluations:
        email_sender.send_evaluation_email(**eval_data)

schedule.every().day.at("09:00").do(send_daily_reports)
```

## Contributing

To extend the email system:

1. Add new providers in `email_config.py`
2. Implement sender methods in `email_sender.py`
3. Create new templates in `templates/emails/`
4. Add API routes in `email_routes.py`
5. Update database schema if needed

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review logs for error details
3. Test with demo script
4. Validate configuration settings

---

**Resume Relevance System Email Module**  
Version: 1.0.0  
Author: Automated Resume Relevance System  
Last Updated: 2024

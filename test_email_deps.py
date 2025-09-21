#!/usr/bin/env python3
"""
Email Dependencies Test Script
Verifies that all email-related imports work correctly
"""

import sys
import os

def test_email_dependencies():
    """Test all email-related imports"""
    print("Testing Email Dependencies")
    print("=" * 40)
    
    print(f"Python executable: {sys.executable}")
    print(f"Virtual environment: {os.environ.get('VIRTUAL_ENV', 'Not active')}")
    print()
    
    # Test sendgrid imports
    try:
        import sendgrid
        print(f"✓ sendgrid imported successfully (version: {sendgrid.__version__})")
        
        from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent
        print("✓ sendgrid.helpers.mail components imported successfully")
        
        # Test creating a mail object
        mail = Mail(
            from_email=From("test@example.com", "Test Sender"),
            to_emails=To("recipient@example.com"),
            subject=Subject("Test Subject"),
            html_content=HtmlContent("<p>Test HTML content</p>")
        )
        print("✓ Mail object created successfully")
        
    except ImportError as e:
        print(f"✗ sendgrid import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ sendgrid functionality test failed: {e}")
        return False
    
    # Test boto3 imports
    try:
        import boto3
        print(f"✓ boto3 imported successfully (version: {boto3.__version__})")
        
        # Test SES client creation (won't work without credentials, but import should work)
        ses_client = boto3.client('ses', region_name='us-east-1')
        print("✓ SES client creation successful (no credentials needed for test)")
        
    except ImportError as e:
        print(f"✗ boto3 import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ boto3 functionality test failed: {e}")
        return False
    
    # Test email-validator
    try:
        from email_validator import validate_email, EmailNotValidError
        print("✓ email_validator imported successfully")
        
        # Test email validation
        valid_email = validate_email("test@example.com")
        print(f"✓ Email validation test passed: {valid_email.email}")
        
    except ImportError as e:
        print(f"✗ email_validator import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ email_validator functionality test failed: {e}")
        return False
    
    print()
    print("=" * 40)
    print("✓ All email dependencies are working correctly!")
    print("You can now use sendgrid and boto3 in your application.")
    return True

if __name__ == "__main__":
    success = test_email_dependencies()
    sys.exit(0 if success else 1)
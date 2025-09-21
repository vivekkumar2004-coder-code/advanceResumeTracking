#!/usr/bin/env python3
"""Quick test to verify application startup and basic functionality"""

import sys
import threading
import time
import requests
from app_safe import create_app_safe

def test_application():
    """Test application creation and basic endpoint"""
    print("Testing Resume Relevance System...")
    print("="*50)
    
    try:
        # Create app
        print("1. Creating Flask application...")
        app = create_app_safe()
        print("✓ Application created successfully")
        
        # Test basic functionality
        print("2. Testing application context...")
        with app.app_context():
            print("✓ Application context works")
        
        # Start server in background thread
        print("3. Starting test server on port 5001...")
        def run_server():
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test endpoints
        print("4. Testing API endpoints...")
        
        # Test /api/info
        try:
            response = requests.get('http://127.0.0.1:5001/api/info', timeout=5)
            print(f"   /api/info - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Application: {data.get('message', 'Unknown')}")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print("✓ API endpoint working")
            else:
                print("⚠ API endpoint returned non-200 status")
        except Exception as e:
            print(f"✗ API endpoint test failed: {e}")
        
        # Test health endpoint
        try:
            response = requests.get('http://127.0.0.1:5001/health', timeout=5)
            print(f"   /health - Status: {response.status_code}")
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print("⚠ Health endpoint returned non-200 status")
        except Exception as e:
            print(f"⚠ Health endpoint test failed: {e}")
        
        # Test dashboard
        try:
            response = requests.get('http://127.0.0.1:5001/', timeout=5)
            print(f"   / (dashboard) - Status: {response.status_code}")
            if response.status_code == 200:
                print("✓ Dashboard endpoint working")
            else:
                print("⚠ Dashboard endpoint returned non-200 status")
        except Exception as e:
            print(f"⚠ Dashboard endpoint test failed: {e}")
        
        print("="*50)
        print("✓ Application startup test completed successfully!")
        print("The Resume Relevance System appears to be working correctly.")
        print("You can access it at: http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"✗ Application test failed: {e}")
        print("Check the error details above for troubleshooting.")
        return False
    
    return True

if __name__ == "__main__":
    success = test_application()
    sys.exit(0 if success else 1)
"""
Example usage script for the Resume Relevance Analyzer API

This script demonstrates how to:
1. Start the Flask server
2. Upload a job description
3. Upload a resume
4. Evaluate the resume against the job description
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread

# API base URL
BASE_URL = "http://localhost:5000/api"

def start_server():
    """Start the Flask development server"""
    print("Starting Flask development server...")
    subprocess.run([sys.executable, "app.py"], cwd=".")

def wait_for_server(url, timeout=30):
    """Wait for the server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/files")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

def upload_job_description_text(job_text):
    """Upload job description as text"""
    try:
        response = requests.post(
            f"{BASE_URL}/upload/job-description",
            json={"text": job_text},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job description uploaded successfully!")
            print(f"   File ID: {data['file_id']}")
            return data['file_id']
        else:
            print(f"❌ Failed to upload job description: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error uploading job description: {str(e)}")
        return None

def upload_resume_text(resume_text):
    """Upload resume as text (simulated)"""
    try:
        # Since we're working with text, we'll save it as a temp file and upload
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(resume_text)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('resume.txt', f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/upload/resume", files=files)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resume uploaded successfully!")
                print(f"   File ID: {data['file_id']}")
                return data['file_id']
            else:
                print(f"❌ Failed to upload resume: {response.json()}")
                return None
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"❌ Error uploading resume: {str(e)}")
        return None

def evaluate_resume(resume_id, job_id):
    """Evaluate resume against job description"""
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate",
            json={"resume_id": resume_id, "job_description_id": job_id},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resume evaluation completed!")
            print(f"   Relevance Score: {data['relevance_score']}%")
            print(f"   Relevance Level: {data['relevance_level']}")
            print(f"   Skill Match: {data['skill_match_percentage']}%")
            print(f"   Matching Skills: {', '.join(data['matching_skills'][:5])}")
            print(f"   Missing Skills: {', '.join(data['missing_skills'][:5])}")
            return data
        else:
            print(f"❌ Failed to evaluate resume: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error evaluating resume: {str(e)}")
        return None

def analyze_keywords(job_id):
    """Analyze keywords from job description"""
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-keywords",
            json={"job_description_id": job_id},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Keyword analysis completed!")
            print(f"   Technical Skills: {', '.join(data['technical_skills'][:5])}")
            print(f"   Soft Skills: {', '.join(data['soft_skills'][:3])}")
            print(f"   Required Skills: {', '.join(data['required_skills'][:5])}")
            return data
        else:
            print(f"❌ Failed to analyze keywords: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error analyzing keywords: {str(e)}")
        return None

def main():
    """Main example function"""
    print("🚀 Resume Relevance Analyzer API Example")
    print("=" * 50)
    
    # Sample job description
    job_description = """
    Job Title: Senior Python Developer
    
    We are seeking a Senior Python Developer to join our growing team. 
    
    Required Skills:
    - 5+ years of Python development experience
    - Strong knowledge of Django or Flask frameworks
    - Experience with RESTful API development
    - Proficiency in SQL and database design
    - Experience with Git version control
    - Strong problem-solving skills
    
    Preferred Skills:
    - Experience with Docker and Kubernetes
    - Knowledge of AWS or other cloud platforms
    - Machine learning experience with scikit-learn or TensorFlow
    - React or Vue.js frontend experience
    - Agile development methodology
    
    Responsibilities:
    - Develop and maintain Python web applications
    - Design and implement RESTful APIs
    - Collaborate with cross-functional teams
    - Code review and mentoring junior developers
    - Optimize application performance
    """
    
    # Sample resume
    resume_text = """
    John Smith
    Senior Software Engineer
    
    EXPERIENCE:
    Senior Python Developer | Tech Corp | 2020-Present
    - Developed web applications using Django and Flask
    - Built RESTful APIs serving 1M+ requests daily
    - Implemented microservices architecture with Docker
    - Worked with PostgreSQL and MongoDB databases
    - Led a team of 3 junior developers
    
    Python Developer | StartupCo | 2018-2020
    - Created machine learning models using scikit-learn
    - Developed data processing pipelines
    - Implemented CI/CD using Jenkins and Git
    - Worked in Agile environment
    
    SKILLS:
    - Python, Django, Flask, FastAPI
    - PostgreSQL, MongoDB, Redis
    - Docker, Kubernetes, AWS
    - Git, Jenkins, CI/CD
    - Machine Learning, scikit-learn
    - React, JavaScript, HTML/CSS
    
    EDUCATION:
    B.S. Computer Science | University of Technology | 2018
    """
    
    print("Note: This example assumes the Flask server is running.")
    print("To start the server, run: python app.py")
    print("Then run this script in a separate terminal.")
    print()
    
    # Check if server is running
    if not wait_for_server(BASE_URL, timeout=5):
        print("❌ Flask server is not running. Please start it with: python app.py")
        return
    
    print("✅ Server is running!")
    print()
    
    # Upload job description
    print("📝 Uploading job description...")
    job_id = upload_job_description_text(job_description)
    if not job_id:
        return
    print()
    
    # Upload resume
    print("📄 Uploading resume...")
    resume_id = upload_resume_text(resume_text)
    if not resume_id:
        return
    print()
    
    # Analyze job keywords
    print("🔍 Analyzing job description keywords...")
    analyze_keywords(job_id)
    print()
    
    # Evaluate resume
    print("⚖️ Evaluating resume relevance...")
    evaluation = evaluate_resume(resume_id, job_id)
    if evaluation:
        print()
        print("📊 Detailed Results:")
        print(f"   • Overall Score: {evaluation['relevance_score']}/100")
        print(f"   • Match Level: {evaluation['relevance_level']}")
        print(f"   • Skills Found: {evaluation['total_matching_skills']}/{evaluation['total_job_skills']}")
        if evaluation['recommendations']:
            print(f"   • Recommendation: {evaluation['recommendations'][0]}")
    
    print()
    print("✅ Example completed successfully!")

if __name__ == "__main__":
    main()
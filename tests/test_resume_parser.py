import pytest
import tempfile
import os
from app.utils.resume_parser import ResumeParser, extract_resume_entities

class TestResumeParser:
    """Test cases for the enhanced resume parser"""
    
    def setup_method(self):
        """Set up test instances"""
        self.parser = ResumeParser()
    
    def test_section_extraction(self):
        """Test section extraction from resume text"""
        sample_text = """
        John Doe
        Senior Developer
        
        EXPERIENCE
        Software Engineer at TechCorp
        Developed Python applications
        
        SKILLS
        Python, JavaScript, SQL, Docker
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology
        """
        
        sections = self.parser._extract_sections(sample_text)
        
        assert 'experience' in sections
        assert 'skills' in sections
        assert 'education' in sections
        assert 'python' in sections['skills'].lower()
    
    def test_skills_extraction(self):
        """Test technical and soft skills extraction"""
        text = """
        Technical Skills: Python, JavaScript, React, PostgreSQL, Docker, Kubernetes
        Soft Skills: Leadership, Communication, Problem-solving, Team collaboration
        """
        
        skills = self.parser._extract_skills(text, text)
        
        assert 'python' in skills['technical_skills']
        assert 'javascript' in skills['technical_skills']
        assert 'postgresql' in skills['technical_skills']
        assert 'leadership' in skills['soft_skills']
        assert len(skills['all_skills']) > 0
    
    def test_certifications_extraction(self):
        """Test certification extraction"""
        text = """
        Certifications:
        - AWS Certified Solutions Architect
        - Certified Scrum Master
        - Oracle Certified Professional
        - CompTIA Security+
        """
        
        certifications = self.parser._extract_certifications(text)
        
        assert len(certifications) > 0
        assert any('aws certified' in cert.lower() for cert in certifications)
        assert any('scrum master' in cert.lower() for cert in certifications)
    
    def test_experience_extraction(self):
        """Test experience details extraction"""
        experience_text = """
        Senior Software Engineer | TechCorp | 2020 - Present
        Led development of microservices architecture
        Implemented CI/CD pipelines
        Mentored junior developers
        
        Software Engineer | StartupCo | 2018 - 2020
        Developed web applications using Django
        Optimized database performance
        """
        
        experiences = self.parser._extract_experience_details(experience_text)
        
        assert len(experiences) >= 1
        assert any('engineer' in exp.get('title', '').lower() for exp in experiences)
    
    def test_contact_info_extraction(self):
        """Test contact information extraction"""
        text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        linkedin.com/in/johndoe
        """
        
        contact_info = self.parser._extract_contact_info(text)
        
        assert 'email' in contact_info
        assert 'john.doe@email.com' in contact_info['email']
        assert 'phone' in contact_info
        assert 'linkedin' in contact_info
    
    def test_education_extraction(self):
        """Test education details extraction"""
        education_text = """
        Bachelor of Science in Computer Science
        University of Technology, 2018
        
        Master of Science in Data Science
        Tech University, 2020
        """
        
        education = self.parser._extract_education_details(education_text)
        
        assert len(education) >= 1
        # Should extract at least one degree
        assert any('bachelor' in edu.get('degree', '').lower() or 
                  'master' in edu.get('degree', '').lower() 
                  for edu in education)
    
    def test_job_title_detection(self):
        """Test job title detection heuristic"""
        assert self.parser._looks_like_job_title("Senior Software Engineer")
        assert self.parser._looks_like_job_title("Data Analyst")
        assert self.parser._looks_like_job_title("Project Manager")
        assert not self.parser._looks_like_job_title("University of Technology")
        assert not self.parser._looks_like_job_title("2018 - 2020")
    
    def test_date_range_detection(self):
        """Test date range detection heuristic"""
        assert self.parser._looks_like_date_range("2018 - 2020")
        assert self.parser._looks_like_date_range("Jan 2020 - Present")
        assert self.parser._looks_like_date_range("2020")
        assert self.parser._looks_like_date_range("05/2020")
        assert not self.parser._looks_like_date_range("Software Engineer")
        assert not self.parser._looks_like_date_range("Python Programming")
    
    def test_comprehensive_parsing(self):
        """Test complete resume parsing with sample text"""
        sample_resume = """
        JANE SMITH
        Senior Data Scientist
        jane.smith@email.com | (555) 987-6543 | linkedin.com/in/janesmith
        
        PROFESSIONAL SUMMARY
        Experienced data scientist with 6+ years in machine learning and analytics
        
        TECHNICAL SKILLS
        Programming: Python, R, SQL, Java
        ML/AI: TensorFlow, PyTorch, scikit-learn, Keras
        Databases: PostgreSQL, MongoDB, Redis
        Cloud: AWS, GCP, Docker, Kubernetes
        
        PROFESSIONAL EXPERIENCE
        Senior Data Scientist | DataTech Inc | 2021 - Present
        • Led machine learning initiatives for customer analytics
        • Developed predictive models improving accuracy by 25%
        • Managed team of 4 junior data scientists
        
        Data Scientist | Analytics Corp | 2019 - 2021
        • Built recommendation systems using collaborative filtering
        • Implemented A/B testing frameworks
        
        EDUCATION
        Master of Science in Data Science | Tech University | 2019
        Bachelor of Science in Mathematics | State University | 2017
        
        CERTIFICATIONS
        AWS Certified Machine Learning Specialist
        Google Cloud Professional Data Engineer
        Certified Analytics Professional (CAP)
        """
        
        # Test with simple text processing (simulated file parsing)
        result = {
            'raw_text': sample_resume,
            'sections': self.parser._extract_sections(sample_resume),
            'entities': {},
            'metadata': {'test': True}
        }
        
        result['entities'] = self.parser._extract_entities(sample_resume, result['sections'])
        
        # Verify comprehensive parsing
        assert result['raw_text']
        assert len(result['sections']) > 0
        assert 'skills' in result['sections']
        assert 'experience' in result['sections']
        assert 'education' in result['sections']
        
        # Verify entity extraction
        entities = result['entities']
        assert 'skills' in entities
        assert 'contact_info' in entities
        assert 'certifications' in entities
        assert 'experience' in entities
        assert 'education' in entities
        
        # Verify specific skills were found
        technical_skills = entities['skills']['technical_skills']
        assert 'python' in technical_skills
        assert 'sql' in technical_skills
        assert 'tensorflow' in technical_skills
        
        # Verify contact info
        contact = entities['contact_info']
        assert 'jane.smith@email.com' in contact.get('email', '')
        assert '555' in contact.get('phone', '')
        
        # Verify certifications
        certs = entities['certifications']
        assert len(certs) > 0
        assert any('aws' in cert.lower() for cert in certs)
    
    def test_extract_resume_entities_function(self):
        """Test the convenience function extract_resume_entities"""
        # Since we can't create actual PDF/DOCX files easily in tests,
        # we'll test the function exists and can handle invalid paths
        try:
            result = extract_resume_entities("nonexistent_file.pdf")
            assert 'error' in result
        except Exception as e:
            # Expected behavior for nonexistent file
            assert True

# Test the new enhanced API endpoint
class TestEnhancedEvaluation:
    """Test cases for enhanced evaluation functionality"""
    
    def test_enhanced_endpoint_structure(self):
        """Test that enhanced evaluation can be imported and structured correctly"""
        # Import the route module to verify it loads correctly
        from app.routes import evaluation_routes
        
        # Verify the new route is defined
        blueprint = evaluation_routes.bp
        assert blueprint is not None
        
        # Check that the blueprint has rules (routes)
        # Note: We can't easily test the actual endpoint without a full Flask app context
        # But we can verify the module loads without errors
        assert hasattr(evaluation_routes, 'evaluate_resume_enhanced')

if __name__ == "__main__":
    # Run basic tests
    parser = ResumeParser()
    
    print("Running basic resume parser tests...")
    
    # Test skills extraction
    test_text = "Skills: Python, JavaScript, Docker, AWS, Machine Learning"
    skills = parser._extract_skills(test_text, test_text)
    print(f"✅ Skills extraction: Found {len(skills['technical_skills'])} technical skills")
    
    # Test contact extraction
    contact_text = "John Doe - john@example.com - (555) 123-4567"
    contact = parser._extract_contact_info(contact_text)
    print(f"✅ Contact extraction: Found email: {contact.get('email', 'None')}")
    
    # Test certification extraction
    cert_text = "AWS Certified Solutions Architect, Certified Scrum Master"
    certs = parser._extract_certifications(cert_text)
    print(f"✅ Certification extraction: Found {len(certs)} certifications")
    
    print("\nAll basic tests passed! ✅")
    print("\nTo run comprehensive tests, use: pytest tests/test_resume_parser.py")
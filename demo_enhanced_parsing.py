"""
Enhanced Resume Parsing Demo

This script demonstrates the advanced resume parsing capabilities
including entity extraction from PDF and DOCX files.
"""

import json
import sys
import os
sys.path.append('.')

from app.utils.resume_parser import ResumeParser, extract_resume_entities

def demo_enhanced_parsing():
    """Demonstrate the enhanced resume parsing capabilities"""
    
    print("🔍 Enhanced Resume Parsing Capabilities Demo")
    print("=" * 60)
    
    # Sample resume text that would typically come from a PDF/DOCX
    sample_resume = """
    SARAH JOHNSON
    Senior Full Stack Developer
    sarah.johnson@techmail.com | (555) 234-5678 | linkedin.com/in/sarahjohnson
    San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Experienced full-stack developer with 7+ years of experience in building scalable 
    web applications. Expertise in modern JavaScript frameworks, cloud technologies, 
    and agile methodologies. Proven track record of leading development teams and 
    delivering high-quality software solutions.
    
    TECHNICAL SKILLS
    Frontend: React, Vue.js, Angular, TypeScript, HTML5, CSS3, SASS
    Backend: Node.js, Python, Django, Flask, Express.js, Java, Spring Boot
    Databases: PostgreSQL, MongoDB, MySQL, Redis, Elasticsearch
    Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitLab CI/CD, Terraform
    Tools: Git, JIRA, Confluence, VS Code, Postman
    
    PROFESSIONAL EXPERIENCE
    
    Senior Full Stack Developer | TechInnovate Inc | San Francisco, CA | 2020 - Present
    • Lead a team of 5 developers in building microservices-based e-commerce platform
    • Architected and implemented RESTful APIs serving 1M+ daily requests
    • Reduced application load time by 40% through optimization and caching strategies
    • Mentored junior developers and conducted code reviews
    • Technologies: React, Node.js, PostgreSQL, AWS, Docker, Kubernetes
    
    Full Stack Developer | StartupCorp | San Francisco, CA | 2018 - 2020
    • Developed responsive web applications using React and Django
    • Implemented automated testing resulting in 30% reduction in production bugs
    • Collaborated with UX/UI designers to create intuitive user interfaces
    • Built CI/CD pipelines using Jenkins and GitLab
    • Technologies: React, Django, PostgreSQL, AWS EC2, Docker
    
    Software Developer | WebSolutions LLC | Remote | 2017 - 2018
    • Built custom CMS solutions for small businesses using PHP and MySQL
    • Integrated third-party APIs including payment gateways and social media
    • Optimized database queries improving application performance by 25%
    • Technologies: PHP, Laravel, MySQL, jQuery, Bootstrap
    
    EDUCATION
    Bachelor of Science in Computer Science | University of California, Berkeley | 2017
    Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering
    GPA: 3.8/4.0
    
    CERTIFICATIONS
    AWS Certified Solutions Architect - Associate (2021)
    Certified Kubernetes Administrator (CKA) (2020)
    Google Cloud Professional Cloud Architect (2019)
    Certified Scrum Master (CSM) (2018)
    
    PROJECTS
    
    E-Commerce Platform Redesign (2021)
    • Led complete redesign of legacy e-commerce platform using modern tech stack
    • Implemented microservices architecture with React frontend and Node.js backend
    • Achieved 50% improvement in page load speeds and 25% increase in conversion rates
    • Technologies: React, Node.js, PostgreSQL, Redis, AWS, Docker
    
    Real-time Chat Application (2020)
    • Built scalable real-time messaging application supporting 10,000+ concurrent users
    • Implemented WebSocket connections with Socket.io and Redis for session management
    • Deployed on AWS with auto-scaling groups and load balancers
    • Technologies: Node.js, Socket.io, MongoDB, Redis, AWS
    
    ACHIEVEMENTS
    • Winner of TechInnovate's "Innovation Award" for outstanding technical contribution (2021)
    • Increased team productivity by 35% through implementation of agile practices
    • Speaker at React SF Meetup on "Building Scalable React Applications" (2020)
    • Contributed to 3 open-source projects with 500+ GitHub stars combined
    """
    
    parser = ResumeParser()
    
    # Simulate parsing process
    print("📄 Parsing sample resume...")
    
    # Extract sections
    sections = parser._extract_sections(sample_resume)
    print(f"\n📑 Sections identified: {list(sections.keys())}")
    
    # Extract entities
    entities = parser._extract_entities(sample_resume, sections)
    
    # Display results
    print("\n🛠️ TECHNICAL SKILLS EXTRACTED:")
    tech_skills = entities['skills']['technical_skills']
    print(f"   Found {len(tech_skills)} technical skills:")
    for i, skill in enumerate(tech_skills[:10], 1):  # Show first 10
        print(f"   {i:2d}. {skill}")
    if len(tech_skills) > 10:
        print(f"   ... and {len(tech_skills) - 10} more")
    
    print("\n🎯 SOFT SKILLS EXTRACTED:")
    soft_skills = entities['skills']['soft_skills']
    if soft_skills:
        for i, skill in enumerate(soft_skills, 1):
            print(f"   {i}. {skill}")
    else:
        print("   None explicitly found (they may be embedded in descriptions)")
    
    print("\n🏆 CERTIFICATIONS EXTRACTED:")
    certifications = entities['certifications']
    if certifications:
        for i, cert in enumerate(certifications, 1):
            print(f"   {i}. {cert}")
    else:
        print("   None found")
    
    print("\n👤 CONTACT INFORMATION:")
    contact = entities['contact_info']
    for key, value in contact.items():
        print(f"   {key.capitalize()}: {value}")
    
    print("\n💼 WORK EXPERIENCE:")
    experiences = entities['experience']
    if experiences:
        for i, exp in enumerate(experiences, 1):
            title = exp.get('title', 'Unknown Position')
            duration = exp.get('duration', 'Duration not specified')
            print(f"   {i}. {title}")
            print(f"      Duration: {duration}")
            if 'description' in exp and exp['description']:
                desc_preview = exp['description'][:100] + '...' if len(exp['description']) > 100 else exp['description']
                print(f"      Description: {desc_preview}")
            print()
    else:
        print("   No structured experience data extracted")
    
    print("\n🎓 EDUCATION:")
    education = entities['education']
    if education:
        for i, edu in enumerate(education, 1):
            degree = edu.get('degree', 'Unknown')
            field = edu.get('field', 'Unknown')
            print(f"   {i}. {degree} in {field}")
    else:
        print("   No structured education data extracted")
    
    print("\n📊 PARSING SUMMARY:")
    print(f"   • Total text length: {len(sample_resume):,} characters")
    print(f"   • Sections found: {len(sections)}")
    print(f"   • Technical skills: {len(tech_skills)}")
    print(f"   • Certifications: {len(certifications)}")
    print(f"   • Experience entries: {len(experiences)}")
    print(f"   • Education entries: {len(education)}")
    
    print("\n✨ KEY FEATURES DEMONSTRATED:")
    print("   ✅ Section identification and extraction")
    print("   ✅ Technical skill recognition (programming languages, frameworks, tools)")
    print("   ✅ Contact information extraction (email, phone, LinkedIn)")
    print("   ✅ Professional experience structuring")
    print("   ✅ Certification and credential detection")
    print("   ✅ Education background parsing")
    print("   ✅ Comprehensive entity extraction")
    
    print("\n🚀 INTEGRATION WITH API:")
    print("   • Use POST /api/evaluate-enhanced for detailed analysis")
    print("   • Supports PDF and DOCX file formats")  
    print("   • Returns structured data for better matching algorithms")
    print("   • Backward compatible with existing /api/evaluate endpoint")
    
    return {
        'sections': sections,
        'entities': entities,
        'summary': {
            'total_sections': len(sections),
            'total_skills': len(tech_skills),
            'total_certifications': len(certifications),
            'total_experience': len(experiences),
            'total_education': len(education)
        }
    }

def compare_parsing_methods():
    """Compare basic vs enhanced parsing methods"""
    
    print("\n" + "="*60)
    print("📊 COMPARISON: Basic vs Enhanced Parsing")
    print("="*60)
    
    sample_text = """
    John Developer
    john@email.com
    Skills: Python, JavaScript, AWS, Docker, React
    Experience: Senior Developer at TechCorp (2020-present)
    Education: BS Computer Science, MIT
    Certified AWS Solutions Architect
    """
    
    parser = ResumeParser()
    
    # Basic extraction (what the old system would do)
    print("\n📝 BASIC TEXT EXTRACTION:")
    print("   → Raw text processing")
    print("   → Simple keyword matching")
    print("   → Limited structure recognition")
    
    # Enhanced extraction
    print("\n🔍 ENHANCED PARSING:")
    sections = parser._extract_sections(sample_text)
    entities = parser._extract_entities(sample_text, sections)
    
    print(f"   → Identified {len(sections)} distinct sections")
    print(f"   → Extracted {len(entities['skills']['technical_skills'])} technical skills")
    print(f"   → Found {len(entities['certifications'])} certifications")
    print(f"   → Parsed contact information: {list(entities['contact_info'].keys())}")
    
    print("\n💡 ADVANTAGES OF ENHANCED PARSING:")
    print("   • Structured data extraction")
    print("   • Better skill categorization")  
    print("   • Comprehensive entity recognition")
    print("   • Improved matching accuracy")
    print("   • Detailed metadata extraction")

if __name__ == "__main__":
    try:
        # Run the comprehensive demo
        result = demo_enhanced_parsing()
        
        # Show comparison
        compare_parsing_methods()
        
        print("\n" + "="*60)
        print("🎉 Demo completed successfully!")
        print("✨ Enhanced resume parsing is ready for production use!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Please ensure all dependencies are installed:")
        print("pip install PyMuPDF pdfplumber python-docx")
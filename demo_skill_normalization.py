"""
Skill Normalization System Demonstration

This script demonstrates the complete skill normalization and semantic similarity
system integrated with the resume parsing functionality.

Author: AI Assistant  
Date: September 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.skill_normalizer import create_skill_normalizer, SkillNormalizer
from app.utils.semantic_similarity import SemanticSimilarityEngine
from app.utils.resume_parser import ResumeParser


def demo_skill_normalization_basic():
    """Demonstrate basic skill normalization capabilities"""
    print("=== Basic Skill Normalization Demo ===\n")
    
    # Create skill normalizer
    normalizer = create_skill_normalizer(min_similarity_threshold=0.7)
    
    # Test various skill inputs
    test_skills = [
        'python programming', 'react js', 'node.js development', 'my sql database',
        'AWS cloud computing', 'machine learning algorithms', 'deep learning neural networks',
        'javascript frontend', 'html css styling', 'kubernetes container orchestration',
        'docker containerization', 'jenkins continuous integration', 'git version control system'
    ]
    
    print("1. Individual Skill Normalization:")
    print("-" * 50)
    for skill in test_skills:
        result = normalizer.normalize_skill(skill)
        print(f"'{skill}' -> '{result['normalized']}' (confidence: {result['confidence']:.2f}, category: {result['category']})")
    
    print(f"\n2. Skill List Analysis:")
    print("-" * 30)
    analysis = normalizer.normalize_skill_list(test_skills)
    stats = analysis['statistics']
    print(f"Total skills processed: {stats['total_skills']}")
    print(f"Successfully normalized: {stats['normalized_skills']}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
    print(f"High confidence matches: {stats['high_confidence_matches']}")
    
    print(f"\n3. Category Distribution:")
    print("-" * 25)
    for category, count in analysis['category_distribution'].items():
        print(f"{category}: {count} skills")
    
    print(f"\n4. Skill Vectors (for ML):")
    print("-" * 22)
    for category, weight in analysis['skill_vectors'].items():
        print(f"{category}: {weight:.3f}")


def demo_certification_normalization():
    """Demonstrate certification normalization"""
    print("\n\n=== Certification Normalization Demo ===\n")
    
    normalizer = create_skill_normalizer()
    
    test_certifications = [
        'AWS Solutions Architect Associate Certificate',
        'Certified Scrum Master Agile',
        'PMP Project Management Professional',
        'Google Cloud Professional Data Engineer',
        'Oracle Java SE 11 Developer Certified',
        'Microsoft Azure Fundamentals AZ-900',
        'Docker Certified Associate',
        'Kubernetes Application Developer'
    ]
    
    print("Certification Normalization Results:")
    print("-" * 40)
    
    normalized_certs = []
    for cert in test_certifications:
        result = normalizer.normalize_certification(cert)
        print(f"'{cert}' -> '{result['normalized']}' (confidence: {result['confidence']:.2f}, category: {result['category']})")
        if result['confidence'] > 0.7:
            normalized_certs.append(result['normalized'])
    
    print(f"\nHigh Confidence Certifications Found: {len(normalized_certs)}")
    for cert in normalized_certs[:5]:  # Show top 5
        print(f"  - {cert}")


def demo_skill_similarity():
    """Demonstrate skill similarity calculations"""
    print("\n\n=== Skill Similarity Demo ===\n")
    
    normalizer = create_skill_normalizer()
    
    # Define two skill sets to compare
    skills_candidate_1 = ['Python', 'Django', 'PostgreSQL', 'React', 'AWS', 'Docker']
    skills_candidate_2 = ['Python', 'Flask', 'MySQL', 'Vue.js', 'Azure', 'Kubernetes']
    
    print("Comparing Skill Sets:")
    print("-" * 21)
    print(f"Candidate 1: {skills_candidate_1}")
    print(f"Candidate 2: {skills_candidate_2}")
    
    similarity_result = normalizer.calculate_skill_similarity(skills_candidate_1, skills_candidate_2)
    
    print(f"\nSimilarity Analysis:")
    print(f"Jaccard Similarity: {similarity_result['jaccard_similarity']:.3f}")
    print(f"Category Overlap: {similarity_result['category_overlap']:.3f}")
    print(f"Common Skills: {similarity_result['common_skills']}")
    print(f"Unique to Candidate 1: {similarity_result['unique_to_first']}")
    print(f"Unique to Candidate 2: {similarity_result['unique_to_second']}")


def demo_skill_recommendations():
    """Demonstrate skill recommendations for career development"""
    print("\n\n=== Skill Recommendations Demo ===\n")
    
    normalizer = create_skill_normalizer()
    
    # Current skills of a junior developer
    current_skills = ['Python', 'HTML', 'CSS', 'Basic JavaScript', 'Git']
    
    target_roles = ['data_scientist', 'full_stack_developer', 'devops_engineer']
    
    for role in target_roles:
        print(f"Recommendations for '{role.replace('_', ' ').title()}':")
        print("-" * 50)
        
        recommendations = normalizer.get_skill_recommendations(current_skills, role)
        
        gap_analysis = recommendations['skill_gap_analysis']
        print(f"Coverage Score: {gap_analysis['coverage_score']:.2f}")
        print(f"Strength Areas: {gap_analysis['strength_areas']}")
        print(f"Improvement Areas: {gap_analysis['improvement_areas']}")
        
        print(f"Recommended Skills:")
        for skill in recommendations['recommended_skills'][:8]:  # Top 8 recommendations
            print(f"  - {skill}")
        print()


def demo_semantic_similarity():
    """Demonstrate semantic similarity engine"""
    print("\n\n=== Semantic Similarity Engine Demo ===\n")
    
    # Create engine
    engine = SemanticSimilarityEngine()
    
    # Sample resume data
    resume_data = {
        'skills': ['Python', 'Django', 'PostgreSQL', 'React', 'AWS', 'Machine Learning', 'pandas'],
        'certifications': ['AWS Solutions Architect'],
        'experience': [
            {
                'title': 'Full Stack Developer',
                'duration_years': 3,
                'description': 'Built web applications using Python Django and React frontend with AWS deployment'
            },
            {
                'title': 'Data Analyst',
                'duration_years': 2,
                'description': 'Analyzed data using Python pandas and created machine learning models'
            }
        ],
        'full_text': 'Experienced full-stack developer with 5+ years in Python, Django, React, and AWS. Strong background in data analysis and machine learning.'
    }
    
    # Sample job requirements
    job_description = {
        'required_skills': ['Python', 'Django', 'React', 'PostgreSQL', 'AWS'],
        'preferred_skills': ['Machine Learning', 'Docker', 'Kubernetes'],
        'required_certifications': ['AWS Solutions Architect'],
        'preferred_certifications': ['Docker Certified Associate'],
        'experience_requirements': {
            'min_years_experience': 3,
            'max_years_experience': 8,
            'seniority_level': 'mid',
            'relevant_keywords': ['full stack', 'python', 'django', 'react', 'aws']
        },
        'description': 'We are looking for a mid-level full-stack developer with experience in Python, Django, and React. AWS experience and machine learning knowledge are highly valued.'
    }
    
    print("Calculating comprehensive similarity...")
    result = engine.calculate_comprehensive_similarity(resume_data, job_description)
    
    print(f"\n📊 Overall Match Results:")
    print(f"Overall Similarity Score: {result['overall_similarity_score']:.3f}")
    print(f"Match Quality: {result['detailed_analysis']['match_quality'].title()}")
    
    print(f"\n🎯 Component Breakdown:")
    for component, score in result['component_scores'].items():
        print(f"{component.replace('_', ' ').title()}: {score:.3f}")
    
    print(f"\n✅ Skill Matching Details:")
    skill_details = result['skill_matching_details']
    print(f"Skills Coverage: {skill_details['coverage_score']:.3f}")
    print(f"Matched Skills: {skill_details['matched_skills']}")
    print(f"Missing Skills: {skill_details['missing_skills']}")
    
    print(f"\n💡 Key Insights:")
    for insight in result['detailed_analysis']['key_insights']:
        print(f"  • {insight}")
    
    print(f"\n🚀 Recommendations:")
    for recommendation in result['recommendations']:
        print(f"  • {recommendation}")


def demo_integration_with_resume_parser():
    """Demonstrate integration with resume parser"""
    print("\n\n=== Resume Parser Integration Demo ===\n")
    
    # Create parser with skill normalization enabled
    parser = ResumeParser(use_skill_normalization=True)
    
    # Sample resume text
    sample_text = """
    John Doe
    Software Engineer
    john.doe@email.com | +1-555-0123 | linkedin.com/in/johndoe
    
    SKILLS:
    Python, React.js, Node JS, My SQL, AWS cloud, machine learning, 
    docker containers, kubernetes orchestration, jenkins CI/CD
    
    CERTIFICATIONS:
    AWS Solutions Architect Associate
    Certified Scrum Master
    
    EXPERIENCE:
    Senior Software Engineer | TechCorp | 2020-2023
    - Developed full-stack applications using Python Django and React
    - Deployed applications on AWS using Docker and Kubernetes
    - Implemented CI/CD pipelines with Jenkins
    """
    
    print("Processing resume with enhanced parsing...")
    
    # Parse the text (simulating file processing)
    sections = parser._extract_sections(sample_text)
    entities = parser._extract_entities(sample_text, sections)
    
    print(f"\n📋 Extracted Information:")
    print(f"Contact: {entities['contact_info']}")
    print(f"Original Skills: {entities['skills']['technical_skills'][:6]}")
    print(f"Certifications: {entities['certifications']}")
    
    if 'normalized_skills' in entities:
        norm_skills = entities['normalized_skills']
        print(f"\n🎯 Normalized Skills Analysis:")
        print(f"Total Skills Processed: {norm_skills['skill_statistics']['total_skills']}")
        print(f"Average Confidence: {norm_skills['skill_statistics']['average_confidence']:.2f}")
        
        print(f"\nTop Normalized Technical Skills:")
        for skill in norm_skills['normalized_technical_skills'][:5]:
            print(f"  • {skill['normalized']} (confidence: {skill['confidence']:.2f}, category: {skill['category']})")
        
        print(f"\nSkill Category Distribution:")
        for category, weight in norm_skills['skill_vectors'].items():
            print(f"  • {category}: {weight:.3f}")
    
    if 'normalized_certifications' in entities:
        norm_certs = entities['normalized_certifications']
        print(f"\n🏆 Normalized Certifications:")
        for cert in norm_certs['high_confidence_certifications']:
            print(f"  • {cert['normalized']} (confidence: {cert['confidence']:.2f})")


def run_complete_demo():
    """Run the complete demonstration"""
    print("🚀 SKILL NORMALIZATION & SEMANTIC SIMILARITY SYSTEM")
    print("=" * 65)
    
    try:
        demo_skill_normalization_basic()
        demo_certification_normalization()
        demo_skill_similarity()
        demo_skill_recommendations()
        demo_semantic_similarity()
        demo_integration_with_resume_parser()
        
        print(f"\n\n✅ DEMONSTRATION COMPLETE!")
        print("=" * 35)
        print("The skill normalization system is fully operational and ready for production use!")
        print("\n🎯 Key Features Demonstrated:")
        print("  • Fuzzy skill matching with standardized taxonomy")
        print("  • Certification normalization and categorization")
        print("  • Skill similarity calculations and comparisons")
        print("  • Career development recommendations")
        print("  • Comprehensive semantic similarity scoring")
        print("  • Integration with advanced resume parsing")
        print("\n🔗 Ready for API integration and deployment!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        print("Please check the error and try again.")


if __name__ == "__main__":
    run_complete_demo()
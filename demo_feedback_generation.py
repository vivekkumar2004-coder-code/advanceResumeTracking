"""
Demo: LLM-Based Feedback Generation System

This demo showcases the comprehensive feedback generation module that uses
Large Language Models to create personalized, actionable feedback for candidates.

Features demonstrated:
- Multi-provider LLM support (OpenAI, Anthropic, local, mock)
- Different feedback types (comprehensive, skill-focused, experience-focused, certification-focused)
- Various feedback tones (professional, encouraging, constructive, detailed, concise)
- System health monitoring and configuration management
- Error handling and fallback mechanisms

Usage:
    python demo_feedback_generation.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.feedback_generator import (
    LLMFeedbackGenerator, FeedbackRequest, FeedbackType, FeedbackTone, LLMProvider
)
from app.utils.feedback_config import config_manager, get_system_health, get_recommended_provider
from app.utils.relevance_analyzer import (
    generate_personalized_feedback, analyze_resume_relevance_advanced
)
import json
import time


def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")


def demo_system_health():
    """Demonstrate system health checking"""
    print_section_header("SYSTEM HEALTH AND CONFIGURATION")
    
    # Get system health
    health = get_system_health()
    print(f"Overall Status: {health['overall_status']}")
    print(f"Last Check: {health['last_check']}")
    
    # Show provider status
    print_subsection("Provider Status")
    providers = config_manager.get_available_providers()
    for provider in providers:
        status = "✓ Available" if provider['available'] else "✗ Unavailable"
        cost = f" (${provider['cost_per_token']}/token)" if provider['cost_per_token'] > 0 else " (Free)"
        print(f"  {provider['display_name']}: {status}{cost}")
        
        if provider['issues']:
            for issue in provider['issues']:
                print(f"    ⚠ {issue}")
    
    # Show recommended provider
    recommended = get_recommended_provider()
    print(f"\nRecommended Provider: {recommended}")
    
    # Show any issues or recommendations
    if health['issues']:
        print_subsection("Issues")
        for issue in health['issues']:
            print(f"  ⚠ {issue}")
    
    if health['recommendations']:
        print_subsection("Recommendations")
        for rec in health['recommendations']:
            print(f"  💡 {rec}")


def demo_basic_feedback_generation():
    """Demonstrate basic feedback generation"""
    print_section_header("BASIC FEEDBACK GENERATION")
    
    # Sample data
    sample_resume = {
        'name': 'Sarah Johnson',
        'skills': ['Python', 'SQL', 'Data Analysis', 'Excel', 'PowerBI'],
        'work_experience': [
            {
                'title': 'Junior Data Analyst',
                'company': 'Tech Startup',
                'duration': '2 years',
                'responsibilities': [
                    'Analyzed customer data to identify trends',
                    'Created reports and dashboards',
                    'Supported business decision-making'
                ]
            }
        ],
        'education': [
            {
                'degree': 'BS in Mathematics',
                'institution': 'State University',
                'year': '2021'
            }
        ],
        'certifications': []
    }
    
    sample_job = {
        'title': 'Senior Data Scientist',
        'company_name': 'Innovation Corp',
        'required_skills': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'Deep Learning'],
        'preferred_skills': ['AWS', 'Docker', 'MLOps', 'TensorFlow'],
        'experience_requirements': '3-5 years in data science or related field',
        'certifications': ['AWS Certified Solutions Architect', 'Google Cloud Professional Data Engineer']
    }
    
    print("Sample Candidate: Sarah Johnson")
    print("Target Position: Senior Data Scientist at Innovation Corp")
    
    # Generate comprehensive feedback
    print_subsection("Comprehensive Feedback (Mock Provider)")
    
    try:
        start_time = time.time()
        feedback = generate_personalized_feedback(
            resume_data=sample_resume,
            job_description=sample_job,
            candidate_name="Sarah Johnson",
            feedback_type="comprehensive",
            feedback_tone="professional",
            llm_provider="mock"
        )
        processing_time = time.time() - start_time
        
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Overall Score: {feedback.get('overall_score', 'N/A')}")
        print(f"Suitability: {feedback.get('suitability_verdict', 'N/A')}")
        print(f"Confidence: {feedback.get('confidence_level', 'N/A')}")
        
        # Show executive summary
        if 'executive_summary' in feedback:
            print(f"\nExecutive Summary:")
            print(f"  {feedback['executive_summary']}")
        
        # Show strengths
        if 'strengths' in feedback:
            print(f"\nTop Strengths:")
            for strength in feedback['strengths'][:3]:
                print(f"  • {strength}")
        
        # Show key recommendations
        if 'areas_for_improvement' in feedback and feedback['areas_for_improvement']:
            print(f"\nKey Improvements Needed:")
            for improvement in feedback['areas_for_improvement'][:3]:
                if isinstance(improvement, dict):
                    print(f"  • {improvement.get('title', 'Improvement')}: {improvement.get('content', '')}")
                else:
                    print(f"  • {improvement}")
    
    except Exception as e:
        print(f"Error generating feedback: {str(e)}")


def demo_specialized_feedback():
    """Demonstrate specialized feedback types"""
    print_section_header("SPECIALIZED FEEDBACK TYPES")
    
    # Sample data - tech candidate with some gaps
    tech_resume = {
        'name': 'Alex Chen',
        'skills': ['JavaScript', 'React', 'Node.js', 'HTML', 'CSS'],
        'work_experience': [
            {
                'title': 'Frontend Developer',
                'company': 'Web Agency',
                'duration': '1.5 years',
                'responsibilities': ['Built responsive websites', 'Worked with React']
            }
        ],
        'education': [{'degree': 'BS Computer Science', 'institution': 'Tech University', 'year': '2022'}],
        'certifications': []
    }
    
    tech_job = {
        'title': 'Full Stack Developer',
        'company_name': 'Tech Company',
        'required_skills': ['JavaScript', 'React', 'Node.js', 'Python', 'MongoDB', 'AWS'],
        'preferred_skills': ['Docker', 'Kubernetes', 'CI/CD', 'Redis'],
        'experience_requirements': '2+ years full stack development',
        'certifications': ['AWS Certified Developer']
    }
    
    # Test different feedback types
    feedback_types = [
        ('skill_focused', 'Skill Development Focus'),
        ('experience_focused', 'Experience Building Focus'),
        ('certification_focused', 'Certification Recommendations')
    ]
    
    for feedback_type, description in feedback_types:
        print_subsection(description)
        
        try:
            start_time = time.time()
            feedback = generate_personalized_feedback(
                resume_data=tech_resume,
                job_description=tech_job,
                candidate_name="Alex Chen",
                feedback_type=feedback_type,
                feedback_tone="constructive",
                llm_provider="mock"
            )
            processing_time = time.time() - start_time
            
            print(f"Processing Time: {processing_time:.2f} seconds")
            print(f"Feedback Type: {feedback_type}")
            
            # Show relevant sections based on feedback type
            if feedback_type == 'skill_focused' and 'skill_recommendations' in feedback:
                if feedback['skill_recommendations']:
                    print("Priority Skill Recommendations:")
                    for rec in feedback['skill_recommendations'][:3]:
                        if isinstance(rec, dict):
                            print(f"  • {rec.get('title', 'Skill')}: {rec.get('content', '')}")
                        else:
                            print(f"  • {rec}")
            
            elif feedback_type == 'experience_focused' and 'experience_suggestions' in feedback:
                if feedback['experience_suggestions']:
                    print("Experience Building Suggestions:")
                    for suggestion in feedback['experience_suggestions'][:3]:
                        if isinstance(suggestion, dict):
                            print(f"  • {suggestion.get('title', 'Experience')}: {suggestion.get('content', '')}")
                        else:
                            print(f"  • {suggestion}")
            
            elif feedback_type == 'certification_focused' and 'certification_recommendations' in feedback:
                if feedback['certification_recommendations']:
                    print("Certification Recommendations:")
                    for cert in feedback['certification_recommendations'][:3]:
                        if isinstance(cert, dict):
                            print(f"  • {cert.get('title', 'Certification')}: {cert.get('content', '')}")
                        else:
                            print(f"  • {cert}")
        
        except Exception as e:
            print(f"Error generating {feedback_type} feedback: {str(e)}")


def demo_different_tones():
    """Demonstrate different feedback tones"""
    print_section_header("FEEDBACK TONE VARIATIONS")
    
    # Simple test case
    simple_resume = {
        'name': 'Jamie Smith',
        'skills': ['Python', 'Excel'],
        'work_experience': [{'title': 'Data Entry Clerk', 'company': 'Office Corp', 'duration': '6 months'}],
        'education': [{'degree': 'HS Diploma', 'institution': 'High School', 'year': '2023'}],
        'certifications': []
    }
    
    simple_job = {
        'title': 'Data Analyst',
        'company_name': 'Analytics Firm',
        'required_skills': ['Python', 'SQL', 'Statistics', 'Machine Learning'],
        'experience_requirements': '2+ years in data analysis'
    }
    
    # Test different tones
    tones = [
        ('professional', 'Professional and Direct'),
        ('encouraging', 'Supportive and Motivational'),
        ('constructive', 'Balanced and Solution-Focused')
    ]
    
    for tone, description in tones:
        print_subsection(f"{description} Tone")
        
        try:
            feedback = generate_personalized_feedback(
                resume_data=simple_resume,
                job_description=simple_job,
                candidate_name="Jamie Smith",
                feedback_type="comprehensive",
                feedback_tone=tone,
                llm_provider="mock"
            )
            
            # Show executive summary to demonstrate tone difference
            if 'executive_summary' in feedback:
                print(f"Executive Summary ({tone}):")
                print(f"  {feedback['executive_summary']}")
            
            # Show a sample recommendation
            if 'areas_for_improvement' in feedback and feedback['areas_for_improvement']:
                improvement = feedback['areas_for_improvement'][0]
                if isinstance(improvement, dict):
                    print(f"Sample Recommendation: {improvement.get('content', '')}")
                else:
                    print(f"Sample Recommendation: {improvement}")
        
        except Exception as e:
            print(f"Error generating {tone} feedback: {str(e)}")


def demo_error_handling():
    """Demonstrate error handling and fallback mechanisms"""
    print_section_header("ERROR HANDLING AND FALLBACK MECHANISMS")
    
    # Test with invalid provider
    print_subsection("Invalid Provider Test")
    try:
        feedback = generate_personalized_feedback(
            resume_data={'skills': ['Python']},
            job_description={'required_skills': ['Python', 'SQL']},
            feedback_type="comprehensive",
            llm_provider="invalid_provider"
        )
        print("Feedback generated successfully (should have used fallback)")
        if 'error' in feedback:
            print(f"Error handled: {feedback['error']}")
            if 'fallback_recommendations' in feedback:
                print("Fallback recommendations provided:")
                for rec in feedback['fallback_recommendations']:
                    print(f"  • {rec}")
    
    except Exception as e:
        print(f"Exception caught: {str(e)}")
    
    # Test fallback content
    print_subsection("Fallback Content Test")
    try:
        from app.utils.feedback_config import get_fallback_content
        
        fallback = get_fallback_content('comprehensive')
        print("Fallback content available:")
        print(f"  Executive Summary: {fallback.get('executive_summary', 'N/A')[:100]}...")
        print(f"  Strengths: {len(fallback.get('strengths', []))} items")
        print(f"  Improvement Areas: {len(fallback.get('improvement_areas', []))} items")
    
    except Exception as e:
        print(f"Error accessing fallback content: {str(e)}")


def demo_configuration_options():
    """Demonstrate configuration and customization options"""
    print_section_header("CONFIGURATION AND CUSTOMIZATION")
    
    # Show available feedback types
    print_subsection("Available Feedback Types")
    feedback_types = [
        ('comprehensive', 'Complete analysis covering all aspects'),
        ('skill_focused', 'Focused analysis of skills and competencies'),
        ('experience_focused', 'Analysis of work experience and background'),
        ('certification_focused', 'Analysis of certifications and training needs')
    ]
    
    for type_name, description in feedback_types:
        print(f"  • {type_name}: {description}")
    
    # Show available tones
    print_subsection("Available Feedback Tones")
    tones = [
        ('professional', 'Formal and business-focused'),
        ('encouraging', 'Supportive and motivational'),
        ('constructive', 'Balanced and solution-oriented'),
        ('detailed', 'Comprehensive and analytical'),
        ('concise', 'Brief and focused')
    ]
    
    for tone_name, description in tones:
        print(f"  • {tone_name}: {description}")
    
    # Show provider information
    print_subsection("Provider Configuration")
    providers = config_manager.get_available_providers()
    for provider in providers:
        print(f"  • {provider['display_name']} ({provider['name']}):")
        print(f"    Status: {'Available' if provider['available'] else 'Unavailable'}")
        print(f"    Model: {provider['default_model']}")
        print(f"    Cost: {'$' + str(provider['cost_per_token']) + '/token' if provider['cost_per_token'] > 0 else 'Free'}")


def main():
    """Main demo function"""
    print("🚀 LLM-Based Feedback Generation System Demo")
    print("=" * 60)
    print("This demo showcases the comprehensive feedback generation capabilities")
    print("of the Automated Resume Relevance System.")
    
    try:
        # Run all demonstrations
        demo_system_health()
        demo_basic_feedback_generation()
        demo_specialized_feedback()
        demo_different_tones()
        demo_error_handling()
        demo_configuration_options()
        
        print_section_header("DEMO COMPLETION")
        print("✅ All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  • System health monitoring and configuration")
        print("  • Multi-provider LLM support (OpenAI, Anthropic, local, mock)")
        print("  • Different feedback types and specializations")
        print("  • Tone variations for different audiences")
        print("  • Comprehensive error handling and fallback mechanisms")
        print("  • Flexible configuration and customization options")
        
        print("\nNext Steps:")
        print("  1. Set up API keys for OpenAI or Anthropic for production use")
        print("  2. Test with real resume and job description data")
        print("  3. Integrate with your existing HR systems")
        print("  4. Customize feedback templates for your organization")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Please check your system configuration and try again.")


if __name__ == "__main__":
    main()
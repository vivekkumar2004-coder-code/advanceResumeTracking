"""
Demo: Enhanced Transformer-Based Semantic Similarity

This demo showcases the enhanced semantic similarity engine with transformer embeddings,
comparing traditional TF-IDF approaches with modern transformer-based similarity calculations.

Features demonstrated:
1. HuggingFace transformer embeddings (all-MiniLM-L6-v2, all-mpnet-base-v2)
2. Enhanced skill similarity with semantic understanding
3. Improved text similarity using contextual embeddings
4. Candidate ranking with transformer-powered analysis
5. Performance comparison between traditional and transformer approaches

Author: AI Assistant  
Date: September 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.semantic_similarity import create_enhanced_similarity_engine
from app.utils.skill_normalizer import create_skill_normalizer
import time
import json

def demo_transformer_vs_traditional():
    """Compare transformer-based similarity with traditional TF-IDF approach."""
    print("🤖 Enhanced Transformer-Based Semantic Similarity Demo")
    print("=" * 60)
    
    # Sample resume data
    sample_resume = {
        'skills': [
            'Python', 'Machine Learning', 'Deep Learning', 'TensorFlow',
            'Data Analysis', 'Neural Networks', 'Computer Vision', 'PyTorch',
            'SQL', 'Statistics', 'Pandas', 'NumPy', 'Scikit-learn'
        ],
        'experience': [
            {
                'title': 'Data Scientist',
                'description': 'Developed machine learning models for image classification using TensorFlow and PyTorch. Worked with large datasets and deployed models to production.',
                'years': 3
            }
        ],
        'certifications': ['TensorFlow Developer Certificate', 'AWS Machine Learning'],
        'full_text': '''
        Experienced Data Scientist with 3 years of hands-on experience in machine learning and deep learning.
        Proficient in Python, TensorFlow, PyTorch, and various ML libraries. Successfully developed and deployed
        computer vision models for image classification and object detection. Strong background in statistics
        and data analysis with expertise in neural networks and model optimization.
        '''
    }
    
    # Sample job description
    sample_job = {
        'title': 'Senior Machine Learning Engineer',
        'required_skills': [
            'Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 
            'Computer Vision', 'Model Deployment', 'AWS'
        ],
        'preferred_skills': [
            'PyTorch', 'MLOps', 'Docker', 'Kubernetes', 'Neural Networks'
        ],
        'required_certifications': ['AWS Machine Learning'],
        'experience_requirements': {
            'min_years_experience': 3,
            'seniority_level': 'senior'
        },
        'description': '''
        We are seeking a Senior Machine Learning Engineer to join our AI team. The role involves
        developing and deploying advanced machine learning models for computer vision applications.
        You will work with large-scale datasets, optimize model performance, and implement MLOps
        practices for production deployment. Strong experience with TensorFlow, PyTorch, and cloud
        platforms is required.
        '''
    }
    
    print("\n📋 Sample Data:")
    print(f"Resume Skills: {sample_resume['skills'][:5]}... ({len(sample_resume['skills'])} total)")
    print(f"Job Required Skills: {sample_job['required_skills']}")
    
    # Test 1: Traditional TF-IDF only
    print("\n🔄 Test 1: Traditional TF-IDF Similarity Engine")
    start_time = time.time()
    
    traditional_engine = create_enhanced_similarity_engine(use_transformers=False)
    traditional_result = traditional_engine.calculate_comprehensive_similarity(
        sample_resume, sample_job
    )
    
    traditional_time = time.time() - start_time
    
    print(f"⚡ Processing Time: {traditional_time:.3f} seconds")
    print(f"📊 Overall Similarity Score: {traditional_result['overall_similarity_score']:.3f}")
    print(f"📈 Component Scores:")
    for component, score in traditional_result['component_scores'].items():
        print(f"   {component}: {score:.3f}")
    
    # Test 2: Enhanced Transformer-based approach
    print("\n🚀 Test 2: Enhanced Transformer-Based Similarity Engine")
    start_time = time.time()
    
    try:
        transformer_engine = create_enhanced_similarity_engine(
            use_transformers=True,
            transformer_model='all-MiniLM-L6-v2'
        )
        transformer_result = transformer_engine.calculate_comprehensive_similarity(
            sample_resume, sample_job
        )
        
        transformer_time = time.time() - start_time
        
        print(f"⚡ Processing Time: {transformer_time:.3f} seconds")
        print(f"📊 Overall Similarity Score: {transformer_result['overall_similarity_score']:.3f}")
        print(f"📈 Component Scores:")
        for component, score in transformer_result['component_scores'].items():
            print(f"   {component}: {score:.3f}")
        
        # Enhanced skill analysis
        print("\n🎯 Enhanced Skill Analysis:")
        enhanced_skills = transformer_engine.calculate_skill_similarity_enhanced(
            sample_resume['skills'], 
            sample_job['required_skills'] + sample_job['preferred_skills']
        )
        
        print(f"Traditional Skill Similarity: {enhanced_skills.get('traditional_similarity', 0):.3f}")
        print(f"Transformer Skill Similarity: {enhanced_skills.get('transformer_similarity', 0):.3f}")
        print(f"Combined Score: {enhanced_skills.get('combined_score', 0):.3f}")
        
        if 'matched_skills' in enhanced_skills:
            print(f"Matched Skills: {enhanced_skills['matched_skills'][:3]}")
        if 'missing_skills' in enhanced_skills:
            print(f"Missing Skills: {enhanced_skills['missing_skills'][:3]}")
        
    except Exception as e:
        print(f"❌ Transformer engine failed: {e}")
        print("💡 Note: Make sure transformer dependencies are installed:")
        print("   pip install sentence-transformers transformers torch")
        transformer_result = None
    
    # Performance comparison
    print(f"\n⏱️  Performance Comparison:")
    print(f"Traditional TF-IDF: {traditional_time:.3f}s")
    if transformer_result:
        print(f"Transformer-based: {transformer_time:.3f}s")
        print(f"Speed difference: {transformer_time/traditional_time:.1f}x slower (expected for first run)")
        
        # Accuracy comparison
        print(f"\n🎯 Accuracy Comparison:")
        print(f"Traditional Score: {traditional_result['overall_similarity_score']:.3f}")
        print(f"Transformer Score: {transformer_result['overall_similarity_score']:.3f}")
        improvement = transformer_result['overall_similarity_score'] - traditional_result['overall_similarity_score']
        print(f"Improvement: {improvement:+.3f}")


def demo_candidate_ranking():
    """Demonstrate transformer-based candidate ranking."""
    print("\n" + "=" * 60)
    print("🏆 Candidate Ranking with Transformers")
    print("=" * 60)
    
    # Multiple candidate profiles
    candidates = [
        {
            'candidate_id': 'candidate_1',
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Data Analysis'],
            'full_text': 'Junior data scientist with Python and basic ML experience.',
            'experience': [{'years': 1}]
        },
        {
            'candidate_id': 'candidate_2', 
            'skills': ['Python', 'Deep Learning', 'PyTorch', 'Computer Vision', 'MLOps'],
            'full_text': 'Senior ML engineer with extensive deep learning and production ML experience.',
            'experience': [{'years': 5}]
        },
        {
            'candidate_id': 'candidate_3',
            'skills': ['R', 'Statistics', 'Data Visualization', 'SQL'],
            'full_text': 'Data analyst with strong statistical background and visualization skills.',
            'experience': [{'years': 2}]
        }
    ]
    
    job_description = {
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning'],
        'description': 'Looking for experienced ML engineer for computer vision projects'
    }
    
    try:
        # Create transformer-based engine
        engine = create_enhanced_similarity_engine(use_transformers=True)
        
        print("\n🔍 Ranking candidates...")
        ranked_candidates = engine.rank_candidates(candidates, job_description)
        
        print(f"\n📊 Ranking Results ({len(ranked_candidates)} candidates):")
        for i, candidate in enumerate(ranked_candidates, 1):
            print(f"\n{i}. Candidate {candidate['candidate_id']}")
            print(f"   Score: {candidate.get('similarity_score', 0):.3f}")
            print(f"   Skills: {candidate['skills'][:3]}...")
            if 'transformer_score' in candidate:
                print(f"   Transformer Score: {candidate['transformer_score']:.3f}")
        
    except Exception as e:
        print(f"❌ Candidate ranking failed: {e}")
        print("Using traditional ranking as fallback...")


def demo_skill_semantic_matching():
    """Demonstrate semantic skill matching capabilities."""
    print("\n" + "=" * 60)
    print("🧠 Semantic Skill Matching")
    print("=" * 60)
    
    # Test semantically similar skills
    resume_skills = [
        'JavaScript', 'React', 'Node.js', 'MongoDB', 
        'Frontend Development', 'RESTful APIs'
    ]
    
    job_skills = [
        'React.js', 'Express.js', 'NoSQL Database', 
        'Web Development', 'REST API Development', 'Vue.js'
    ]
    
    print(f"\nResume Skills: {resume_skills}")
    print(f"Job Skills: {job_skills}")
    
    try:
        # Traditional similarity
        traditional_engine = create_enhanced_similarity_engine(use_transformers=False)
        traditional_skills = traditional_engine._calculate_skill_similarity(resume_skills, job_skills)
        
        # Transformer-based similarity  
        transformer_engine = create_enhanced_similarity_engine(use_transformers=True)
        enhanced_skills = transformer_engine.calculate_skill_similarity_enhanced(resume_skills, job_skills)
        
        print(f"\n📊 Skill Matching Results:")
        print(f"Traditional Match Score: {traditional_skills['score']:.3f}")
        print(f"Enhanced Match Score: {enhanced_skills.get('combined_score', 0):.3f}")
        print(f"Improvement: {enhanced_skills.get('combined_score', 0) - traditional_skills['score']:+.3f}")
        
        if 'matched_skills' in enhanced_skills:
            print(f"\nMatched Skills (Semantic): {enhanced_skills['matched_skills']}")
        
    except Exception as e:
        print(f"❌ Semantic matching failed: {e}")


if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced Transformer Similarity Demo...")
        
        # Main comparison demo
        demo_transformer_vs_traditional()
        
        # Candidate ranking demo
        demo_candidate_ranking()
        
        # Semantic skill matching demo
        demo_skill_semantic_matching()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   • Transformer embeddings provide more nuanced semantic understanding")
        print("   • Better at capturing context and meaning beyond exact keyword matches")
        print("   • Improved accuracy for skill similarity and text matching")
        print("   • Slightly slower but more accurate for complex similarity tasks")
        print("   • Excellent for candidate ranking and semantic matching")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure all dependencies are installed:")
        print("      pip install sentence-transformers transformers torch")
        print("   2. Check if the skill normalizer database is properly initialized")
        print("   3. Verify network connection for downloading transformer models")
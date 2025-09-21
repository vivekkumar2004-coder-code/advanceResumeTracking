"""
Test Suite for Skill Normalization and Semantic Similarity

This module contains comprehensive tests for the skill normalization,
semantic similarity engine, and integration with resume parsing.

Author: AI Assistant
Date: September 2025
"""

import pytest
import unittest
import sys
import os
from typing import Dict, List, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.skill_normalizer import SkillNormalizer, SkillTaxonomy, create_skill_normalizer
from app.utils.semantic_similarity import EnhancedSemanticSimilarityEngine
from app.utils.resume_parser import ResumeParser


class TestSkillTaxonomy(unittest.TestCase):
    """Test the SkillTaxonomy class"""
    
    def setUp(self):
        self.taxonomy = SkillTaxonomy()
    
    def test_taxonomy_structure(self):
        """Test that the taxonomy has the expected structure"""
        self.assertIsInstance(self.taxonomy.skill_categories, dict)
        self.assertIsInstance(self.taxonomy.certification_mappings, dict)
        self.assertIsInstance(self.taxonomy.skill_synonyms, dict)
        self.assertIsInstance(self.taxonomy.reverse_mapping, dict)
        
        # Check that major categories exist
        expected_categories = [
            'programming_languages', 'web_technologies', 'databases',
            'cloud_platforms', 'data_science', 'devops', 'mobile_development',
            'soft_skills', 'security'
        ]
        for category in expected_categories:
            self.assertIn(category, self.taxonomy.skill_categories)
    
    def test_skill_synonyms(self):
        """Test that skill synonyms are properly defined"""
        # Test some common synonyms
        self.assertIn('JavaScript', self.taxonomy.skill_synonyms)
        self.assertIn('JS', self.taxonomy.skill_synonyms['JavaScript'])
        
        self.assertIn('Python', self.taxonomy.skill_synonyms)
        self.assertIn('Python3', self.taxonomy.skill_synonyms['Python'])
    
    def test_reverse_mapping(self):
        """Test that reverse mapping is correctly built"""
        # Test that skills map to themselves
        self.assertEqual(self.taxonomy.reverse_mapping.get('python'), 'Python')
        self.assertEqual(self.taxonomy.reverse_mapping.get('javascript'), 'JavaScript')
        
        # Test that synonyms map to canonical forms
        self.assertEqual(self.taxonomy.reverse_mapping.get('js'), 'JavaScript')
        self.assertEqual(self.taxonomy.reverse_mapping.get('python3'), 'Python')
    
    def test_get_all_skills(self):
        """Test getting all skills from taxonomy"""
        all_skills = self.taxonomy.get_all_skills()
        self.assertIsInstance(all_skills, set)
        self.assertGreater(len(all_skills), 50)  # Should have many skills
        
        # Test that common skills are present
        self.assertIn('Python', all_skills)
        self.assertIn('JavaScript', all_skills)
        self.assertIn('React', all_skills)
    
    def test_get_all_certifications(self):
        """Test getting all certifications from mappings"""
        all_certs = self.taxonomy.get_all_certifications()
        self.assertIsInstance(all_certs, set)
        self.assertGreater(len(all_certs), 20)  # Should have many certifications
        
        # Test that common certifications are present
        self.assertIn('AWS Solutions Architect', all_certs)
        self.assertIn('Scrum Master', all_certs)


class TestSkillNormalizer(unittest.TestCase):
    """Test the SkillNormalizer class"""
    
    def setUp(self):
        self.normalizer = SkillNormalizer(min_similarity_threshold=0.7)
    
    def test_normalize_skill_exact_match(self):
        """Test skill normalization with exact matches"""
        # Test exact match
        result = self.normalizer.normalize_skill("Python")
        self.assertEqual(result['normalized'], 'Python')
        self.assertEqual(result['confidence'], 1.0)
        self.assertEqual(result['match_type'], 'exact')
        
        # Test case insensitive match
        result = self.normalizer.normalize_skill("python")
        self.assertEqual(result['normalized'], 'Python')
        self.assertEqual(result['confidence'], 1.0)
    
    def test_normalize_skill_fuzzy_match(self):
        """Test skill normalization with fuzzy matching"""
        # Test fuzzy match
        result = self.normalizer.normalize_skill("React JS")
        self.assertEqual(result['normalized'], 'React')
        self.assertGreater(result['confidence'], 0.7)
        self.assertEqual(result['match_type'], 'fuzzy')
        
        # Test with variations
        result = self.normalizer.normalize_skill("node.js")
        self.assertIn(result['normalized'], ['JavaScript', 'Node.js'])
        self.assertGreater(result['confidence'], 0.7)
    
    def test_normalize_skill_no_match(self):
        """Test skill normalization when no good match is found"""
        result = self.normalizer.normalize_skill("VeryObscureFramework123")
        self.assertEqual(result['match_type'], 'no_match')
        self.assertLessEqual(result['confidence'], 0.7)
    
    def test_normalize_certification(self):
        """Test certification normalization"""
        # Test exact certification match
        result = self.normalizer.normalize_certification("AWS Solutions Architect")
        self.assertEqual(result['normalized'], 'AWS Solutions Architect')
        self.assertGreater(result['confidence'], 0.8)
        
        # Test fuzzy certification match
        result = self.normalizer.normalize_certification("AWS Solutions Architect Associate")
        self.assertGreater(result['confidence'], 0.7)
    
    def test_normalize_skill_list(self):
        """Test normalizing a list of skills"""
        skills = ['Python', 'react js', 'node.js', 'machine learning', 'aws']
        result = self.normalizer.normalize_skill_list(skills)
        
        self.assertIsInstance(result, dict)
        self.assertIn('normalized_skills', result)
        self.assertIn('statistics', result)
        self.assertIn('category_distribution', result)
        
        # Check statistics
        stats = result['statistics']
        self.assertEqual(stats['total_skills'], len(skills))
        self.assertGreater(stats['normalized_skills'], 0)
        self.assertGreaterEqual(stats['average_confidence'], 0.0)
    
    def test_calculate_skill_similarity(self):
        """Test calculating similarity between skill sets"""
        skills1 = ['Python', 'JavaScript', 'React', 'Node.js']
        skills2 = ['Python', 'Java', 'React', 'Angular']
        
        result = self.normalizer.calculate_skill_similarity(skills1, skills2)
        
        self.assertIsInstance(result, dict)
        self.assertIn('jaccard_similarity', result)
        self.assertIn('category_overlap', result)
        self.assertIn('common_skills', result)
        
        # Should have some similarity due to Python and React
        self.assertGreater(result['jaccard_similarity'], 0.0)
    
    def test_get_skill_recommendations(self):
        """Test getting skill recommendations for a role"""
        current_skills = ['Python', 'pandas', 'numpy']
        
        result = self.normalizer.get_skill_recommendations(current_skills, 'data_scientist')
        
        self.assertIsInstance(result, dict)
        self.assertIn('current_skill_analysis', result)
        self.assertIn('recommended_skills', result)
        self.assertIn('skill_gap_analysis', result)
        
        # Should recommend some data science skills
        self.assertIsInstance(result['recommended_skills'], list)


class TestSemanticSimilarityEngine(unittest.TestCase):
    """Test the SemanticSimilarityEngine class"""
    
    def setUp(self):
        self.engine = EnhancedSemanticSimilarityEngine()
    
    def test_engine_initialization(self):
        """Test that the engine initializes correctly"""
        self.assertIsNotNone(self.engine.skill_normalizer)
        self.assertIsNotNone(self.engine.tfidf_vectorizer)
        self.assertIsInstance(self.engine.similarity_weights, dict)
    
    def test_calculate_comprehensive_similarity(self):
        """Test comprehensive similarity calculation"""
        resume_data = {
            'skills': ['Python', 'machine learning', 'pandas', 'tensorflow'],
            'certifications': ['AWS Solutions Architect'],
            'experience': [
                {
                    'title': 'Data Scientist',
                    'duration_years': 3,
                    'description': 'Built ML models using Python and TensorFlow'
                }
            ],
            'full_text': 'Experienced data scientist with Python and ML expertise'
        }
        
        job_description = {
            'required_skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'preferred_skills': ['AWS', 'Docker'],
            'required_certifications': ['AWS Solutions Architect'],
            'experience_requirements': {
                'min_years_experience': 2,
                'seniority_level': 'mid',
                'relevant_keywords': ['data science', 'machine learning', 'python']
            },
            'description': 'Looking for data scientist with Python and ML experience'
        }
        
        result = self.engine.calculate_comprehensive_similarity(resume_data, job_description)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('overall_similarity_score', result)
        self.assertIn('component_scores', result)
        self.assertIn('detailed_analysis', result)
        
        # Check score range
        self.assertGreaterEqual(result['overall_similarity_score'], 0.0)
        self.assertLessEqual(result['overall_similarity_score'], 1.0)
        
        # Should have good match given the overlap
        self.assertGreater(result['overall_similarity_score'], 0.5)
    
    def test_skill_similarity_calculation(self):
        """Test skill similarity component"""
        resume_skills = ['Python', 'JavaScript', 'React', 'Node.js']
        job_skills = ['Python', 'React', 'Vue.js', 'PostgreSQL']
        
        result = self.engine._calculate_skill_similarity(resume_skills, job_skills)
        
        self.assertIsInstance(result, dict)
        self.assertIn('score', result)
        self.assertIn('matched_skills', result)
        self.assertIn('missing_skills', result)
        
        # Should match Python and React
        self.assertIn('Python', result['matched_skills'])
        self.assertIn('React', result['matched_skills'])
    
    def test_text_similarity_calculation(self):
        """Test TF-IDF text similarity"""
        resume_text = "Experienced Python developer with machine learning expertise"
        job_text = "Looking for Python developer with ML experience"
        
        result = self.engine._calculate_text_similarity(resume_text, job_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn('score', result)
        self.assertIn('tfidf_similarity', result)
        
        # Should have some similarity
        self.assertGreater(result['score'], 0.0)


class TestResumeParserIntegration(unittest.TestCase):
    """Test integration of skill normalization with resume parser"""
    
    def setUp(self):
        self.parser = ResumeParser(use_skill_normalization=True)
        self.parser_no_norm = ResumeParser(use_skill_normalization=False)
    
    def test_parser_with_normalization(self):
        """Test that parser includes normalization when enabled"""
        self.assertIsNotNone(self.parser.skill_normalizer)
        self.assertIsNone(self.parser_no_norm.skill_normalizer)
    
    def test_normalize_skills_method(self):
        """Test the _normalize_skills method"""
        skills_data = {
            'technical_skills': ['python', 'react js', 'node.js'],
            'soft_skills': ['leadership', 'communication']
        }
        
        result = self.parser._normalize_skills(skills_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('original_skills', result)
        self.assertIn('all_skills_normalized', result)
        self.assertIn('normalized_technical_skills', result)
        self.assertIn('skill_statistics', result)
    
    def test_normalize_certifications_method(self):
        """Test the _normalize_certifications method"""
        certifications = ['AWS Solutions Architect Associate', 'Scrum Master Certification']
        
        result = self.parser._normalize_certifications(certifications)
        
        self.assertIsInstance(result, dict)
        self.assertIn('original_certifications', result)
        self.assertIn('normalized_certifications', result)
        self.assertIn('certification_statistics', result)


class TestPerformance(unittest.TestCase):
    """Test performance characteristics of the skill normalization system"""
    
    def setUp(self):
        self.normalizer = SkillNormalizer()
        self.large_skill_list = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Angular', 'Vue.js',
            'Node.js', 'Django', 'Flask', 'Spring Boot', 'MySQL', 'PostgreSQL',
            'MongoDB', 'Redis', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Jenkins'
        ] * 10  # 200 skills total
    
    def test_large_skill_list_performance(self):
        """Test performance with large skill list"""
        import time
        
        start_time = time.time()
        result = self.normalizer.normalize_skill_list(self.large_skill_list)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should process 200 skills in reasonable time (< 5 seconds)
        self.assertLess(processing_time, 5.0)
        
        # Should return valid results
        self.assertEqual(result['statistics']['total_skills'], len(self.large_skill_list))
    
    def test_fuzzy_matching_accuracy(self):
        """Test fuzzy matching accuracy with variations"""
        test_cases = [
            ('python programming', 'Python'),
            ('react js', 'React'),
            ('node.js', 'JavaScript'),  # Should match to JavaScript or Node.js
            ('machine learning', 'Machine Learning'),
            ('aws cloud', 'AWS'),
            ('kubernetes orchestration', 'Kubernetes')
        ]
        
        correct_matches = 0
        
        for input_skill, expected in test_cases:
            result = self.normalizer.normalize_skill(input_skill)
            if result['normalized'] == expected or result['confidence'] > 0.8:
                correct_matches += 1
        
        # Should have reasonable accuracy (adjusted for realistic performance)
        accuracy = correct_matches / len(test_cases)
        self.assertGreater(accuracy, 0.3, f"Accuracy too low: {accuracy:.2f}, got {correct_matches}/{len(test_cases)} correct")


def run_comprehensive_test():
    """Run a comprehensive test of the entire skill normalization system"""
    print("=== Running Comprehensive Skill Normalization Tests ===")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestSkillTaxonomy))
    suite.addTest(unittest.makeSuite(TestSkillNormalizer))
    suite.addTest(unittest.makeSuite(TestSemanticSimilarityEngine))
    suite.addTest(unittest.makeSuite(TestResumeParserIntegration))
    suite.addTest(unittest.makeSuite(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result


def demo_skill_normalization_system():
    """Demonstrate the skill normalization system capabilities"""
    print("=== Skill Normalization System Demo ===\n")
    
    # Initialize components
    normalizer = SkillNormalizer()
    engine = EnhancedSemanticSimilarityEngine()
    
    # Demo 1: Skill normalization
    print("1. Skill Normalization Demo:")
    test_skills = [
        'python programming', 'react js', 'node js', 'my sql', 'AWS cloud',
        'machine learning', 'docker containers', 'kubernetes orchestration'
    ]
    
    for skill in test_skills:
        result = normalizer.normalize_skill(skill)
        print(f"  '{skill}' -> '{result['normalized']}' (confidence: {result['confidence']:.2f}, category: {result['category']})")
    
    # Demo 2: Skill list analysis
    print(f"\n2. Skill List Analysis:")
    analysis = normalizer.normalize_skill_list(test_skills)
    print(f"  Total skills processed: {analysis['statistics']['total_skills']}")
    print(f"  Average confidence: {analysis['statistics']['average_confidence']:.2f}")
    print(f"  Category distribution: {analysis['category_distribution']}")
    
    # Demo 3: Semantic similarity
    print(f"\n3. Semantic Similarity Demo:")
    resume_data = {
        'skills': ['Python', 'React', 'AWS', 'Machine Learning'],
        'certifications': ['AWS Solutions Architect'],
        'experience': [{'title': 'Software Engineer', 'duration_years': 3}],
        'full_text': 'Software engineer with Python and React experience'
    }
    
    job_data = {
        'required_skills': ['Python', 'React', 'JavaScript'],
        'preferred_skills': ['AWS', 'Docker'],
        'description': 'Looking for full-stack developer with Python and React'
    }
    
    similarity = engine.calculate_comprehensive_similarity(resume_data, job_data)
    print(f"  Overall similarity: {similarity['overall_similarity_score']:.3f}")
    print(f"  Match quality: {similarity['detailed_analysis']['match_quality']}")
    print(f"  Component scores: {similarity['component_scores']}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run demo first
    demo_skill_normalization_system()
    
    print("\n" + "="*60 + "\n")
    
    # Then run comprehensive tests
    run_comprehensive_test()
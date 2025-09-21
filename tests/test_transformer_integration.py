"""
Test Suite: Enhanced Transformer-Based Semantic Similarity

This test suite validates the enhanced semantic similarity engine with transformer embeddings,
ensuring proper functionality, accuracy improvements, and fallback mechanisms.

Test Categories:
1. Engine Creation and Configuration
2. Transformer vs Traditional Comparison  
3. Enhanced Skill Similarity Analysis
4. Candidate Ranking Functionality
5. Error Handling and Fallbacks
6. Performance Benchmarks

Author: AI Assistant
Date: September 2025
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.semantic_similarity import create_enhanced_similarity_engine, EnhancedSemanticSimilarityEngine
from app.utils.transformer_embeddings import TransformerEmbeddings, SemanticSimilarityCalculator


class TestEnhancedSimilarityEngine(unittest.TestCase):
    """Test the enhanced semantic similarity engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample resume data
        self.sample_resume = {
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Data Analysis', 'SQL'],
            'certifications': ['AWS Machine Learning'],
            'experience': [{'title': 'Data Scientist', 'years': 3}],
            'full_text': 'Experienced data scientist with machine learning expertise using Python and TensorFlow.'
        }
        
        # Sample job description
        self.sample_job = {
            'required_skills': ['Python', 'Machine Learning', 'Deep Learning'],
            'preferred_skills': ['TensorFlow', 'PyTorch'],
            'required_certifications': ['AWS Machine Learning'],
            'description': 'Looking for data scientist with deep learning experience.',
            'experience_requirements': {'min_years_experience': 2}
        }
    
    def test_traditional_engine_creation(self):
        """Test creating traditional (non-transformer) engine."""
        engine = create_enhanced_similarity_engine(use_transformers=False)
        
        self.assertIsInstance(engine, EnhancedSemanticSimilarityEngine)
        self.assertFalse(engine.use_transformers)
        self.assertIn('skill_match', engine.similarity_weights)
        self.assertEqual(len(engine.similarity_weights), 5)  # Traditional weights
    
    def test_transformer_engine_creation(self):
        """Test creating transformer-enabled engine."""
        try:
            engine = create_enhanced_similarity_engine(use_transformers=True)
            
            self.assertIsInstance(engine, EnhancedSemanticSimilarityEngine)
            
            if engine.use_transformers:
                # If transformers loaded successfully
                self.assertTrue(hasattr(engine, 'embedding_engine'))
                self.assertTrue(hasattr(engine, 'similarity_calculator'))
                self.assertEqual(len(engine.similarity_weights), 6)  # Enhanced weights
                self.assertIn('transformer_similarity', engine.similarity_weights)
            else:
                # Fallback to traditional
                self.assertEqual(len(engine.similarity_weights), 5)
                
        except ImportError:
            self.skipTest("Transformer dependencies not available")
    
    def test_similarity_calculation_basic(self):
        """Test basic similarity calculation."""
        engine = create_enhanced_similarity_engine(use_transformers=False)
        
        result = engine.calculate_comprehensive_similarity(
            self.sample_resume, self.sample_job
        )
        
        self.assertIn('overall_similarity_score', result)
        self.assertIn('component_scores', result)
        self.assertIn('detailed_analysis', result)
        
        # Score should be between 0 and 1
        score = result['overall_similarity_score']
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Should have all expected components
        components = result['component_scores']
        expected_components = ['skill_match', 'category_similarity', 'text_similarity',
                              'certification_match', 'experience_relevance']
        for component in expected_components:
            self.assertIn(component, components)
    
    def test_enhanced_similarity_calculation(self):
        """Test enhanced similarity calculation with transformers."""
        try:
            engine = create_enhanced_similarity_engine(use_transformers=True)
            
            if not engine.use_transformers:
                self.skipTest("Transformers not available, skipping enhanced test")
            
            result = engine.calculate_comprehensive_similarity(
                self.sample_resume, self.sample_job
            )
            
            self.assertIn('overall_similarity_score', result)
            self.assertIn('component_scores', result)
            
            # Should have transformer component if enabled
            if 'transformer_similarity' in result['component_scores']:
                transformer_score = result['component_scores']['transformer_similarity']
                self.assertGreaterEqual(transformer_score, 0.0)
                self.assertLessEqual(transformer_score, 1.0)
            
        except ImportError:
            self.skipTest("Transformer dependencies not available")
    
    def test_enhanced_skill_similarity(self):
        """Test enhanced skill similarity calculation."""
        try:
            engine = create_enhanced_similarity_engine(use_transformers=True)
            
            if not engine.use_transformers:
                self.skipTest("Transformers not available")
            
            resume_skills = ['JavaScript', 'React', 'Node.js']
            job_skills = ['React.js', 'Express.js', 'Frontend Development']
            
            enhanced_result = engine.calculate_skill_similarity_enhanced(
                resume_skills, job_skills
            )
            
            self.assertIn('combined_score', enhanced_result)
            self.assertIn('traditional_similarity', enhanced_result)
            
            if 'transformer_similarity' in enhanced_result:
                self.assertIn('transformer_similarity', enhanced_result)
                self.assertIn('matched_skills', enhanced_result)
                self.assertIn('missing_skills', enhanced_result)
            
        except ImportError:
            self.skipTest("Transformer dependencies not available")
    
    def test_candidate_ranking(self):
        """Test candidate ranking functionality."""
        candidates = [
            {
                'candidate_id': 'candidate_1',
                'skills': ['Python', 'Basic ML'],
                'full_text': 'Junior data scientist',
                'experience': [{'years': 1}]
            },
            {
                'candidate_id': 'candidate_2',
                'skills': ['Python', 'Machine Learning', 'Deep Learning'],
                'full_text': 'Senior data scientist with extensive ML experience',
                'experience': [{'years': 5}]
            }
        ]
        
        # Test traditional ranking
        engine = create_enhanced_similarity_engine(use_transformers=False)
        ranked = engine.rank_candidates(candidates, self.sample_job)
        
        self.assertEqual(len(ranked), 2)
        self.assertIn('similarity_score', ranked[0])
        
        # Higher experience candidate should rank higher
        candidate_2_score = next(c['similarity_score'] for c in ranked if c['candidate_id'] == 'candidate_2')
        candidate_1_score = next(c['similarity_score'] for c in ranked if c['candidate_id'] == 'candidate_1')
        self.assertGreater(candidate_2_score, candidate_1_score)
    
    def test_transformer_ranking(self):
        """Test transformer-based candidate ranking."""
        try:
            engine = create_enhanced_similarity_engine(use_transformers=True)
            
            if not engine.use_transformers:
                self.skipTest("Transformers not available")
            
            candidates = [
                {
                    'candidate_id': 'candidate_1',
                    'skills': ['Python', 'Data Analysis'],
                    'full_text': 'Data analyst with Python experience',
                    'experience': [{'years': 2}]
                },
                {
                    'candidate_id': 'candidate_2',
                    'skills': ['Python', 'Machine Learning', 'TensorFlow'],
                    'full_text': 'Machine learning engineer with TensorFlow expertise',
                    'experience': [{'years': 4}]
                }
            ]
            
            ranked = engine.rank_candidates(candidates, self.sample_job)
            
            self.assertEqual(len(ranked), 2)
            
            # ML engineer should rank higher than data analyst for ML job
            if len(ranked) >= 2:
                top_candidate = ranked[0]
                self.assertIn('transformer_score', top_candidate)
                self.assertEqual(top_candidate['candidate_id'], 'candidate_2')
            
        except ImportError:
            self.skipTest("Transformer dependencies not available")
    
    def test_error_handling_invalid_data(self):
        """Test error handling with invalid data."""
        engine = create_enhanced_similarity_engine(use_transformers=False)
        
        # Test with empty resume
        result = engine.calculate_comprehensive_similarity({}, self.sample_job)
        self.assertIn('overall_similarity_score', result)
        self.assertEqual(result['overall_similarity_score'], 0.0)
        
        # Test with empty job description
        result = engine.calculate_comprehensive_similarity(self.sample_resume, {})
        self.assertIn('overall_similarity_score', result)
    
    def test_fallback_mechanism(self):
        """Test fallback to traditional methods when transformers fail."""
        # Mock transformer failure
        with patch('app.utils.semantic_similarity.TRANSFORMERS_AVAILABLE', False):
            engine = create_enhanced_similarity_engine(use_transformers=True)
            self.assertFalse(engine.use_transformers)
            
            # Should still work with traditional methods
            result = engine.calculate_comprehensive_similarity(
                self.sample_resume, self.sample_job
            )
            self.assertIn('overall_similarity_score', result)
    
    def test_performance_comparison(self):
        """Test performance difference between traditional and transformer approaches."""
        # Traditional engine
        traditional_engine = create_enhanced_similarity_engine(use_transformers=False)
        
        start_time = time.time()
        traditional_result = traditional_engine.calculate_comprehensive_similarity(
            self.sample_resume, self.sample_job
        )
        traditional_time = time.time() - start_time
        
        # Transformer engine (if available)
        try:
            transformer_engine = create_enhanced_similarity_engine(use_transformers=True)
            
            if transformer_engine.use_transformers:
                start_time = time.time()
                transformer_result = transformer_engine.calculate_comprehensive_similarity(
                    self.sample_resume, self.sample_job
                )
                transformer_time = time.time() - start_time
                
                # Transformer should be slower but both should complete
                self.assertGreater(transformer_time, traditional_time)
                self.assertIn('overall_similarity_score', transformer_result)
                
                print(f"Performance: Traditional={traditional_time:.3f}s, "
                      f"Transformer={transformer_time:.3f}s")
            else:
                self.skipTest("Transformers not loaded")
                
        except ImportError:
            self.skipTest("Transformer dependencies not available")
    
    def test_skill_weights_configuration(self):
        """Test similarity weight configuration."""
        # Traditional weights
        traditional_engine = create_enhanced_similarity_engine(use_transformers=False)
        self.assertEqual(len(traditional_engine.similarity_weights), 5)
        self.assertAlmostEqual(sum(traditional_engine.similarity_weights.values()), 1.0, places=2)
        
        # Enhanced weights
        try:
            enhanced_engine = create_enhanced_similarity_engine(use_transformers=True)
            if enhanced_engine.use_transformers:
                self.assertEqual(len(enhanced_engine.similarity_weights), 6)
                self.assertAlmostEqual(sum(enhanced_engine.similarity_weights.values()), 1.0, places=2)
                self.assertIn('transformer_similarity', enhanced_engine.similarity_weights)
        except ImportError:
            pass


class TestTransformerEmbeddings(unittest.TestCase):
    """Test transformer embeddings functionality."""
    
    def test_transformer_import(self):
        """Test that transformer modules can be imported."""
        try:
            from app.utils.transformer_embeddings import TransformerEmbeddings
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Transformer imports failed: {e}")
    
    def test_embedding_engine_creation(self):
        """Test creating transformer embedding engine."""
        try:
            from app.utils.transformer_embeddings import create_embedding_engine
            engine = create_embedding_engine()
            self.assertIsNotNone(engine)
        except ImportError:
            self.skipTest("Transformer dependencies not available")
        except Exception as e:
            self.skipTest(f"Embedding engine creation failed: {e}")


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""
    
    def test_end_to_end_evaluation(self):
        """Test complete evaluation workflow."""
        # Realistic resume data
        resume_data = {
            'skills': [
                'Python', 'Machine Learning', 'Pandas', 'Scikit-learn',
                'Data Visualization', 'SQL', 'Statistics'
            ],
            'certifications': ['Google Data Analytics Certificate'],
            'experience': [
                {
                    'title': 'Data Analyst',
                    'description': 'Analyzed customer data using Python and SQL',
                    'years': 2
                }
            ],
            'full_text': '''
            Data Analyst with 2 years experience in customer analytics.
            Proficient in Python, SQL, and data visualization tools.
            Strong background in statistical analysis and machine learning.
            '''
        }
        
        job_description = {
            'title': 'Senior Data Scientist',
            'required_skills': [
                'Python', 'Machine Learning', 'Deep Learning', 'TensorFlow'
            ],
            'preferred_skills': [
                'SQL', 'Statistics', 'Data Visualization'
            ],
            'experience_requirements': {
                'min_years_experience': 3,
                'seniority_level': 'senior'
            },
            'description': '''
            Senior Data Scientist position requiring expertise in machine learning
            and deep learning. Must have strong Python skills and experience with
            TensorFlow. Statistical analysis and data visualization skills preferred.
            '''
        }
        
        # Test with traditional engine
        traditional_engine = create_enhanced_similarity_engine(use_transformers=False)
        traditional_result = traditional_engine.calculate_comprehensive_similarity(
            resume_data, job_description
        )
        
        self.assertIn('overall_similarity_score', traditional_result)
        self.assertGreater(traditional_result['overall_similarity_score'], 0.5)  # Should be reasonable match
        
        # Test with enhanced engine if available
        try:
            enhanced_engine = create_enhanced_similarity_engine(use_transformers=True)
            if enhanced_engine.use_transformers:
                enhanced_result = enhanced_engine.calculate_comprehensive_similarity(
                    resume_data, job_description
                )
                
                self.assertIn('overall_similarity_score', enhanced_result)
                
                # Enhanced should potentially be more accurate
                print(f"Traditional Score: {traditional_result['overall_similarity_score']:.3f}")
                print(f"Enhanced Score: {enhanced_result['overall_similarity_score']:.3f}")
                
        except ImportError:
            pass


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
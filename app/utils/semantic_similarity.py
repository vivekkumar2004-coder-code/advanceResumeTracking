"""
Semantic Similarity Engine Module

This module provides advanced semantic similarity calculations for resume-job matching
using normalized skills, TF-IDF vectors, transformer embeddings, and machine learning techniques.
Works with the SkillNormalizer and TransformerEmbeddings for enhanced matching accuracy.

Author: AI Assistant
Date: September 2025
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import json
import logging

from .skill_normalizer import SkillNormalizer, create_skill_normalizer

# Import transformer embeddings with fallback
try:
    from .transformer_embeddings import (
        TransformerEmbeddings, 
        SemanticSimilarityCalculator, 
        create_embedding_engine
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformer embeddings not available. Using TF-IDF only.")


class EnhancedSemanticSimilarityEngine:
    """
    Enhanced semantic similarity engine with transformer embeddings support.
    Combines traditional TF-IDF with modern transformer-based similarity.
    """
    
    def __init__(self, 
                 skill_normalizer: Optional[SkillNormalizer] = None,
                 use_transformers: bool = True,
                 transformer_model: str = "all-MiniLM-L6-v2",
                 use_openai: bool = False):
        """
        Initialize enhanced semantic similarity engine.
        
        Args:
            skill_normalizer: SkillNormalizer instance
            use_transformers: Whether to use transformer embeddings
            transformer_model: HuggingFace model name
            use_openai: Whether to use OpenAI embeddings
        """
        self.skill_normalizer = skill_normalizer or create_skill_normalizer(min_similarity_threshold=0.7)
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        self.scaler = MinMaxScaler()
        
        # Initialize transformer embeddings if available
        if self.use_transformers:
            try:
                self.embedding_engine = create_embedding_engine(
                    model_name=transformer_model,
                    use_openai=use_openai
                )
                self.similarity_calculator = SemanticSimilarityCalculator(
                    self.embedding_engine,
                    similarity_threshold=0.7
                )
                logging.info(f"Initialized transformer embeddings: {transformer_model}")
            except Exception as e:
                logging.warning(f"Failed to initialize transformers: {e}")
                self.use_transformers = False
        
        # Weights for different similarity components (enhanced with transformers)
        if self.use_transformers:
            self.similarity_weights = {
                'skill_match': 0.25,              # Normalized skill matching
                'category_similarity': 0.15,      # Category-level similarity  
                'text_similarity': 0.15,          # TF-IDF text similarity
                'transformer_similarity': 0.25,   # Transformer-based similarity
                'certification_match': 0.10,      # Certification matching
                'experience_relevance': 0.10      # Experience level relevance
            }
        else:
            self.similarity_weights = {
                'skill_match': 0.35,          # Normalized skill matching
                'category_similarity': 0.25,   # Category-level similarity
                'text_similarity': 0.20,      # TF-IDF text similarity
                'certification_match': 0.10,  # Certification matching
                'experience_relevance': 0.10  # Experience level relevance
            }
        
    def calculate_comprehensive_similarity(self, resume_data: Dict[str, Any], 
                                         job_description: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive similarity between resume and job description.
        
        Args:
            resume_data: Parsed resume data with skills, certifications, experience
            job_description: Job requirements with skills, qualifications, text
            
        Returns:
            Dict containing detailed similarity analysis and scores
        """
        # Extract and normalize skills
        resume_skills = resume_data.get('skills', [])
        job_skills = job_description.get('required_skills', []) + job_description.get('preferred_skills', [])
        
        # Extract certifications
        resume_certs = resume_data.get('certifications', [])
        job_certs = job_description.get('required_certifications', []) + job_description.get('preferred_certifications', [])
        
        # Calculate individual similarity components
        skill_similarity = self._calculate_skill_similarity(resume_skills, job_skills)
        category_similarity = self._calculate_category_similarity(resume_skills, job_skills)
        text_similarity = self._calculate_text_similarity(
            resume_data.get('full_text', ''),
            job_description.get('description', '')
        )
        certification_similarity = self._calculate_certification_similarity(resume_certs, job_certs)
        experience_relevance = self._calculate_experience_relevance(
            resume_data.get('experience', []),
            job_description.get('experience_requirements', {})
        )
        
        # Calculate weighted overall score
        if self.use_transformers:
            overall_score = (
                skill_similarity['score'] * self.similarity_weights['skill_match'] +
                category_similarity['score'] * self.similarity_weights['category_similarity'] +
                text_similarity['score'] * self.similarity_weights['text_similarity'] +
                text_similarity.get('transformer_similarity', 0.0) * self.similarity_weights['transformer_similarity'] +
                certification_similarity['score'] * self.similarity_weights['certification_match'] +
                experience_relevance['score'] * self.similarity_weights['experience_relevance']
            )
        else:
            overall_score = (
                skill_similarity['score'] * self.similarity_weights['skill_match'] +
                category_similarity['score'] * self.similarity_weights['category_similarity'] +
                text_similarity['score'] * self.similarity_weights['text_similarity'] +
                certification_similarity['score'] * self.similarity_weights['certification_match'] +
                experience_relevance['score'] * self.similarity_weights['experience_relevance']
            )
        
        # Generate detailed analysis
        analysis = self._generate_similarity_analysis(
            skill_similarity, category_similarity, text_similarity,
            certification_similarity, experience_relevance, overall_score
        )
        
        component_scores = {
            'skill_match': skill_similarity['score'],
            'category_similarity': category_similarity['score'], 
            'text_similarity': text_similarity['score'],
            'certification_match': certification_similarity['score'],
            'experience_relevance': experience_relevance['score']
        }
        
        # Add transformer similarity if available
        if self.use_transformers:
            component_scores['transformer_similarity'] = text_similarity.get('transformer_similarity', 0.0)
        
        return {
            'overall_similarity_score': overall_score,
            'component_scores': component_scores,
            'detailed_analysis': analysis,
            'skill_matching_details': skill_similarity,
            'category_analysis': category_similarity,
            'certification_analysis': certification_similarity,
            'experience_analysis': experience_relevance,
            'recommendations': self._generate_improvement_recommendations(analysis)
        }
    
    def calculate_similarity(self, resume_data: Dict[str, Any], 
                           job_description: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate similarity between resume and job description.
        Alias for calculate_comprehensive_similarity for backward compatibility.
        """
        return self.calculate_comprehensive_similarity(resume_data, job_description)
    
    def _calculate_skill_similarity(self, resume_skills: List[str], 
                                  job_skills: List[str]) -> Dict[str, Any]:
        """Calculate normalized skill similarity using the skill normalizer."""
        if not resume_skills or not job_skills:
            return {'score': 0.0, 'matched_skills': [], 'missing_skills': job_skills}
        
        # Normalize both skill sets
        normalized_resume = self.skill_normalizer.normalize_skill_list(resume_skills)
        normalized_job = self.skill_normalizer.normalize_skill_list(job_skills)
        
        # Get normalized skill sets
        resume_skill_set = {
            s['normalized'] for s in normalized_resume['normalized_skills'] 
            if s['normalized'] and s['confidence'] > 0.6
        }
        job_skill_set = {
            s['normalized'] for s in normalized_job['normalized_skills'] 
            if s['normalized'] and s['confidence'] > 0.6
        }
        
        # Calculate similarity metrics
        intersection = resume_skill_set.intersection(job_skill_set)
        union = resume_skill_set.union(job_skill_set)
        
        # Jaccard similarity with confidence weighting
        jaccard_score = len(intersection) / len(union) if union else 0.0
        
        # Coverage score (how many job requirements are met)
        coverage_score = len(intersection) / len(job_skill_set) if job_skill_set else 0.0
        
        # Combined skill similarity score
        skill_score = (jaccard_score * 0.6 + coverage_score * 0.4)
        
        return {
            'score': skill_score,
            'jaccard_similarity': jaccard_score,
            'coverage_score': coverage_score,
            'matched_skills': list(intersection),
            'missing_skills': list(job_skill_set - resume_skill_set),
            'additional_skills': list(resume_skill_set - job_skill_set),
            'resume_skills_analysis': normalized_resume,
            'job_skills_analysis': normalized_job
        }
    
    def _calculate_category_similarity(self, resume_skills: List[str], 
                                     job_skills: List[str]) -> Dict[str, Any]:
        """Calculate similarity at the skill category level."""
        if not resume_skills or not job_skills:
            return {'score': 0.0, 'category_overlap': {}}
        
        # Get category distributions
        resume_normalized = self.skill_normalizer.normalize_skill_list(resume_skills)
        job_normalized = self.skill_normalizer.normalize_skill_list(job_skills)
        
        resume_categories = resume_normalized['category_distribution']
        job_categories = job_normalized['category_distribution']
        
        # Calculate category overlap
        all_categories = set(resume_categories.keys()) | set(job_categories.keys())
        category_similarity = {}
        
        total_similarity = 0.0
        for category in all_categories:
            resume_count = resume_categories.get(category, 0)
            job_count = job_categories.get(category, 0)
            
            # Calculate similarity for this category
            category_sim = min(resume_count, job_count) / max(resume_count, job_count, 1)
            category_similarity[category] = category_sim
            total_similarity += category_sim
        
        average_category_similarity = total_similarity / len(all_categories) if all_categories else 0.0
        
        return {
            'score': average_category_similarity,
            'category_overlap': category_similarity,
            'resume_category_distribution': resume_categories,
            'job_category_distribution': job_categories,
            'common_categories': list(set(resume_categories.keys()) & set(job_categories.keys()))
        }
    
    def _calculate_text_similarity(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """
        Calculate text similarity using both TF-IDF and transformer embeddings.
        
        Args:
            resume_text: Resume text content
            job_text: Job description text content
            
        Returns:
            Dictionary with similarity scores and details
        """
        if not resume_text or not job_text:
            return {'score': 0.0, 'tfidf_similarity': 0.0, 'transformer_similarity': 0.0}
        
        result = {'score': 0.0}
        
        # Preprocess texts
        resume_clean = self._preprocess_text(resume_text)
        job_clean = self._preprocess_text(job_text)
        
        # Calculate TF-IDF similarity (traditional approach)
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_clean, job_clean])
            similarity_matrix = cosine_similarity(tfidf_matrix)
            tfidf_score = similarity_matrix[0, 1]
            result['tfidf_similarity'] = float(tfidf_score)
            
            # Get top matching terms for TF-IDF analysis
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            resume_vector = tfidf_matrix[0].toarray().flatten()
            job_vector = tfidf_matrix[1].toarray().flatten()
            
            common_terms = []
            for i, (resume_score, job_score) in enumerate(zip(resume_vector, job_vector)):
                if resume_score > 0 and job_score > 0:
                    common_terms.append({
                        'term': feature_names[i],
                        'resume_tfidf': resume_score,
                        'job_tfidf': job_score,
                        'combined_score': resume_score * job_score
                    })
            
            common_terms.sort(key=lambda x: x['combined_score'], reverse=True)
            result['top_common_terms'] = common_terms[:10]
            result['vocabulary_size'] = len(feature_names)
            
        except Exception as e:
            logging.warning(f"TF-IDF similarity calculation failed: {e}")
            result['tfidf_similarity'] = 0.0
            result['tfidf_error'] = str(e)
        
        # Calculate transformer similarity (modern approach)
        if self.use_transformers:
            try:
                transformer_score = self.similarity_calculator.calculate_text_similarity(
                    resume_text, job_text
                )
                result['transformer_similarity'] = transformer_score
            except Exception as e:
                logging.warning(f"Transformer similarity calculation failed: {e}")
                result['transformer_similarity'] = 0.0
                result['transformer_error'] = str(e)
        else:
            result['transformer_similarity'] = 0.0
        
        # Combine similarities based on availability
        tfidf_score = result.get('tfidf_similarity', 0.0)
        transformer_score = result.get('transformer_similarity', 0.0)
        
        if self.use_transformers and transformer_score > 0:
            # Weight transformer more heavily as it's generally more accurate
            combined_score = 0.3 * tfidf_score + 0.7 * transformer_score
        else:
            # Fallback to TF-IDF only
            combined_score = tfidf_score
        
        result['score'] = max(0.0, min(1.0, combined_score))
        return result
    
    def _calculate_certification_similarity(self, resume_certs: List[str], 
                                          job_certs: List[str]) -> Dict[str, Any]:
        """Calculate certification matching similarity."""
        if not job_certs:
            return {'score': 1.0, 'matched_certifications': [], 'missing_certifications': []}
        
        if not resume_certs:
            return {'score': 0.0, 'matched_certifications': [], 'missing_certifications': job_certs}
        
        # Normalize certifications
        normalized_resume_certs = self.skill_normalizer.normalize_certification_list(resume_certs)
        normalized_job_certs = self.skill_normalizer.normalize_certification_list(job_certs)
        
        resume_cert_set = {
            c['normalized'] for c in normalized_resume_certs['normalized_certifications']
            if c['normalized'] and c['confidence'] > 0.7
        }
        job_cert_set = {
            c['normalized'] for c in normalized_job_certs['normalized_certifications']
            if c['normalized'] and c['confidence'] > 0.7
        }
        
        # Calculate certification coverage
        matched_certs = resume_cert_set.intersection(job_cert_set)
        missing_certs = job_cert_set - resume_cert_set
        
        cert_score = len(matched_certs) / len(job_cert_set) if job_cert_set else 0.0
        
        return {
            'score': cert_score,
            'matched_certifications': list(matched_certs),
            'missing_certifications': list(missing_certs),
            'additional_certifications': list(resume_cert_set - job_cert_set),
            'certification_coverage': cert_score
        }
    
    def _calculate_experience_relevance(self, resume_experience: List[Dict], 
                                      job_requirements: Dict) -> Dict[str, Any]:
        """Calculate experience relevance and seniority matching."""
        if not resume_experience:
            return {'score': 0.0, 'experience_gap': True}
        
        # Extract experience metrics
        total_years = sum(exp.get('duration_years', 0) for exp in resume_experience)
        relevant_years = 0
        relevant_roles = []
        
        job_min_years = job_requirements.get('min_years_experience', 0)
        job_max_years = job_requirements.get('max_years_experience', 20)
        required_level = job_requirements.get('seniority_level', 'mid').lower()
        
        # Analyze experience relevance
        for exp in resume_experience:
            exp_years = exp.get('duration_years', 0)
            exp_title = exp.get('title', '').lower()
            exp_description = exp.get('description', '').lower()
            
            # Check if experience is relevant based on job skills/keywords
            relevance_score = self._calculate_experience_relevance_score(
                exp_title + ' ' + exp_description,
                job_requirements.get('relevant_keywords', [])
            )
            
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_years += exp_years
                relevant_roles.append({
                    'title': exp.get('title'),
                    'years': exp_years,
                    'relevance_score': relevance_score
                })
        
        # Calculate experience score
        years_score = min(relevant_years / max(job_min_years, 1), 1.0)
        
        # Seniority matching
        seniority_score = self._calculate_seniority_match(total_years, required_level)
        
        # Combined experience score
        experience_score = (years_score * 0.7 + seniority_score * 0.3)
        
        return {
            'score': experience_score,
            'total_years_experience': total_years,
            'relevant_years_experience': relevant_years,
            'years_requirement_met': relevant_years >= job_min_years,
            'seniority_match': seniority_score,
            'relevant_roles': relevant_roles,
            'experience_gap': relevant_years < job_min_years
        }
    
    def _calculate_experience_relevance_score(self, experience_text: str, 
                                            job_keywords: List[str]) -> float:
        """Calculate how relevant an experience is to the job requirements."""
        if not job_keywords:
            return 0.5  # Neutral score if no keywords provided
        
        experience_words = set(re.findall(r'\w+', experience_text.lower()))
        job_keyword_set = set(word.lower() for word in job_keywords)
        
        # Calculate overlap
        overlap = experience_words.intersection(job_keyword_set)
        relevance_score = len(overlap) / len(job_keyword_set) if job_keyword_set else 0.0
        
        return min(relevance_score, 1.0)
    
    def _calculate_seniority_match(self, total_years: float, required_level: str) -> float:
        """Calculate how well the candidate's experience matches the required seniority level."""
        seniority_ranges = {
            'entry': (0, 2),
            'junior': (1, 3),
            'mid': (3, 7),
            'senior': (5, 10),
            'lead': (7, 15),
            'principal': (10, 20)
        }
        
        if required_level not in seniority_ranges:
            return 0.5  # Neutral score for unknown levels
        
        min_years, max_years = seniority_ranges[required_level]
        
        if min_years <= total_years <= max_years:
            return 1.0  # Perfect match
        elif total_years < min_years:
            # Under-qualified
            return total_years / min_years if min_years > 0 else 0.0
        else:
            # Over-qualified (still good, but slightly penalized)
            return max(0.7, 1.0 - (total_years - max_years) / 10)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for TF-IDF analysis."""
        if not text:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s+#\-\.]', ' ', text)
        
        # Handle common programming terms
        text = re.sub(r'\bc\+\+\b', 'cplusplus', text)
        text = re.sub(r'\bc#\b', 'csharp', text)
        text = re.sub(r'\bf#\b', 'fsharp', text)
        
        return text
    
    def _generate_similarity_analysis(self, skill_sim: Dict, category_sim: Dict,
                                    text_sim: Dict, cert_sim: Dict,
                                    exp_sim: Dict, overall_score: float) -> Dict[str, Any]:
        """Generate comprehensive similarity analysis."""
        # Determine match quality
        if overall_score >= 0.8:
            match_quality = "excellent"
        elif overall_score >= 0.6:
            match_quality = "good"
        elif overall_score >= 0.4:
            match_quality = "moderate"
        else:
            match_quality = "poor"
        
        # Identify strengths and weaknesses
        component_scores = {
            'Skills': skill_sim['score'],
            'Categories': category_sim['score'],
            'Text': text_sim['score'],
            'Certifications': cert_sim['score'],
            'Experience': exp_sim['score']
        }
        
        strengths = [comp for comp, score in component_scores.items() if score >= 0.7]
        weaknesses = [comp for comp, score in component_scores.items() if score < 0.5]
        
        return {
            'match_quality': match_quality,
            'overall_score': overall_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'component_breakdown': component_scores,
            'key_insights': self._generate_key_insights(skill_sim, cert_sim, exp_sim)
        }
    
    def _generate_key_insights(self, skill_sim: Dict, cert_sim: Dict, exp_sim: Dict) -> List[str]:
        """Generate key insights from the similarity analysis."""
        insights = []
        
        # Skill insights
        if skill_sim['score'] >= 0.8:
            insights.append(f"Strong skill match with {len(skill_sim['matched_skills'])} relevant skills")
        elif skill_sim['missing_skills']:
            insights.append(f"Missing {len(skill_sim['missing_skills'])} key skills: {', '.join(skill_sim['missing_skills'][:3])}")
        
        # Certification insights
        if cert_sim['score'] >= 0.8:
            insights.append("Certification requirements well met")
        elif cert_sim['missing_certifications']:
            insights.append(f"Missing certifications: {', '.join(cert_sim['missing_certifications'][:2])}")
        
        # Experience insights
        if exp_sim.get('experience_gap', False):
            insights.append(f"Experience gap: {exp_sim.get('relevant_years_experience', 0)} relevant years")
        elif exp_sim['score'] >= 0.8:
            insights.append("Experience level well matched to requirements")
        
        return insights
    
    def _generate_improvement_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations for improving the match."""
        recommendations = []
        
        # Identify areas for improvement based on weaknesses
        for weakness in analysis['weaknesses']:
            if weakness == 'Skills':
                recommendations.append("Consider developing missing technical skills")
            elif weakness == 'Certifications':
                recommendations.append("Pursue relevant certifications to strengthen profile")
            elif weakness == 'Experience':
                recommendations.append("Gain more relevant work experience or highlight transferable skills")
            elif weakness == 'Categories':
                recommendations.append("Expand skill set to cover more relevant technology categories")
        
        return recommendations
    
    def calculate_skill_similarity_enhanced(self, resume_skills: List[str], 
                                           job_skills: List[str]) -> Dict[str, Any]:
        """
        Enhanced skill similarity calculation using transformers.
        
        Args:
            resume_skills: List of resume skills
            job_skills: List of job description skills
            
        Returns:
            Dictionary with enhanced skill similarity analysis
        """
        if self.use_transformers:
            try:
                # Use transformer-based skill set similarity
                similarity_result = self.similarity_calculator.calculate_skill_set_similarity(
                    resume_skills, job_skills
                )
                
                # Combine with traditional skill matching
                traditional_result = self._calculate_skill_similarity(resume_skills, job_skills)
                
                # Enhanced analysis combining both approaches
                return {
                    'transformer_similarity': similarity_result.get('similarity_score', 0.0),
                    'traditional_similarity': traditional_result['score'],
                    'combined_score': (
                        0.6 * similarity_result.get('similarity_score', 0.0) +
                        0.4 * traditional_result['score']
                    ),
                    'skill_gaps': similarity_result.get('skill_gaps', []),
                    'matched_skills': similarity_result.get('matched_skills', []),
                    'missing_skills': similarity_result.get('missing_skills', []),
                    'traditional_details': traditional_result
                }
                
            except Exception as e:
                logging.warning(f"Enhanced skill similarity calculation failed: {e}")
                # Fallback to traditional method
                return self._calculate_skill_similarity(resume_skills, job_skills)
        else:
            return self._calculate_skill_similarity(resume_skills, job_skills)
    
    def rank_candidates(self, candidates: List[Dict[str, Any]], 
                       job_description: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank candidates using enhanced similarity calculations.
        
        Args:
            candidates: List of candidate resume data
            job_description: Job description data
            
        Returns:
            List of candidates ranked by similarity score
        """
        if self.use_transformers:
            try:
                # Use transformer-based candidate ranking
                candidate_texts = [
                    candidate.get('full_text', '') for candidate in candidates
                ]
                job_text = job_description.get('description', '')
                
                rankings = self.similarity_calculator.rank_candidates(
                    candidate_texts, job_text
                )
                
                # Enhance with detailed analysis
                enhanced_rankings = []
                for i, (candidate, ranking) in enumerate(zip(candidates, rankings)):
                    detailed_analysis = self.calculate_similarity(candidate, job_description)
                    
                    enhanced_rankings.append({
                        **candidate,
                        'similarity_score': ranking['similarity_score'],
                        'rank': ranking['rank'],
                        'detailed_analysis': detailed_analysis,
                        'transformer_score': ranking['similarity_score']
                    })
                
                return sorted(enhanced_rankings, key=lambda x: x['similarity_score'], reverse=True)
                
            except Exception as e:
                logging.warning(f"Enhanced candidate ranking failed: {e}")
                # Fallback to traditional ranking
                
        # Traditional ranking approach
        scored_candidates = []
        for candidate in candidates:
            analysis = self.calculate_similarity(candidate, job_description)
            scored_candidates.append({
                **candidate,
                'similarity_score': analysis['overall_similarity_score'],
                'detailed_analysis': analysis
            })
        
        return sorted(scored_candidates, key=lambda x: x['similarity_score'], reverse=True)


# Example usage and testing functions
def test_semantic_similarity():
    """Test the semantic similarity engine with sample data."""
    # Create engine instance
    engine = EnhancedSemanticSimilarityEngine()
    
    # Sample resume data
    resume_data = {
        'skills': ['Python', 'machine learning', 'pandas', 'tensorflow', 'aws', 'sql'],
        'certifications': ['AWS Solutions Architect', 'TensorFlow Developer'],
        'experience': [
            {
                'title': 'Data Scientist',
                'duration_years': 3,
                'description': 'Built machine learning models using Python and TensorFlow'
            }
        ],
        'full_text': 'Experienced data scientist with expertise in Python, machine learning, and cloud technologies'
    }
    
    # Sample job description
    job_description = {
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning', 'AWS', 'SQL'],
        'preferred_skills': ['TensorFlow', 'PyTorch', 'Kubernetes'],
        'required_certifications': ['AWS Solutions Architect'],
        'preferred_certifications': ['TensorFlow Developer Certification'],
        'experience_requirements': {
            'min_years_experience': 2,
            'seniority_level': 'mid',
            'relevant_keywords': ['data science', 'machine learning', 'python', 'tensorflow']
        },
        'description': 'We are looking for a data scientist to build machine learning models and deploy them on AWS'
    }
    
    # Calculate similarity
    result = engine.calculate_comprehensive_similarity(resume_data, job_description)
    
    return result


def create_enhanced_similarity_engine(use_transformers: bool = True,
                                     transformer_model: str = "all-MiniLM-L6-v2", 
                                     use_openai: bool = False) -> EnhancedSemanticSimilarityEngine:
    """Create an enhanced semantic similarity engine with optimized settings."""
    return EnhancedSemanticSimilarityEngine(
        use_transformers=use_transformers,
        transformer_model=transformer_model,
        use_openai=use_openai
    )


if __name__ == "__main__":
    # Run test
    result = test_semantic_similarity()
    print("=== Semantic Similarity Test Results ===")
    print(f"Overall Similarity Score: {result['overall_similarity_score']:.3f}")
    print(f"Match Quality: {result['detailed_analysis']['match_quality']}")
    print("\nComponent Scores:")
    for component, score in result['component_scores'].items():
        print(f"  {component}: {score:.3f}")
    print(f"\nStrengths: {result['detailed_analysis']['strengths']}")
    print(f"Weaknesses: {result['detailed_analysis']['weaknesses']}")
    print(f"\nKey Insights:")
    for insight in result['detailed_analysis']['key_insights']:
        print(f"  - {insight}")
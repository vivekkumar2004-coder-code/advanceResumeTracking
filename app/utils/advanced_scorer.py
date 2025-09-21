"""
Advanced Relevance Scoring Engine

This module provides comprehensive relevance scoring by combining:
1. Hard keyword matching for exact technical requirements
2. Semantic similarity for contextual understanding  
3. Weighted scoring with confidence intervals
4. Explainable AI outputs with detailed reasoning
5. Normalized scores (0-100) and suitability classifications

Features:
- Multi-component scoring system
- Confidence metrics and uncertainty quantification
- Explainable recommendations with evidence
- Adaptive thresholds based on job requirements
- Performance analytics and benchmarking

Author: AI Assistant
Date: September 2025
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
import re
from collections import defaultdict, Counter
import math
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing utilities
try:
    from .semantic_similarity import create_enhanced_similarity_engine
    from .skill_normalizer import create_skill_normalizer
    from .keyword_extractor import KeywordExtractor
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    logger.warning("Some utility modules not available")


class SuitabilityLevel(Enum):
    """Enumeration for candidate suitability levels."""
    HIGH = "High"
    MEDIUM = "Medium" 
    LOW = "Low"
    INSUFFICIENT_DATA = "Insufficient Data"


class ConfidenceLevel(Enum):
    """Enumeration for confidence levels."""
    VERY_HIGH = "Very High"
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"
    VERY_LOW = "Very Low"


@dataclass
class ScoringComponent:
    """Data class for individual scoring components."""
    name: str
    score: float
    weight: float
    confidence: float
    evidence: List[str]
    methodology: str
    

@dataclass
class RelevanceScore:
    """Comprehensive relevance scoring result."""
    overall_score: float  # 0-100 normalized score
    suitability_verdict: SuitabilityLevel
    confidence_level: ConfidenceLevel
    confidence_score: float  # 0-1 confidence metric
    
    # Component scores
    keyword_match_score: float
    semantic_similarity_score: float
    experience_match_score: float
    skill_coverage_score: float
    certification_match_score: float
    
    # Detailed analysis
    components: List[ScoringComponent]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    evidence_summary: Dict[str, Any]
    
    # Metadata
    timestamp: str
    processing_time: float
    methodology_version: str


class AdvancedRelevanceScorer:
    """
    Advanced relevance scoring engine combining multiple methodologies.
    """
    
    def __init__(self, 
                 use_semantic_similarity: bool = True,
                 semantic_weight: float = 0.4,
                 keyword_weight: float = 0.3,
                 experience_weight: float = 0.15,
                 skill_weight: float = 0.1,
                 certification_weight: float = 0.05):
        """
        Initialize the advanced relevance scorer.
        
        Args:
            use_semantic_similarity: Whether to use semantic similarity
            semantic_weight: Weight for semantic similarity component
            keyword_weight: Weight for hard keyword matching
            experience_weight: Weight for experience matching
            skill_weight: Weight for skill coverage
            certification_weight: Weight for certification matching
        """
        self.use_semantic_similarity = use_semantic_similarity and UTILS_AVAILABLE
        
        # Component weights (must sum to 1.0)
        self.weights = {
            'semantic_similarity': semantic_weight,
            'keyword_matching': keyword_weight, 
            'experience_matching': experience_weight,
            'skill_coverage': skill_weight,
            'certification_matching': certification_weight
        }
        
        # Validate weights
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights don't sum to 1.0 (sum={total_weight:.3f}), normalizing...")
            for key in self.weights:
                self.weights[key] /= total_weight
        
        # Initialize components
        if self.use_semantic_similarity:
            try:
                self.semantic_engine = create_enhanced_similarity_engine(use_transformers=True)
                self.skill_normalizer = create_skill_normalizer()
                logger.info("Semantic similarity engine initialized")
            except Exception as e:
                logger.warning(f"Semantic similarity initialization failed: {e}")
                self.use_semantic_similarity = False
        
        self.keyword_extractor = KeywordExtractor() if UTILS_AVAILABLE else None
        
        # Scoring thresholds
        self.suitability_thresholds = {
            SuitabilityLevel.HIGH: 75.0,
            SuitabilityLevel.MEDIUM: 50.0,
            SuitabilityLevel.LOW: 25.0
        }
        
        # Confidence calculation parameters
        self.confidence_factors = {
            'data_completeness': 0.3,
            'score_consistency': 0.25,
            'evidence_strength': 0.25,
            'methodology_reliability': 0.2
        }
        
        self.version = "2.0.0"
    
    def calculate_relevance_score(self, 
                                resume_data: Dict[str, Any],
                                job_description: Dict[str, Any],
                                include_explanations: bool = True) -> RelevanceScore:
        """
        Calculate comprehensive relevance score with explanations.
        
        Args:
            resume_data: Parsed resume data
            job_description: Job description data  
            include_explanations: Whether to include detailed explanations
            
        Returns:
            RelevanceScore object with comprehensive analysis
        """
        start_time = datetime.now()
        
        try:
            # Calculate individual scoring components
            components = []
            
            # 1. Keyword Matching Score
            keyword_component = self._calculate_keyword_matching(resume_data, job_description)
            components.append(keyword_component)
            
            # 2. Semantic Similarity Score
            semantic_component = self._calculate_semantic_similarity(resume_data, job_description)
            components.append(semantic_component)
            
            # 3. Experience Matching Score
            experience_component = self._calculate_experience_matching(resume_data, job_description)
            components.append(experience_component)
            
            # 4. Skill Coverage Score
            skill_component = self._calculate_skill_coverage(resume_data, job_description)
            components.append(skill_component)
            
            # 5. Certification Matching Score
            cert_component = self._calculate_certification_matching(resume_data, job_description)
            components.append(cert_component)
            
            # Calculate weighted overall score
            overall_score = sum(comp.score * comp.weight for comp in components)
            overall_score = max(0.0, min(100.0, overall_score))  # Normalize to 0-100
            
            # Determine suitability verdict
            suitability_verdict = self._determine_suitability(overall_score, components)
            
            # Calculate confidence metrics
            confidence_score, confidence_level = self._calculate_confidence(
                components, resume_data, job_description
            )
            
            # Generate insights
            strengths, weaknesses, recommendations = self._generate_insights(
                components, overall_score, resume_data, job_description
            ) if include_explanations else ([], [], [])
            
            # Create evidence summary
            evidence_summary = self._create_evidence_summary(components)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RelevanceScore(
                overall_score=overall_score,
                suitability_verdict=suitability_verdict,
                confidence_level=confidence_level,
                confidence_score=confidence_score,
                keyword_match_score=keyword_component.score,
                semantic_similarity_score=semantic_component.score,
                experience_match_score=experience_component.score,
                skill_coverage_score=skill_component.score,
                certification_match_score=cert_component.score,
                components=components,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                evidence_summary=evidence_summary,
                timestamp=start_time.isoformat(),
                processing_time=processing_time,
                methodology_version=self.version
            )
            
        except Exception as e:
            logger.error(f"Relevance scoring failed: {e}")
            # Return minimal score with error information
            return self._create_error_score(str(e), start_time)
    
    def _calculate_keyword_matching(self, resume_data: Dict, job_description: Dict) -> ScoringComponent:
        """Calculate hard keyword matching score."""
        try:
            resume_text = resume_data.get('full_text', '').lower()
            job_text = job_description.get('description', '').lower()
            
            # Extract keywords from job description
            required_keywords = set()
            preferred_keywords = set()
            
            # Get explicit skills
            required_skills = job_description.get('required_skills', [])
            preferred_skills = job_description.get('preferred_skills', [])
            
            required_keywords.update([skill.lower() for skill in required_skills])
            preferred_keywords.update([skill.lower() for skill in preferred_skills])
            
            # Extract additional keywords using regex patterns
            tech_patterns = [
                r'\b(python|java|javascript|react|node\.?js|sql|aws|docker|kubernetes)\b',
                r'\b(machine learning|deep learning|ai|ml|nlp|computer vision)\b',
                r'\b(agile|scrum|devops|ci/cd|microservices|api)\b'
            ]
            
            for pattern in tech_patterns:
                job_matches = re.findall(pattern, job_text, re.IGNORECASE)
                required_keywords.update([match.lower() for match in job_matches])
            
            # Count matches in resume
            required_matches = 0
            preferred_matches = 0
            matched_keywords = []
            
            for keyword in required_keywords:
                if keyword in resume_text:
                    required_matches += 1
                    matched_keywords.append(keyword)
            
            for keyword in preferred_keywords:
                if keyword in resume_text:
                    preferred_matches += 1
                    if keyword not in matched_keywords:
                        matched_keywords.append(keyword)
            
            # Calculate score
            total_required = len(required_keywords)
            total_preferred = len(preferred_keywords)
            
            if total_required == 0 and total_preferred == 0:
                score = 50.0  # Neutral score when no keywords specified
                confidence = 0.3
            else:
                required_score = (required_matches / total_required * 100) if total_required > 0 else 0
                preferred_score = (preferred_matches / total_preferred * 100) if total_preferred > 0 else 0
                
                # Weight required higher than preferred
                score = 0.8 * required_score + 0.2 * preferred_score
                confidence = min(0.9, (total_required + total_preferred) / 20)  # More keywords = higher confidence
            
            evidence = [
                f"Matched {required_matches}/{total_required} required keywords",
                f"Matched {preferred_matches}/{total_preferred} preferred keywords",
                f"Keywords found: {', '.join(matched_keywords[:5])}{'...' if len(matched_keywords) > 5 else ''}"
            ]
            
            return ScoringComponent(
                name="Keyword Matching",
                score=score,
                weight=self.weights['keyword_matching'],
                confidence=confidence,
                evidence=evidence,
                methodology="Hard keyword matching with regex patterns"
            )
            
        except Exception as e:
            logger.error(f"Keyword matching calculation failed: {e}")
            return ScoringComponent(
                name="Keyword Matching",
                score=0.0,
                weight=self.weights['keyword_matching'],
                confidence=0.1,
                evidence=[f"Error in calculation: {str(e)}"],
                methodology="Hard keyword matching (failed)"
            )
    
    def _calculate_semantic_similarity(self, resume_data: Dict, job_description: Dict) -> ScoringComponent:
        """Calculate semantic similarity score using transformers."""
        try:
            if not self.use_semantic_similarity:
                return ScoringComponent(
                    name="Semantic Similarity",
                    score=50.0,  # Neutral score
                    weight=self.weights['semantic_similarity'],
                    confidence=0.2,
                    evidence=["Semantic analysis not available"],
                    methodology="Fallback to neutral scoring"
                )
            
            # Use enhanced similarity engine
            similarity_result = self.semantic_engine.calculate_comprehensive_similarity(
                resume_data, job_description
            )
            
            # Extract semantic score (0-1) and convert to 0-100
            semantic_score = similarity_result.get('overall_similarity_score', 0.0) * 100
            
            # Calculate confidence based on component consistency
            component_scores = similarity_result.get('component_scores', {})
            score_variance = np.var(list(component_scores.values())) if component_scores else 0
            confidence = max(0.3, 1.0 - score_variance)  # Higher consistency = higher confidence
            
            # Extract evidence
            evidence = [
                f"Overall semantic similarity: {semantic_score:.1f}%",
                f"Text similarity: {component_scores.get('text_similarity', 0)*100:.1f}%",
                f"Skill similarity: {component_scores.get('skill_match', 0)*100:.1f}%"
            ]
            
            if 'transformer_similarity' in component_scores:
                evidence.append(f"Transformer similarity: {component_scores['transformer_similarity']*100:.1f}%")
            
            return ScoringComponent(
                name="Semantic Similarity",
                score=semantic_score,
                weight=self.weights['semantic_similarity'],
                confidence=confidence,
                evidence=evidence,
                methodology="Transformer-based semantic embedding similarity"
            )
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return ScoringComponent(
                name="Semantic Similarity",
                score=30.0,
                weight=self.weights['semantic_similarity'],
                confidence=0.1,
                evidence=[f"Error in semantic analysis: {str(e)}"],
                methodology="Semantic similarity (failed)"
            )
    
    def _calculate_experience_matching(self, resume_data: Dict, job_description: Dict) -> ScoringComponent:
        """Calculate experience matching score."""
        try:
            # Get experience data
            resume_experience = resume_data.get('experience', [])
            job_requirements = job_description.get('experience_requirements', {})
            
            # Calculate total years of experience
            total_years = sum(exp.get('years', 0) for exp in resume_experience)
            
            # Get required years
            required_years = job_requirements.get('min_years_experience', 0)
            preferred_years = job_requirements.get('preferred_years_experience', required_years + 2)
            
            # Calculate score based on experience
            if required_years == 0:
                score = 70.0  # Neutral score for no requirements
                confidence = 0.4
            elif total_years >= preferred_years:
                score = 95.0  # Exceeds preferred
                confidence = 0.9
            elif total_years >= required_years:
                # Linear scale between required and preferred
                ratio = (total_years - required_years) / max(1, preferred_years - required_years)
                score = 70.0 + (25.0 * ratio)
                confidence = 0.8
            else:
                # Below requirements
                ratio = total_years / max(1, required_years)
                score = max(10.0, 50.0 * ratio)
                confidence = 0.7
            
            # Analyze relevant experience
            relevant_keywords = job_requirements.get('relevant_keywords', [])
            relevant_experience = 0
            
            for exp in resume_experience:
                exp_desc = exp.get('description', '').lower()
                if any(keyword.lower() in exp_desc for keyword in relevant_keywords):
                    relevant_experience += exp.get('years', 0)
            
            # Adjust score based on relevance
            if relevant_keywords and relevant_experience > 0:
                relevance_bonus = min(15.0, (relevant_experience / max(1, total_years)) * 15)
                score += relevance_bonus
                confidence = min(0.95, confidence + 0.1)
            
            score = min(100.0, score)
            
            evidence = [
                f"Total experience: {total_years} years",
                f"Required: {required_years} years",
                f"Relevant experience: {relevant_experience} years",
                f"Experience level: {'Above requirements' if total_years >= required_years else 'Below requirements'}"
            ]
            
            return ScoringComponent(
                name="Experience Matching",
                score=score,
                weight=self.weights['experience_matching'],
                confidence=confidence,
                evidence=evidence,
                methodology="Years-based experience matching with relevance weighting"
            )
            
        except Exception as e:
            logger.error(f"Experience matching calculation failed: {e}")
            return ScoringComponent(
                name="Experience Matching",
                score=50.0,
                weight=self.weights['experience_matching'],
                confidence=0.2,
                evidence=[f"Error in experience analysis: {str(e)}"],
                methodology="Experience matching (failed)"
            )
    
    def _calculate_skill_coverage(self, resume_data: Dict, job_description: Dict) -> ScoringComponent:
        """Calculate skill coverage score."""
        try:
            resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
            required_skills = set(skill.lower() for skill in job_description.get('required_skills', []))
            preferred_skills = set(skill.lower() for skill in job_description.get('preferred_skills', []))
            
            if not required_skills and not preferred_skills:
                return ScoringComponent(
                    name="Skill Coverage",
                    score=60.0,
                    weight=self.weights['skill_coverage'],
                    confidence=0.3,
                    evidence=["No specific skills required"],
                    methodology="Neutral scoring for undefined requirements"
                )
            
            # Calculate coverage
            required_matches = len(resume_skills & required_skills)
            preferred_matches = len(resume_skills & preferred_skills)
            
            required_total = len(required_skills)
            preferred_total = len(preferred_skills)
            
            # Score calculation
            required_coverage = (required_matches / required_total * 100) if required_total > 0 else 100
            preferred_coverage = (preferred_matches / preferred_total * 100) if preferred_total > 0 else 100
            
            # Weight required skills higher
            score = 0.8 * required_coverage + 0.2 * preferred_coverage
            
            # Confidence based on skill count and matches
            total_skills = len(resume_skills)
            confidence = min(0.9, (total_skills + required_matches + preferred_matches) / 20)
            
            evidence = [
                f"Required skills coverage: {required_coverage:.1f}% ({required_matches}/{required_total})",
                f"Preferred skills coverage: {preferred_coverage:.1f}% ({preferred_matches}/{preferred_total})",
                f"Total resume skills: {total_skills}",
                f"Matched skills: {', '.join(list(resume_skills & (required_skills | preferred_skills))[:5])}"
            ]
            
            return ScoringComponent(
                name="Skill Coverage",
                score=score,
                weight=self.weights['skill_coverage'],
                confidence=confidence,
                evidence=evidence,
                methodology="Direct skill matching with required/preferred weighting"
            )
            
        except Exception as e:
            logger.error(f"Skill coverage calculation failed: {e}")
            return ScoringComponent(
                name="Skill Coverage",
                score=40.0,
                weight=self.weights['skill_coverage'],
                confidence=0.2,
                evidence=[f"Error in skill analysis: {str(e)}"],
                methodology="Skill coverage (failed)"
            )
    
    def _calculate_certification_matching(self, resume_data: Dict, job_description: Dict) -> ScoringComponent:
        """Calculate certification matching score."""
        try:
            resume_certs = set(cert.lower() for cert in resume_data.get('certifications', []))
            required_certs = set(cert.lower() for cert in job_description.get('required_certifications', []))
            preferred_certs = set(cert.lower() for cert in job_description.get('preferred_certifications', []))
            
            if not required_certs and not preferred_certs:
                return ScoringComponent(
                    name="Certification Matching",
                    score=70.0,
                    weight=self.weights['certification_matching'],
                    confidence=0.4,
                    evidence=["No certifications required"],
                    methodology="Neutral scoring for no requirements"
                )
            
            # Calculate matches
            required_matches = len(resume_certs & required_certs)
            preferred_matches = len(resume_certs & preferred_certs)
            
            required_total = len(required_certs)
            preferred_total = len(preferred_certs)
            
            # Score calculation
            if required_total > 0:
                required_score = (required_matches / required_total) * 100
                if required_matches == required_total:
                    score = 90.0 + min(10.0, preferred_matches * 2)  # Bonus for preferred
                elif required_matches > 0:
                    score = 50.0 + (required_score * 0.4)
                else:
                    score = max(20.0, preferred_matches * 10)  # Some credit for preferred
            else:
                # Only preferred certifications
                score = min(80.0, preferred_matches * 20)
            
            confidence = 0.8 if (required_total + preferred_total) > 0 else 0.4
            
            evidence = [
                f"Required certifications: {required_matches}/{required_total}",
                f"Preferred certifications: {preferred_matches}/{preferred_total}",
                f"Resume certifications: {len(resume_certs)}"
            ]
            
            if resume_certs & (required_certs | preferred_certs):
                matched = list(resume_certs & (required_certs | preferred_certs))
                evidence.append(f"Matched: {', '.join(matched[:3])}")
            
            return ScoringComponent(
                name="Certification Matching",
                score=score,
                weight=self.weights['certification_matching'],
                confidence=confidence,
                evidence=evidence,
                methodology="Direct certification matching with required/preferred weighting"
            )
            
        except Exception as e:
            logger.error(f"Certification matching calculation failed: {e}")
            return ScoringComponent(
                name="Certification Matching",
                score=50.0,
                weight=self.weights['certification_matching'],
                confidence=0.2,
                evidence=[f"Error in certification analysis: {str(e)}"],
                methodology="Certification matching (failed)"
            )
    
    def _determine_suitability(self, overall_score: float, components: List[ScoringComponent]) -> SuitabilityLevel:
        """Determine suitability verdict based on score and components."""
        # Basic thresholds
        if overall_score >= self.suitability_thresholds[SuitabilityLevel.HIGH]:
            return SuitabilityLevel.HIGH
        elif overall_score >= self.suitability_thresholds[SuitabilityLevel.MEDIUM]:
            return SuitabilityLevel.MEDIUM
        elif overall_score >= self.suitability_thresholds[SuitabilityLevel.LOW]:
            return SuitabilityLevel.LOW
        else:
            # Check if we have insufficient data
            low_confidence_count = sum(1 for comp in components if comp.confidence < 0.3)
            if low_confidence_count >= len(components) / 2:
                return SuitabilityLevel.INSUFFICIENT_DATA
            return SuitabilityLevel.LOW
    
    def _calculate_confidence(self, components: List[ScoringComponent], 
                            resume_data: Dict, job_description: Dict) -> Tuple[float, ConfidenceLevel]:
        """Calculate overall confidence in the scoring."""
        try:
            # Data completeness factor
            resume_completeness = self._assess_data_completeness(resume_data)
            job_completeness = self._assess_data_completeness(job_description)
            data_completeness = (resume_completeness + job_completeness) / 2
            
            # Score consistency factor
            component_scores = [comp.score for comp in components]
            score_variance = np.var(component_scores) if len(component_scores) > 1 else 0
            score_consistency = max(0.0, 1.0 - (score_variance / 1000))  # Normalize variance
            
            # Evidence strength factor
            avg_component_confidence = np.mean([comp.confidence for comp in components])
            evidence_strength = avg_component_confidence
            
            # Methodology reliability factor
            semantic_available = any(comp.name == "Semantic Similarity" and comp.confidence > 0.5 
                                   for comp in components)
            methodology_reliability = 0.9 if semantic_available else 0.6
            
            # Weighted confidence calculation
            confidence_score = (
                data_completeness * self.confidence_factors['data_completeness'] +
                score_consistency * self.confidence_factors['score_consistency'] +
                evidence_strength * self.confidence_factors['evidence_strength'] +
                methodology_reliability * self.confidence_factors['methodology_reliability']
            )
            
            # Determine confidence level
            if confidence_score >= 0.85:
                confidence_level = ConfidenceLevel.VERY_HIGH
            elif confidence_score >= 0.70:
                confidence_level = ConfidenceLevel.HIGH
            elif confidence_score >= 0.55:
                confidence_level = ConfidenceLevel.MODERATE
            elif confidence_score >= 0.35:
                confidence_level = ConfidenceLevel.LOW
            else:
                confidence_level = ConfidenceLevel.VERY_LOW
            
            return confidence_score, confidence_level
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.3, ConfidenceLevel.LOW
    
    def _assess_data_completeness(self, data: Dict) -> float:
        """Assess completeness of data for confidence calculation."""
        completeness = 0.0
        total_factors = 0
        
        # Check for key data elements
        key_fields = ['skills', 'experience', 'description', 'full_text']
        for field in key_fields:
            total_factors += 1
            if field in data and data[field]:
                if isinstance(data[field], list):
                    completeness += min(1.0, len(data[field]) / 3)  # More items = better
                elif isinstance(data[field], str):
                    completeness += min(1.0, len(data[field]) / 100)  # Longer text = better
                else:
                    completeness += 0.5
        
        return completeness / total_factors if total_factors > 0 else 0.0
    
    def _generate_insights(self, components: List[ScoringComponent], 
                          overall_score: float, resume_data: Dict, 
                          job_description: Dict) -> Tuple[List[str], List[str], List[str]]:
        """Generate strengths, weaknesses, and recommendations."""
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyze component performance
        for comp in components:
            weighted_contribution = comp.score * comp.weight
            
            if comp.score >= 75.0:
                strengths.append(f"Strong {comp.name.lower()}: {comp.score:.1f}%")
            elif comp.score <= 40.0:
                weaknesses.append(f"Weak {comp.name.lower()}: {comp.score:.1f}%")
                
                # Generate specific recommendations
                if comp.name == "Keyword Matching":
                    recommendations.append("Include more relevant technical keywords in resume")
                elif comp.name == "Skill Coverage":
                    recommendations.append("Develop skills in required technologies")
                elif comp.name == "Experience Matching":
                    recommendations.append("Highlight relevant project experience")
                elif comp.name == "Certification Matching":
                    recommendations.append("Consider obtaining relevant certifications")
        
        # Overall performance insights
        if overall_score >= 80:
            strengths.append(f"Excellent overall match: {overall_score:.1f}%")
        elif overall_score <= 30:
            weaknesses.append(f"Low overall relevance: {overall_score:.1f}%")
        
        return strengths, weaknesses, recommendations
    
    def _create_evidence_summary(self, components: List[ScoringComponent]) -> Dict[str, Any]:
        """Create summary of evidence from all components."""
        summary = {
            'total_evidence_points': sum(len(comp.evidence) for comp in components),
            'average_confidence': np.mean([comp.confidence for comp in components]),
            'methodology_mix': [comp.methodology for comp in components],
            'component_contributions': {
                comp.name: {
                    'weighted_score': comp.score * comp.weight,
                    'confidence': comp.confidence,
                    'evidence_count': len(comp.evidence)
                } for comp in components
            }
        }
        return summary
    
    def _create_error_score(self, error_message: str, start_time: datetime) -> RelevanceScore:
        """Create minimal error score when calculation fails."""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return RelevanceScore(
            overall_score=0.0,
            suitability_verdict=SuitabilityLevel.INSUFFICIENT_DATA,
            confidence_level=ConfidenceLevel.VERY_LOW,
            confidence_score=0.0,
            keyword_match_score=0.0,
            semantic_similarity_score=0.0,
            experience_match_score=0.0,
            skill_coverage_score=0.0,
            certification_match_score=0.0,
            components=[],
            strengths=[],
            weaknesses=[f"Scoring failed: {error_message}"],
            recommendations=["Please check input data quality and try again"],
            evidence_summary={'error': error_message},
            timestamp=start_time.isoformat(),
            processing_time=processing_time,
            methodology_version=self.version
        )


def create_advanced_scorer(**kwargs) -> AdvancedRelevanceScorer:
    """Create an advanced relevance scorer with default settings."""
    return AdvancedRelevanceScorer(**kwargs)


if __name__ == "__main__":
    # Test the advanced scoring system
    print("🎯 Testing Advanced Relevance Scoring System")
    print("=" * 50)
    
    # Sample data
    sample_resume = {
        'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Data Analysis', 'SQL'],
        'experience': [
            {'title': 'Data Scientist', 'years': 3, 'description': 'ML model development'},
            {'title': 'Analyst', 'years': 2, 'description': 'Data analysis and visualization'}
        ],
        'certifications': ['AWS Machine Learning'],
        'full_text': '''
        Experienced Data Scientist with 5 years of experience in machine learning,
        Python development, and data analysis. Skilled in TensorFlow, scikit-learn,
        and SQL databases. AWS certified ML professional with proven track record
        of deploying production ML models.
        '''
    }
    
    sample_job = {
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning'],
        'preferred_skills': ['TensorFlow', 'AWS', 'SQL'],
        'required_certifications': ['AWS Machine Learning'],
        'preferred_certifications': ['TensorFlow Developer Certificate'],
        'experience_requirements': {
            'min_years_experience': 3,
            'relevant_keywords': ['machine learning', 'python', 'data science']
        },
        'description': '''
        We are looking for a Senior Data Scientist with expertise in machine learning
        and deep learning. The candidate should have strong Python skills and experience
        with TensorFlow. AWS experience is preferred for model deployment.
        '''
    }
    
    try:
        # Create scorer
        scorer = create_advanced_scorer()
        
        # Calculate score
        result = scorer.calculate_relevance_score(sample_resume, sample_job)
        
        # Display results
        print(f"\n📊 SCORING RESULTS:")
        print(f"Overall Score: {result.overall_score:.1f}/100")
        print(f"Suitability: {result.suitability_verdict.value}")
        print(f"Confidence: {result.confidence_level.value} ({result.confidence_score:.2f})")
        
        print(f"\n🔍 COMPONENT BREAKDOWN:")
        for comp in result.components:
            print(f"  {comp.name}: {comp.score:.1f}% (weight: {comp.weight:.2f}, confidence: {comp.confidence:.2f})")
        
        print(f"\n💪 STRENGTHS:")
        for strength in result.strengths:
            print(f"  • {strength}")
        
        print(f"\n⚠️  WEAKNESSES:")
        for weakness in result.weaknesses:
            print(f"  • {weakness}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        for recommendation in result.recommendations:
            print(f"  • {recommendation}")
        
        print(f"\n⏱️ Performance: {result.processing_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
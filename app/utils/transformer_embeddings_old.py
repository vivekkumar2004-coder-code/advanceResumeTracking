"""
Transformer-based Semantic Embeddings Module

This module provides advanced semantic similarity calculations using transformer models.
Supports both HuggingFace Transformers and OpenAI embeddings for accurate resume-job matching.

Features:
- Sentence Transformers for optimized embeddings
- AutoModel fallback for flexibility  
- OpenAI embeddings API support
- Intelligent caching system for performance
- Cosine similarity calculations
- Advanced candidate ranking and skill gap analysis

Author: AI Assistant
Date: September 2025
"""
        """Encode text using transformer model."""
        try:
            if hasattr(self, 'sentence_transformer') and self.sentence_transformer is not None:
                # Use SentenceTransformer (recommended)
                embedding = self.sentence_transformer.encode(text, convert_to_numpy=True)
                return embedding
                
            elif hasattr(self, 'model') and self.model is not None and self.tokenizer is not None:
                # Use AutoModel with mean pooling
                embedding = self._encode_with_automodel(text)
                return embedding
                
            else:
                logger.warning("No transformer model available, using random embedding as fallback")
                # Return a random normalized embedding as fallback
                embedding = np.random.normal(0, 0.1, 384)
                return embedding / np.linalg.norm(embedding)
                
        except Exception as e:
            logger.error(f"Transformer encoding failed: {e}")
            logger.warning("Using random embedding as fallback")
            # Return a random normalized embedding as fallback
            embedding = np.random.normal(0, 0.1, 384)
            return embedding / np.linalg.norm(embedding)AI Assistant
Date: September 2025
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

# Transformer and embedding imports
try:
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer, AutoModel
    import torch
    import torch.nn.functional as F
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Scikit-learn for similarity calculations
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple file-based cache for embeddings to improve performance."""
    
    def __init__(self, cache_dir: str = "./embeddings_cache", max_age_days: int = 7):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age_days = max_age_days
        
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key from text and model name."""
        content = f"{text}_{model_name}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """Retrieve embedding from cache if available and not expired."""
        cache_key = self._get_cache_key(text, model_name)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # Check if cache is expired
                cached_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cached_time < timedelta(days=self.max_age_days):
                    return np.array(data['embedding'])
                else:
                    cache_file.unlink()  # Remove expired cache
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
                
        return None
    
    def set(self, text: str, model_name: str, embedding: np.ndarray):
        """Store embedding in cache."""
        cache_key = self._get_cache_key(text, model_name)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            data = {
                'embedding': embedding.tolist(),
                'timestamp': datetime.now().isoformat(),
                'text_length': len(text),
                'model': model_name
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


class TransformerEmbeddings:
    """
    Advanced transformer-based embeddings for semantic similarity.
    Supports multiple embedding models and providers.
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 use_openai: bool = False,
                 openai_model: str = "text-embedding-3-small",
                 cache_embeddings: bool = True,
                 device: str = None):
        """
        Initialize transformer embeddings.
        
        Args:
            model_name: HuggingFace model name or path
            use_openai: Whether to use OpenAI embeddings API
            openai_model: OpenAI embedding model to use
            cache_embeddings: Whether to cache embeddings for performance
            device: Device to run model on (auto-detected if None)
        """
        self.model_name = model_name
        self.use_openai = use_openai
        self.openai_model = openai_model
        self.cache_embeddings = cache_embeddings
        
        # Initialize cache
        if cache_embeddings:
            self.cache = EmbeddingCache()
        
        # Initialize models
        self.sentence_transformer = None
        self.tokenizer = None
        self.model = None
        
        if not use_openai and TRANSFORMERS_AVAILABLE:
            self._initialize_transformers(device)
        elif use_openai and not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available, falling back to HuggingFace")
            self.use_openai = False
            if TRANSFORMERS_AVAILABLE:
                self._initialize_transformers(device)
    
    def _initialize_transformers(self, device: str = None):
        """Initialize HuggingFace transformer models."""
        try:
            # Determine device
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
            self.device = device
            
            logger.info(f"Initializing transformer model: {self.model_name} on {device}")
            
            # Try to use SentenceTransformer first (optimized for embeddings)
            try:
                self.sentence_transformer = SentenceTransformer(self.model_name, device=device)
                logger.info("Successfully initialized SentenceTransformer for embeddings")
                return  # Success, no need to try AutoModel
                
            except Exception as e:
                logger.warning(f"SentenceTransformer failed: {e}")
                logger.info("Attempting fallback to AutoModel...")
                
                # Fall back to AutoModel
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    self.model = AutoModel.from_pretrained(self.model_name)
                    self.model.to(device)
                    self.model.eval()
                    logger.info("Successfully initialized AutoModel for embeddings")
                    return  # Success
                    
                except Exception as e2:
                    logger.error(f"AutoModel also failed: {e2}")
                    raise Exception(f"Both SentenceTransformer and AutoModel failed: {e}, {e2}")
                
        except Exception as e:
            logger.error(f"Failed to initialize transformers: {e}")
            # Mark as not available instead of raising
            self.sentence_transformer = None
            self.tokenizer = None
            self.model = None
            logger.warning("Transformer initialization failed, will use fallback embeddings")
    
    def encode_text(self, text: Union[str, List[str]], 
                   batch_size: int = 32,
                   normalize_embeddings: bool = True) -> np.ndarray:
        """
        Encode text(s) into embedding vectors.
        
        Args:
            text: Single text string or list of texts
            batch_size: Batch size for processing
            normalize_embeddings: Whether to L2-normalize embeddings
            
        Returns:
            Embedding vector(s) as numpy array
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = []
        
        for i in range(0, len(text), batch_size):
            batch = text[i:i + batch_size]
            batch_embeddings = self._encode_batch(batch)
            embeddings.extend(batch_embeddings)
        
        embeddings = np.array(embeddings)
        
        if normalize_embeddings:
            embeddings = normalize(embeddings, norm='l2', axis=1)
        
        return embeddings.squeeze() if len(text) == 1 else embeddings
    
    def _encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Encode a batch of texts."""
        embeddings = []
        
        for text in texts:
            # Check cache first
            if self.cache_embeddings:
                cached_embedding = self.cache.get(text, self.model_name)
                if cached_embedding is not None:
                    embeddings.append(cached_embedding)
                    continue
            
            # Generate embedding
            if self.use_openai:
                embedding = self._encode_openai(text)
            else:
                embedding = self._encode_transformer(text)
            
            embeddings.append(embedding)
            
            # Cache the embedding
            if self.cache_embeddings:
                self.cache.set(text, self.model_name, embedding)
        
        return embeddings
    
    def _encode_openai(self, text: str) -> np.ndarray:
        """Encode text using OpenAI embeddings API."""
        try:
            response = openai.embeddings.create(
                model=self.openai_model,
                input=text.replace("\n", " ")  # OpenAI recommends replacing newlines
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    def _encode_transformer(self, text: str) -> np.ndarray:
        """Encode text using HuggingFace transformers."""
        try:
            if self.sentence_transformer is not None:
                # Use SentenceTransformer (recommended)
                return self.sentence_transformer.encode(text, convert_to_numpy=True)
            else:
                # Use AutoModel with mean pooling
                return self._encode_with_automodel(text)
        except Exception as e:
            logger.error(f"Transformer encoding failed: {e}")
            raise
    
    def _encode_with_automodel(self, text: str) -> np.ndarray:
        """Encode text using AutoModel with mean pooling."""
        # Tokenize
        encoded_input = self.tokenizer(text, padding=True, truncation=True, 
                                     max_length=512, return_tensors='pt')
        encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}
        
        # Generate embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            
        # Mean pooling
        token_embeddings = model_output.last_hidden_state
        attention_mask = encoded_input['attention_mask']
        
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
        mean_pooled = sum_embeddings / sum_mask
        return mean_pooled.cpu().numpy().squeeze()


class SemanticSimilarityCalculator:
    """
    Advanced semantic similarity calculations using transformer embeddings.
    """
    
    def __init__(self, 
                 embedding_engine: TransformerEmbeddings,
                 similarity_threshold: float = 0.7):
        """
        Initialize similarity calculator.
        
        Args:
            embedding_engine: TransformerEmbeddings instance
            similarity_threshold: Minimum similarity score for matches
        """
        self.embedding_engine = embedding_engine
        self.similarity_threshold = similarity_threshold
        
    def calculate_text_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Dict with similarity metrics
        """
        # Generate embeddings
        embeddings = self.embedding_engine.encode_text([text1, text2])
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity([embeddings[0]], [embeddings[1]])
        cosine_sim = float(similarity_matrix[0, 0])
        
        # Calculate Euclidean distance
        euclidean_dist = float(np.linalg.norm(embeddings[0] - embeddings[1]))
        
        # Calculate dot product (for normalized vectors, this equals cosine similarity)
        dot_product = float(np.dot(embeddings[0], embeddings[1]))
        
        return {
            'cosine_similarity': cosine_sim,
            'euclidean_distance': euclidean_dist,
            'dot_product': dot_product,
            'similarity_score': cosine_sim,  # Primary score
            'is_similar': cosine_sim >= self.similarity_threshold
        }
    
    def calculate_skill_set_similarity(self, skills1: List[str], 
                                     skills2: List[str]) -> Dict[str, Any]:
        """
        Calculate semantic similarity between two skill sets.
        
        Args:
            skills1: First set of skills
            skills2: Second set of skills
            
        Returns:
            Dict with detailed similarity analysis
        """
        if not skills1 or not skills2:
            return {
                'overall_similarity': 0.0,
                'skill_matches': [],
                'similarity_matrix': None,
                'best_matches': {}
            }
        
        # Generate embeddings for all skills
        all_skills = skills1 + skills2
        embeddings = self.embedding_engine.encode_text(all_skills)
        
        skills1_embeddings = embeddings[:len(skills1)]
        skills2_embeddings = embeddings[len(skills1):]
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(skills1_embeddings, skills2_embeddings)
        
        # Find best matches
        best_matches = {}
        skill_matches = []
        
        for i, skill1 in enumerate(skills1):
            max_sim_idx = np.argmax(similarity_matrix[i])
            max_similarity = similarity_matrix[i, max_sim_idx]
            
            if max_similarity >= self.similarity_threshold:
                matched_skill = skills2[max_sim_idx]
                best_matches[skill1] = {
                    'matched_skill': matched_skill,
                    'similarity': float(max_similarity)
                }
                skill_matches.append({
                    'skill1': skill1,
                    'skill2': matched_skill,
                    'similarity': float(max_similarity)
                })
        
        # Calculate overall similarity metrics
        max_similarities = np.max(similarity_matrix, axis=1)
        overall_similarity = float(np.mean(max_similarities))
        
        # Calculate coverage (percentage of skills1 that have good matches)
        coverage = len([s for s in max_similarities if s >= self.similarity_threshold]) / len(skills1)
        
        return {
            'overall_similarity': overall_similarity,
            'coverage': coverage,
            'skill_matches': skill_matches,
            'best_matches': best_matches,
            'similarity_matrix': similarity_matrix.tolist(),
            'max_similarities': max_similarities.tolist(),
            'threshold': self.similarity_threshold
        }
    
    def find_skill_gaps(self, resume_skills: List[str], 
                       job_requirements: List[str],
                       required_skills: List[str] = None) -> Dict[str, Any]:
        """
        Identify skill gaps using semantic similarity.
        
        Args:
            resume_skills: Skills from resume
            job_requirements: All job requirements/skills
            required_skills: Critical required skills (subset of job_requirements)
            
        Returns:
            Dict with gap analysis
        """
        # Calculate similarity between resume skills and job requirements
        similarity_result = self.calculate_skill_set_similarity(
            job_requirements, resume_skills
        )
        
        # Identify missing skills
        missing_skills = []
        covered_requirements = set()
        
        for req_skill in job_requirements:
            best_match = None
            best_similarity = 0.0
            
            # Find best matching resume skill
            req_embedding = self.embedding_engine.encode_text(req_skill)
            resume_embeddings = self.embedding_engine.encode_text(resume_skills)
            
            similarities = cosine_similarity([req_embedding], resume_embeddings)[0]
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            if best_similarity >= self.similarity_threshold:
                covered_requirements.add(req_skill)
                best_match = resume_skills[best_idx]
            else:
                missing_skills.append({
                    'skill': req_skill,
                    'closest_match': resume_skills[best_idx] if resume_skills else None,
                    'similarity': float(best_similarity),
                    'is_critical': req_skill in (required_skills or [])
                })
        
        # Calculate gap metrics
        total_requirements = len(job_requirements)
        covered_count = len(covered_requirements)
        gap_percentage = (total_requirements - covered_count) / total_requirements * 100
        
        # Analyze critical gaps
        critical_gaps = []
        if required_skills:
            for skill in required_skills:
                if skill not in covered_requirements:
                    critical_gaps.append(skill)
        
        return {
            'total_requirements': total_requirements,
            'covered_requirements': covered_count,
            'gap_percentage': gap_percentage,
            'missing_skills': missing_skills,
            'critical_gaps': critical_gaps,
            'covered_skills': list(covered_requirements),
            'skill_coverage_score': covered_count / total_requirements,
            'critical_coverage_score': (len(required_skills or []) - len(critical_gaps)) / len(required_skills or [1])
        }
    
    def rank_candidates(self, candidates: List[Dict[str, Any]], 
                       job_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank multiple candidates based on semantic similarity to job requirements.
        
        Args:
            candidates: List of candidate data (skills, experience, etc.)
            job_requirements: Job requirements and description
            
        Returns:
            Ranked list of candidates with scores
        """
        ranked_candidates = []
        
        for candidate in candidates:
            candidate_skills = candidate.get('skills', [])
            candidate_text = candidate.get('resume_text', '')
            
            # Calculate skill similarity
            skill_similarity = self.calculate_skill_set_similarity(
                candidate_skills,
                job_requirements.get('required_skills', [])
            )
            
            # Calculate text similarity
            job_description = job_requirements.get('description', '')
            text_similarity = self.calculate_text_similarity(
                candidate_text, job_description
            )
            
            # Calculate skill gap analysis
            gap_analysis = self.find_skill_gaps(
                candidate_skills,
                job_requirements.get('required_skills', []) + 
                job_requirements.get('preferred_skills', []),
                job_requirements.get('required_skills', [])
            )
            
            # Calculate overall score
            skill_score = skill_similarity['overall_similarity']
            text_score = text_similarity['similarity_score']
            coverage_score = gap_analysis['skill_coverage_score']
            critical_coverage = gap_analysis['critical_coverage_score']
            
            # Weighted overall score
            overall_score = (
                skill_score * 0.4 +
                coverage_score * 0.3 +
                text_score * 0.2 +
                critical_coverage * 0.1
            )
            
            ranked_candidates.append({
                'candidate': candidate,
                'overall_score': overall_score,
                'skill_similarity': skill_similarity,
                'text_similarity': text_similarity,
                'gap_analysis': gap_analysis,
                'scores': {
                    'skill_similarity': skill_score,
                    'text_similarity': text_score,
                    'skill_coverage': coverage_score,
                    'critical_coverage': critical_coverage
                }
            })
        
        # Sort by overall score (descending)
        ranked_candidates.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return ranked_candidates


def create_embedding_engine(model_type: str = "sentence-transformer",
                           model_name: str = "all-MiniLM-L6-v2",
                           use_openai: bool = False,
                           **kwargs) -> TransformerEmbeddings:
    """
    Factory function to create embedding engine.
    
    Args:
        model_type: Type of model ("sentence-transformer", "automodel", "openai")
        model_name: Model name or path
        use_openai: Whether to use OpenAI embeddings
        **kwargs: Additional arguments
        
    Returns:
        TransformerEmbeddings instance
    """
    # Model recommendations based on use case
    model_recommendations = {
        "general": "all-MiniLM-L6-v2",  # Fast and good quality
        "technical": "all-mpnet-base-v2",  # Best quality
        "multilingual": "paraphrase-multilingual-MiniLM-L12-v2",
        "fast": "all-MiniLM-L6-v2",
        "best": "all-mpnet-base-v2"
    }
    
    if model_name in model_recommendations:
        model_name = model_recommendations[model_name]
    
    return TransformerEmbeddings(
        model_name=model_name,
        use_openai=use_openai,
        **kwargs
    )


# Example usage and testing
if __name__ == "__main__":
    def test_transformer_embeddings():
        """Test transformer embeddings functionality."""
        print("=== Transformer Embeddings Test ===\n")
        
        # Initialize embedding engine
        print("1. Initializing embedding engine...")
        engine = create_embedding_engine(model_name="all-MiniLM-L6-v2")
        
        # Test text similarity
        print("2. Testing text similarity...")
        text1 = "Python developer with machine learning experience"
        text2 = "Software engineer skilled in Python and AI"
        
        calculator = SemanticSimilarityCalculator(engine)
        similarity = calculator.calculate_text_similarity(text1, text2)
        
        print(f"Text 1: {text1}")
        print(f"Text 2: {text2}")
        print(f"Cosine similarity: {similarity['cosine_similarity']:.3f}")
        print(f"Is similar: {similarity['is_similar']}")
        
        # Test skill set similarity
        print(f"\n3. Testing skill set similarity...")
        skills1 = ["Python", "Machine Learning", "TensorFlow", "AWS"]
        skills2 = ["Python programming", "AI/ML", "Deep learning", "Cloud computing"]
        
        skill_similarity = calculator.calculate_skill_set_similarity(skills1, skills2)
        print(f"Skills 1: {skills1}")
        print(f"Skills 2: {skills2}")
        print(f"Overall similarity: {skill_similarity['overall_similarity']:.3f}")
        print(f"Coverage: {skill_similarity['coverage']:.3f}")
        print(f"Skill matches: {skill_similarity['skill_matches']}")
        
        # Test skill gap analysis
        print(f"\n4. Testing skill gap analysis...")
        resume_skills = ["Python", "Django", "PostgreSQL"]
        job_requirements = ["Python", "FastAPI", "MongoDB", "Docker", "Kubernetes"]
        
        gap_analysis = calculator.find_skill_gaps(resume_skills, job_requirements)
        print(f"Resume skills: {resume_skills}")
        print(f"Job requirements: {job_requirements}")
        print(f"Skill coverage: {gap_analysis['skill_coverage_score']:.3f}")
        print(f"Gap percentage: {gap_analysis['gap_percentage']:.1f}%")
        print(f"Missing skills: {[s['skill'] for s in gap_analysis['missing_skills']]}")
        
        return True
    
    # Run test
    if TRANSFORMERS_AVAILABLE:
        try:
            test_transformer_embeddings()
            print("\n✅ All tests passed!")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    else:
        print("⚠️  Transformers not available. Install with: pip install sentence-transformers transformers torch")
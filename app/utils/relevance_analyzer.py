import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np

# Import advanced scorer and feedback generator
try:
    from .advanced_scorer import create_advanced_scorer, AdvancedRelevanceScorer
    ADVANCED_SCORER_AVAILABLE = True
except ImportError:
    ADVANCED_SCORER_AVAILABLE = False
    print("Warning: Advanced scorer not available, using legacy methods")

try:
    from .feedback_generator import (
        LLMFeedbackGenerator, FeedbackRequest, FeedbackType, FeedbackTone, 
        LLMProvider, generate_candidate_feedback
    )
    FEEDBACK_GENERATOR_AVAILABLE = True
except ImportError:
    FEEDBACK_GENERATOR_AVAILABLE = False
    print("Warning: Feedback generator not available")

# Download required NLTK data (will only download if not already present)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def preprocess_text(text):
    """Clean and preprocess text for analysis"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def truncate_text(text, max_length=500, add_ellipsis=True):
    """
    Truncate text to a maximum length with optional ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum character length
        add_ellipsis: Add "..." at the end if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    if add_ellipsis:
        # Try to truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # Only if we don't lose too much text
            truncated = truncated[:last_space]
        truncated += "..."
    
    return truncated

def limit_list_items(items, max_items=10, item_name="items"):
    """
    Limit list items and return summary info
    
    Args:
        items: List of items
        max_items: Maximum items to include
        item_name: Name for the items (for summary)
    
    Returns:
        Dictionary with limited items and summary info
    """
    if not items:
        return {"items": [], "total_count": 0, "truncated": False, "summary": f"No {item_name} found"}
    
    limited_items = items[:max_items]
    truncated = len(items) > max_items
    
    return {
        "items": limited_items,
        "total_count": len(items),
        "truncated": truncated,
        "hidden_count": len(items) - max_items if truncated else 0,
        "summary": f"Showing {len(limited_items)} of {len(items)} {item_name}" if truncated else f"{len(items)} {item_name}"
    }

def extract_skills_and_keywords(text, custom_skills=None, max_skills=50):
    """
    Extract skills and keywords from text with output limits
    
    Args:
        text: Text to analyze
        custom_skills: Custom skills list
        max_skills: Maximum number of skills to return
    
    Returns:
        List of found skills (limited to max_skills)
    """
    
    # Common technical skills and keywords
    default_skills = [
        # Programming languages
        'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
        'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
        
        # Web technologies
        'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
        'spring', 'laravel', 'rails', 'asp.net', 'bootstrap', 'jquery', 'typescript',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis', 'elasticsearch',
        'nosql', 'database', 'dba',
        
        # Cloud and DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
        'ci/cd', 'devops', 'terraform', 'ansible', 'chef', 'puppet',
        
        # Data Science and AI
        'machine learning', 'deep learning', 'neural networks', 'tensorflow', 'pytorch',
        'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark',
        'hadoop', 'tableau', 'powerbi', 'excel', 'statistics', 'analytics',
        
        # Other technical skills
        'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'kanban', 'jira',
        'linux', 'windows', 'unix', 'networking', 'security', 'testing', 'debugging'
    ]
    
    skills = custom_skills if custom_skills else default_skills
    processed_text = preprocess_text(text)
    
    found_skills = []
    for skill in skills:
        if skill.lower() in processed_text:
            found_skills.append(skill)
    
    # Limit output and sort by relevance (alphabetically for now)
    found_skills.sort()
    return found_skills[:max_skills]

def calculate_keyword_frequency(text, keywords):
    """Calculate frequency of keywords in text"""
    processed_text = preprocess_text(text)
    word_freq = {}
    
    for keyword in keywords:
        count = processed_text.count(keyword.lower())
        if count > 0:
            word_freq[keyword] = count
    
    return word_freq

def calculate_tfidf_similarity(resume_text, job_desc_text):
    """Calculate TF-IDF based similarity between resume and job description"""
    try:
        # Preprocess texts
        resume_processed = preprocess_text(resume_text)
        job_desc_processed = preprocess_text(job_desc_text)
        
        if not resume_processed or not job_desc_processed:
            return 0.0
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)  # Include both unigrams and bigrams
        )
        
        tfidf_matrix = vectorizer.fit_transform([resume_processed, job_desc_processed])
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        return float(similarity_matrix[0][0])
    
    except Exception as e:
        print(f"Error calculating TF-IDF similarity: {str(e)}")
        return 0.0

def analyze_resume_relevance(resume_text, job_desc_text, max_skills_display=20):
    """
    Comprehensive analysis of resume relevance to job description with output limits
    
    Args:
        resume_text: Resume text content
        job_desc_text: Job description text content
        max_skills_display: Maximum number of skills to display in results
    
    Returns:
        Dictionary with analysis results (with limited output)
    """
    
    # Extract skills from job description (limit to reasonable number)
    job_skills = extract_skills_and_keywords(job_desc_text, max_skills=50)
    resume_skills = extract_skills_and_keywords(resume_text, max_skills=50)
    
    # Find matching skills
    matching_skills = list(set(job_skills) & set(resume_skills))
    missing_skills = list(set(job_skills) - set(resume_skills))
    
    # Calculate skill match percentage
    skill_match_percentage = len(matching_skills) / len(job_skills) * 100 if job_skills else 0
    
    # Calculate TF-IDF similarity
    tfidf_similarity = calculate_tfidf_similarity(resume_text, job_desc_text)
    
    # Calculate keyword frequency for matching skills
    keyword_frequency = calculate_keyword_frequency(resume_text, matching_skills[:10])  # Limit to top 10
    
    # Calculate overall relevance score (weighted combination)
    relevance_score = (skill_match_percentage * 0.4 + tfidf_similarity * 100 * 0.6)
    
    # Determine relevance level
    if relevance_score >= 75:
        relevance_level = "High"
    elif relevance_score >= 50:
        relevance_level = "Medium"
    elif relevance_score >= 25:
        relevance_level = "Low"
    else:
        relevance_level = "Very Low"
    
    # Extract key phrases from job description (limited)
    job_key_phrases = extract_key_phrases(job_desc_text, max_phrases=10)
    
    # Limit skills output for better UX
    matching_skills_limited = limit_list_items(matching_skills, max_skills_display, "matching skills")
    missing_skills_limited = limit_list_items(missing_skills, max_skills_display, "missing skills")
    
    return {
        'relevance_score': round(relevance_score, 2),
        'relevance_level': relevance_level,
        'skill_match_percentage': round(skill_match_percentage, 2),
        'tfidf_similarity': round(tfidf_similarity, 4),
        
        # Limited skill outputs for UI
        'matching_skills': matching_skills_limited["items"],
        'missing_skills': missing_skills_limited["items"],
        'total_matching_skills': len(matching_skills),
        'total_missing_skills': len(missing_skills),
        'matching_skills_summary': matching_skills_limited["summary"],
        'missing_skills_summary': missing_skills_limited["summary"],
        
        # Full data for backend processing
        'all_matching_skills': matching_skills,
        'all_missing_skills': missing_skills,
        
        'total_job_skills': len(job_skills),
        'keyword_frequency': keyword_frequency,
        'job_key_phrases': job_key_phrases[:10],  # Top 10 key phrases
        'recommendations': generate_recommendations(missing_skills[:5], relevance_score)  # Limit recommendations
    }

def extract_key_phrases(text, max_phrases=20):
    """Extract key phrases from text using simple n-gram analysis"""
    try:
        processed_text = preprocess_text(text)
        
        # Tokenize and remove stopwords
        stop_words = set(stopwords.words('english'))
        words = [word for word in word_tokenize(processed_text) if word not in stop_words and len(word) > 2]
        
        # Generate bigrams and trigrams
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        
        # Count frequency
        phrase_freq = Counter(bigrams + trigrams)
        
        # Return most common phrases
        return [phrase for phrase, count in phrase_freq.most_common(max_phrases)]
    
    except Exception as e:
        print(f"Error extracting key phrases: {str(e)}")
        return []

def generate_recommendations(missing_skills, relevance_score):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if relevance_score < 50:
        recommendations.append("Consider adding more relevant skills and experience to better match the job requirements.")
    
    if missing_skills:
        if len(missing_skills) <= 3:
            recommendations.append(f"Consider highlighting these skills if you have them: {', '.join(missing_skills[:3])}")
        else:
            recommendations.append(f"Focus on developing these key skills: {', '.join(missing_skills[:5])}")
    
    if relevance_score >= 75:
        recommendations.append("Excellent match! Your resume aligns well with the job requirements.")
    elif relevance_score >= 50:
        recommendations.append("Good match! Consider emphasizing more relevant experiences.")
    
    return recommendations


def analyze_resume_relevance_advanced(resume_data, job_description, include_explanations=True):
    """
    Advanced resume relevance analysis using multi-component scoring.
    
    Args:
        resume_data: Parsed resume data dictionary
        job_description: Job description dictionary
        include_explanations: Whether to include detailed explanations
        
    Returns:
        Dictionary with comprehensive scoring and analysis
    """
    if not ADVANCED_SCORER_AVAILABLE:
        # Fallback to legacy analysis
        return analyze_resume_relevance(
            resume_data.get('full_text', ''),
            job_description.get('description', ''),
            job_description.get('required_skills', [])
        )
    
    try:
        # Create advanced scorer
        scorer = create_advanced_scorer(
            use_semantic_similarity=True,
            semantic_weight=0.35,
            keyword_weight=0.30,
            experience_weight=0.20,
            skill_weight=0.10,
            certification_weight=0.05
        )
        
        # Calculate comprehensive score
        result = scorer.calculate_relevance_score(
            resume_data, 
            job_description, 
            include_explanations=include_explanations
        )
        
        # Convert to compatible format
        return {
            'overall_score': result.overall_score,
            'normalized_score': result.overall_score,  # Already 0-100
            'suitability_verdict': result.suitability_verdict.value,
            'confidence_level': result.confidence_level.value,
            'confidence_score': result.confidence_score,
            
            # Component scores
            'keyword_match_score': result.keyword_match_score,
            'semantic_similarity_score': result.semantic_similarity_score,
            'experience_match_score': result.experience_match_score,
            'skill_coverage_score': result.skill_coverage_score,
            'certification_match_score': result.certification_match_score,
            
            # Detailed analysis
            'strengths': result.strengths,
            'weaknesses': result.weaknesses,
            'recommendations': result.recommendations,
            'component_breakdown': [
                {
                    'name': comp.name,
                    'score': comp.score,
                    'weight': comp.weight,
                    'confidence': comp.confidence,
                    'evidence': comp.evidence,
                    'methodology': comp.methodology
                } for comp in result.components
            ],
            
            # Metadata
            'analysis_type': 'advanced_multi_component',
            'processing_time': result.processing_time,
            'methodology_version': result.methodology_version,
            'timestamp': result.timestamp,
            
            # Legacy compatibility
            'relevance_score': result.overall_score,
            'matching_skills': [],  # Would need to extract from components
            'missing_skills': [],   # Would need to extract from components
            'key_phrases': []       # Would need to extract from components
        }
        
    except Exception as e:
        print(f"Advanced analysis failed: {e}")
        # Fallback to legacy analysis
        return analyze_resume_relevance(
            resume_data.get('full_text', ''),
            job_description.get('description', ''),
            job_description.get('required_skills', [])
        )


def batch_analyze_resumes_advanced(resume_list, job_description, include_explanations=False):
    """
    Analyze multiple resumes with advanced scoring and ranking.
    
    Args:
        resume_list: List of resume data dictionaries
        job_description: Job description dictionary
        include_explanations: Whether to include detailed explanations
        
    Returns:
        List of analysis results ranked by relevance score
    """
    results = []
    
    for i, resume_data in enumerate(resume_list):
        try:
            # Add resume identifier
            resume_data['resume_index'] = i
            
            # Perform advanced analysis
            analysis = analyze_resume_relevance_advanced(
                resume_data, 
                job_description, 
                include_explanations=include_explanations
            )
            
            # Add resume identifier to results
            analysis['resume_index'] = i
            analysis['resume_id'] = resume_data.get('resume_id', f'resume_{i}')
            
            results.append(analysis)
            
        except Exception as e:
            print(f"Error analyzing resume {i}: {e}")
            # Add error result
            results.append({
                'resume_index': i,
                'resume_id': resume_data.get('resume_id', f'resume_{i}'),
                'overall_score': 0.0,
                'suitability_verdict': 'Error',
                'error': str(e)
            })
    
    # Sort by overall score (descending)
    results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
    
    return results


def get_scoring_summary(analysis_result):
    """
    Generate a concise summary of the scoring analysis.
    
    Args:
        analysis_result: Result from analyze_resume_relevance_advanced
        
    Returns:
        Dictionary with summary information
    """
    if not isinstance(analysis_result, dict):
        return {'error': 'Invalid analysis result'}
    
    # Extract key metrics
    overall_score = analysis_result.get('overall_score', 0)
    suitability = analysis_result.get('suitability_verdict', 'Unknown')
    confidence = analysis_result.get('confidence_level', 'Unknown')
    
    # Determine score category
    if overall_score >= 80:
        score_category = "Excellent"
    elif overall_score >= 65:
        score_category = "Good"
    elif overall_score >= 50:
        score_category = "Fair"
    elif overall_score >= 30:
        score_category = "Poor"
    else:
        score_category = "Very Poor"
    
    # Get top strengths and weaknesses
    strengths = analysis_result.get('strengths', [])[:3]
    weaknesses = analysis_result.get('weaknesses', [])[:3]
    
    # Get component scores
    components = analysis_result.get('component_breakdown', [])
    top_component = max(components, key=lambda x: x['score'], default={'name': 'None', 'score': 0})
    weak_component = min(components, key=lambda x: x['score'], default={'name': 'None', 'score': 0})
    
    return {
        'score_summary': {
            'overall_score': overall_score,
            'score_category': score_category,
            'suitability_verdict': suitability,
            'confidence_level': confidence
        },
        'performance_highlights': {
            'strongest_area': f"{top_component['name']}: {top_component['score']:.1f}%",
            'weakest_area': f"{weak_component['name']}: {weak_component['score']:.1f}%",
            'top_strengths': strengths,
            'main_weaknesses': weaknesses
        },
        'analysis_metadata': {
            'methodology': analysis_result.get('analysis_type', 'standard'),
            'processing_time': analysis_result.get('processing_time', 0),
            'confidence_score': analysis_result.get('confidence_score', 0)
        }
    }


# =============================================================================
# FEEDBACK GENERATION INTEGRATION
# =============================================================================

def generate_personalized_feedback(resume_data, job_description, analysis_results=None, 
                                 candidate_name=None, feedback_type="comprehensive",
                                 feedback_tone="professional", llm_provider="mock",
                                 include_resources=True):
    """
    Generate personalized feedback for a candidate based on resume analysis
    
    Args:
        resume_data: Parsed resume information
        job_description: Job requirements and description
        analysis_results: Results from advanced analysis (optional)
        candidate_name: Name of the candidate
        feedback_type: Type of feedback (comprehensive, skill_focused, etc.)
        feedback_tone: Tone of feedback (professional, encouraging, etc.)
        llm_provider: LLM provider to use (openai, anthropic, mock)
        include_resources: Whether to include learning resources
    
    Returns:
        Dictionary containing generated feedback
    """
    if not FEEDBACK_GENERATOR_AVAILABLE:
        return {
            'error': 'Feedback generation not available',
            'message': 'Please install required dependencies for LLM feedback generation'
        }
    
    try:
        # If no analysis results provided, generate them
        if analysis_results is None:
            analysis_results = analyze_resume_relevance_advanced(resume_data, job_description)
        
        # Create feedback generator
        generator = LLMFeedbackGenerator(
            provider=LLMProvider(llm_provider.lower()),
            api_key=None  # Will be read from environment
        )
        
        # Create feedback request
        request = FeedbackRequest(
            candidate_name=candidate_name,
            resume_data=resume_data,
            job_description=job_description,
            analysis_results=analysis_results,
            feedback_type=FeedbackType(feedback_type.lower()),
            tone=FeedbackTone(feedback_tone.lower()),
            company_name=job_description.get('company_name'),
            position_title=job_description.get('position_title', job_description.get('title')),
            include_resources=include_resources
        )
        
        # Generate feedback
        feedback = generator.generate_feedback(request)
        
        # Convert to dictionary for JSON serialization
        from dataclasses import asdict
        feedback_dict = asdict(feedback)
        
        # Add integration metadata
        feedback_dict['integration_info'] = {
            'source': 'automated_resume_relevance_system',
            'analysis_integrated': True,
            'scoring_system_version': analysis_results.get('methodology_version', '2.0.0'),
            'feedback_system_version': '1.0.0'
        }
        
        return feedback_dict
        
    except Exception as e:
        return {
            'error': f'Feedback generation failed: {str(e)}',
            'fallback_recommendations': _generate_basic_feedback_fallback(analysis_results)
        }


def generate_skill_focused_feedback(resume_data, job_description, analysis_results=None,
                                  candidate_name=None, llm_provider="mock"):
    """Generate skill-focused feedback for a candidate"""
    return generate_personalized_feedback(
        resume_data=resume_data,
        job_description=job_description,
        analysis_results=analysis_results,
        candidate_name=candidate_name,
        feedback_type="skill_focused",
        feedback_tone="practical",
        llm_provider=llm_provider
    )


def generate_experience_focused_feedback(resume_data, job_description, analysis_results=None,
                                       candidate_name=None, llm_provider="mock"):
    """Generate experience-focused feedback for a candidate"""
    return generate_personalized_feedback(
        resume_data=resume_data,
        job_description=job_description,
        analysis_results=analysis_results,
        candidate_name=candidate_name,
        feedback_type="experience_focused",
        feedback_tone="strategic",
        llm_provider=llm_provider
    )


def generate_certification_focused_feedback(resume_data, job_description, analysis_results=None,
                                          candidate_name=None, llm_provider="mock"):
    """Generate certification and training focused feedback for a candidate"""
    return generate_personalized_feedback(
        resume_data=resume_data,
        job_description=job_description,
        analysis_results=analysis_results,
        candidate_name=candidate_name,
        feedback_type="certification_focused",
        feedback_tone="analytical",
        llm_provider=llm_provider
    )


def batch_generate_candidate_feedback(candidates_data, job_description, 
                                     feedback_type="comprehensive",
                                     llm_provider="mock"):
    """
    Generate feedback for multiple candidates in batch
    
    Args:
        candidates_data: List of candidate data dictionaries with 'resume_data' and 'candidate_name'
        job_description: Job requirements and description
        feedback_type: Type of feedback to generate
        llm_provider: LLM provider to use
    
    Returns:
        List of feedback results for each candidate
    """
    feedback_results = []
    
    for candidate in candidates_data:
        try:
            # Extract candidate information
            resume_data = candidate.get('resume_data')
            candidate_name = candidate.get('candidate_name', 'Candidate')
            candidate_id = candidate.get('candidate_id')
            
            # Generate analysis if not provided
            analysis_results = candidate.get('analysis_results')
            if not analysis_results:
                analysis_results = analyze_resume_relevance_advanced(resume_data, job_description)
            
            # Generate feedback
            feedback = generate_personalized_feedback(
                resume_data=resume_data,
                job_description=job_description,
                analysis_results=analysis_results,
                candidate_name=candidate_name,
                feedback_type=feedback_type,
                llm_provider=llm_provider
            )
            
            feedback_results.append({
                'candidate_id': candidate_id,
                'candidate_name': candidate_name,
                'feedback': feedback,
                'status': 'success'
            })
            
        except Exception as e:
            feedback_results.append({
                'candidate_id': candidate.get('candidate_id'),
                'candidate_name': candidate.get('candidate_name', 'Unknown'),
                'error': str(e),
                'status': 'failed'
            })
    
    return feedback_results


def compare_candidate_feedback(candidates_data, job_description, llm_provider="mock"):
    """
    Generate comparative feedback for multiple candidates
    
    Args:
        candidates_data: List of candidate data
        job_description: Job requirements
        llm_provider: LLM provider to use
    
    Returns:
        Comparative analysis with individual feedback and ranking insights
    """
    try:
        # Generate individual feedback for each candidate
        individual_feedback = batch_generate_candidate_feedback(
            candidates_data, job_description, "comprehensive", llm_provider
        )
        
        # Extract scores and rankings
        candidate_scores = []
        for feedback_result in individual_feedback:
            if feedback_result['status'] == 'success':
                feedback = feedback_result['feedback']
                candidate_scores.append({
                    'candidate_id': feedback_result['candidate_id'],
                    'candidate_name': feedback_result['candidate_name'],
                    'overall_score': feedback.get('overall_score', 0),
                    'suitability_verdict': feedback.get('suitability_verdict', 'Unknown'),
                    'confidence_level': feedback.get('confidence_level', 'Unknown'),
                    'strengths': feedback.get('strengths', [])[:3],
                    'key_recommendations': feedback.get('areas_for_improvement', [])[:3]
                })
        
        # Sort by overall score
        candidate_scores.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Generate comparative insights
        if candidate_scores:
            top_candidate = candidate_scores[0]
            score_range = candidate_scores[0]['overall_score'] - candidate_scores[-1]['overall_score']
            avg_score = sum(c['overall_score'] for c in candidate_scores) / len(candidate_scores)
            
            comparative_insights = {
                'ranking_summary': {
                    'total_candidates': len(candidate_scores),
                    'top_candidate': top_candidate['candidate_name'],
                    'top_score': top_candidate['overall_score'],
                    'score_range': score_range,
                    'average_score': avg_score
                },
                'ranking_insights': _generate_ranking_insights(candidate_scores, score_range),
                'hiring_recommendations': _generate_hiring_recommendations(candidate_scores)
            }
        else:
            comparative_insights = {
                'error': 'No valid candidate analyses available for comparison'
            }
        
        return {
            'individual_feedback': individual_feedback,
            'ranked_candidates': candidate_scores,
            'comparative_analysis': comparative_insights,
            'job_description': job_description
        }
        
    except Exception as e:
        return {
            'error': f'Comparative feedback generation failed: {str(e)}',
            'individual_feedback': individual_feedback if 'individual_feedback' in locals() else []
        }


def _generate_basic_feedback_fallback(analysis_results):
    """Generate basic feedback when LLM is not available"""
    if not analysis_results:
        return ["Please review your qualifications against the job requirements"]
    
    fallback_recommendations = []
    
    # Based on overall score
    score = analysis_results.get('overall_score', 0)
    if score < 50:
        fallback_recommendations.append("Consider gaining more relevant skills and experience before applying")
    elif score < 70:
        fallback_recommendations.append("Address key skill gaps to improve your candidacy")
    else:
        fallback_recommendations.append("You have strong qualifications - consider highlighting them better")
    
    # Based on weaknesses
    weaknesses = analysis_results.get('weaknesses', [])
    for weakness in weaknesses[:2]:
        fallback_recommendations.append(f"Focus on improving: {weakness}")
    
    # Based on component scores
    components = analysis_results.get('component_breakdown', [])
    weak_components = [c for c in components if c.get('score', 0) < 50]
    for component in weak_components[:2]:
        fallback_recommendations.append(f"Strengthen your {component.get('name', 'profile')} section")
    
    return fallback_recommendations


def _generate_ranking_insights(candidate_scores, score_range):
    """Generate insights about candidate rankings"""
    insights = []
    
    if score_range > 30:
        insights.append("Significant variation in candidate quality - clear differentiation possible")
    elif score_range > 15:
        insights.append("Moderate variation in candidate quality - additional criteria may help selection")
    else:
        insights.append("Similar candidate quality levels - consider cultural fit and soft skills")
    
    high_performers = [c for c in candidate_scores if c['overall_score'] >= 70]
    if len(high_performers) > 1:
        insights.append(f"{len(high_performers)} candidates show strong qualifications")
    elif len(high_performers) == 1:
        insights.append("One standout candidate identified")
    else:
        insights.append("No candidates meet high qualification threshold - consider expanding search")
    
    return insights


def _generate_hiring_recommendations(candidate_scores):
    """Generate hiring recommendations based on candidate analysis"""
    recommendations = []
    
    if not candidate_scores:
        return ["No candidates available for recommendation"]
    
    top_candidate = candidate_scores[0]
    
    if top_candidate['overall_score'] >= 80:
        recommendations.append(f"Strong recommendation to proceed with {top_candidate['candidate_name']}")
    elif top_candidate['overall_score'] >= 60:
        recommendations.append(f"Consider {top_candidate['candidate_name']} with additional skill development")
    else:
        recommendations.append("Consider expanding candidate pool - current options may need significant development")
    
    # Check for multiple strong candidates
    strong_candidates = [c for c in candidate_scores if c['overall_score'] >= 70]
    if len(strong_candidates) > 1:
        names = [c['candidate_name'] for c in strong_candidates[:3]]
        recommendations.append(f"Multiple strong candidates available: {', '.join(names)}")
    
    return recommendations


def analyze_relevance(resume_text, job_text, use_advanced=True):
    """
    Analyze relevance between resume and job description
    
    Args:
        resume_text (str): Resume content
        job_text (str): Job description content
        use_advanced (bool): Whether to use advanced scoring
        
    Returns:
        dict: Analysis results including relevance score and details
    """
    try:
        if use_advanced and ADVANCED_SCORER_AVAILABLE:
            scorer = create_advanced_scorer()
            return scorer.calculate_relevance_score(resume_text, job_text)
        else:
            # Use basic analysis
            return calculate_similarity_score(resume_text, job_text)
            
    except Exception as e:
        # Fallback basic analysis
        return {
            'success': False,
            'relevance_score': 0.0,
            'error': str(e),
            'matched_skills': [],
            'missing_skills': [],
            'recommendations': ['Unable to perform detailed analysis']
        }
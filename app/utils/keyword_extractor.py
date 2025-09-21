import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def extract_keywords_and_requirements(text):
    """Extract keywords, skills, and requirements from job description text"""
    
    # Technical skills patterns
    technical_skills = [
        # Programming languages
        r'\b(?:python|java|javascript|js|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala|r|matlab)\b',
        
        # Web technologies
        r'\b(?:html|css|react|angular|vue|node\.?js|express|django|flask|spring|laravel|rails|asp\.net|bootstrap|jquery|typescript)\b',
        
        # Databases
        r'\b(?:sql|mysql|postgresql|postgres|mongodb|oracle|sqlite|redis|elasticsearch|nosql)\b',
        
        # Cloud and DevOps
        r'\b(?:aws|azure|gcp|google cloud|docker|kubernetes|jenkins|git|github|gitlab|ci/cd|devops|terraform|ansible)\b',
        
        # Data Science
        r'\b(?:machine learning|deep learning|neural networks|tensorflow|pytorch|scikit-learn|pandas|numpy|matplotlib|seaborn|jupyter|spark|hadoop|tableau|power\s?bi)\b'
    ]
    
    # Soft skills patterns
    soft_skills_patterns = [
        r'\b(?:leadership|communication|teamwork|problem[\s-]solving|analytical|creative|organized|detail[\s-]oriented|time management|project management)\b',
        r'\b(?:collaboration|adaptability|critical thinking|decision making|mentoring|training|presentation|negotiation)\b'
    ]
    
    # Education patterns
    education_patterns = [
        r'\b(?:bachelor|master|phd|degree|diploma|certification|certificate)\b',
        r'\b(?:computer science|engineering|mathematics|statistics|business|mba)\b'
    ]
    
    # Experience patterns
    experience_patterns = [
        r'\b(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)\b',
        r'\b(?:senior|junior|lead|principal|architect|manager|director|intern)\b'
    ]
    
    processed_text = text.lower()
    
    # Extract different types of keywords
    results = {
        'technical_skills': [],
        'soft_skills': [],
        'education_requirements': [],
        'experience_requirements': [],
        'key_responsibilities': [],
        'required_skills': [],
        'preferred_skills': [],
        'all_keywords': []
    }
    
    # Extract technical skills
    for pattern in technical_skills:
        matches = re.findall(pattern, processed_text, re.IGNORECASE)
        results['technical_skills'].extend(matches)
    
    # Extract soft skills
    for pattern in soft_skills_patterns:
        matches = re.findall(pattern, processed_text, re.IGNORECASE)
        results['soft_skills'].extend(matches)
    
    # Extract education requirements
    for pattern in education_patterns:
        matches = re.findall(pattern, processed_text, re.IGNORECASE)
        results['education_requirements'].extend(matches)
    
    # Extract experience requirements
    for pattern in experience_patterns:
        matches = re.findall(pattern, processed_text, re.IGNORECASE)
        results['experience_requirements'].extend(matches)
    
    # Extract required vs preferred skills
    results['required_skills'] = extract_required_skills(text)
    results['preferred_skills'] = extract_preferred_skills(text)
    
    # Extract key responsibilities
    results['key_responsibilities'] = extract_responsibilities(text)
    
    # Remove duplicates and clean up
    for key in results:
        if isinstance(results[key], list):
            results[key] = list(set([item.strip() for item in results[key] if item.strip()]))
    
    # Generate comprehensive keyword list
    all_keywords = []
    all_keywords.extend(results['technical_skills'])
    all_keywords.extend(results['soft_skills'])
    all_keywords.extend(results['required_skills'])
    all_keywords.extend(results['preferred_skills'])
    
    results['all_keywords'] = list(set(all_keywords))
    
    # Add keyword frequency analysis
    results['keyword_frequency'] = analyze_keyword_frequency(processed_text, results['all_keywords'])
    
    # Add importance scoring
    results['skill_importance'] = score_skill_importance(text, results['all_keywords'])
    
    return results

def extract_required_skills(text):
    """Extract skills marked as required"""
    required_patterns = [
        r'required[:\s]*([^.]*?)(?:\.|required|preferred|$)',
        r'must have[:\s]*([^.]*?)(?:\.|must|should|$)',
        r'essential[:\s]*([^.]*?)(?:\.|essential|desired|$)'
    ]
    
    required_skills = []
    text_lower = text.lower()
    
    for pattern in required_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # Extract individual skills from the matched text
            skills = extract_skills_from_text(match)
            required_skills.extend(skills)
    
    return required_skills

def extract_preferred_skills(text):
    """Extract skills marked as preferred or nice to have"""
    preferred_patterns = [
        r'preferred[:\s]*([^.]*?)(?:\.|required|preferred|$)',
        r'nice to have[:\s]*([^.]*?)(?:\.|nice|must|$)',
        r'desired[:\s]*([^.]*?)(?:\.|desired|required|$)',
        r'plus[:\s]*([^.]*?)(?:\.|plus|required|$)'
    ]
    
    preferred_skills = []
    text_lower = text.lower()
    
    for pattern in preferred_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            skills = extract_skills_from_text(match)
            preferred_skills.extend(skills)
    
    return preferred_skills

def extract_responsibilities(text):
    """Extract key responsibilities from job description"""
    responsibility_patterns = [
        r'responsibilities[:\s]*([^.]*?)(?:\.|responsibilities|requirements|$)',
        r'duties[:\s]*([^.]*?)(?:\.|duties|requirements|$)',
        r'you will[:\s]*([^.]*?)(?:\.|you|requirements|$)',
        r'role involves[:\s]*([^.]*?)(?:\.|role|requirements|$)'
    ]
    
    responsibilities = []
    text_lower = text.lower()
    
    for pattern in responsibility_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # Split by common delimiters and clean up
            items = re.split(r'[,;•\-\n]', match)
            for item in items:
                item = item.strip()
                if len(item) > 10:  # Filter out very short items
                    responsibilities.append(item)
    
    return responsibilities[:10]  # Return top 10 responsibilities

def extract_skills_from_text(text):
    """Extract individual skills from a text block"""
    # Common delimiters for skills
    skills = re.split(r'[,;•\-\n]', text)
    
    cleaned_skills = []
    for skill in skills:
        skill = skill.strip()
        # Remove common prefixes
        skill = re.sub(r'^(and|or|with|in|of|the|a|an)\s+', '', skill, flags=re.IGNORECASE)
        if len(skill) > 2 and len(skill) < 50:  # Reasonable skill length
            cleaned_skills.append(skill)
    
    return cleaned_skills

def analyze_keyword_frequency(text, keywords):
    """Analyze frequency of keywords in text"""
    frequency = {}
    text_lower = text.lower()
    
    for keyword in keywords:
        count = text_lower.count(keyword.lower())
        if count > 0:
            frequency[keyword] = count
    
    # Sort by frequency
    return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))

def score_skill_importance(text, skills):
    """Score the importance of skills based on context"""
    text_lower = text.lower()
    importance_scores = {}
    
    # Keywords that indicate high importance
    high_importance_indicators = ['required', 'must', 'essential', 'critical', 'key', 'strong']
    medium_importance_indicators = ['preferred', 'desired', 'experience with', 'knowledge of']
    
    for skill in skills:
        score = 0
        skill_lower = skill.lower()
        
        # Base score for appearance
        appearances = text_lower.count(skill_lower)
        score += appearances
        
        # Check context around the skill
        skill_positions = []
        start = 0
        while True:
            pos = text_lower.find(skill_lower, start)
            if pos == -1:
                break
            skill_positions.append(pos)
            start = pos + 1
        
        # Analyze context around each appearance
        for pos in skill_positions:
            context_start = max(0, pos - 50)
            context_end = min(len(text_lower), pos + len(skill_lower) + 50)
            context = text_lower[context_start:context_end]
            
            # Check for importance indicators
            for indicator in high_importance_indicators:
                if indicator in context:
                    score += 3
            
            for indicator in medium_importance_indicators:
                if indicator in context:
                    score += 1
        
        importance_scores[skill] = score
    
    # Normalize scores
    if importance_scores:
        max_score = max(importance_scores.values())
        if max_score > 0:
            for skill in importance_scores:
                importance_scores[skill] = round(importance_scores[skill] / max_score * 100, 2)
    
    return dict(sorted(importance_scores.items(), key=lambda x: x[1], reverse=True))

def extract_company_info(text):
    """Extract basic company information from job description"""
    company_patterns = [
        r'(?:at|join|for)\s+([A-Z][A-Za-z\s&]+?)(?:\s+(?:is|are|we|our|the))',
        r'company[:\s]*([^.]*?)(?:\.|company|$)'
    ]
    
    company_info = []
    
    for pattern in company_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        company_info.extend([match.strip() for match in matches if len(match.strip()) > 2])
    
    return company_info[:3]  # Return top 3 potential company mentions


def extract_keywords(text, num_keywords=20):
    """
    Simple keyword extraction function for tests and basic functionality
    
    Args:
        text (str): Text to extract keywords from
        num_keywords (int): Number of keywords to return
        
    Returns:
        list: List of extracted keywords
    """
    try:
        # Use the more comprehensive function and extract just keywords
        results = extract_keywords_and_requirements(text)
        
        # Combine all skills and keywords
        all_keywords = []
        all_keywords.extend(results.get('technical_skills', []))
        all_keywords.extend(results.get('soft_skills', []))
        all_keywords.extend(results.get('domain_expertise', []))
        
        # Remove duplicates and return top keywords
        unique_keywords = list(set(all_keywords))
        return unique_keywords[:num_keywords]
        
    except Exception as e:
        # Fallback simple keyword extraction
        words = re.findall(r'\b[A-Za-z]+\b', text.lower())
        return list(set(words))[:num_keywords]
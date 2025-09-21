"""
Advanced Feedback Generation Module using Large Language Models

This module provides comprehensive, personalized feedback for candidates based on
resume analysis and job requirements. It uses LLM APIs to generate actionable
insights, skill improvement suggestions, and career guidance.

Features:
- Multi-provider LLM support (OpenAI, Anthropic, local models)
- Personalized feedback generation
- Skill gap analysis with improvement suggestions
- Career progression recommendations
- Resume enhancement advice
- Certification and training recommendations

Author: Automated Resume Relevance System
Version: 1.0.0
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback that can be generated"""
    COMPREHENSIVE = "comprehensive"
    SKILL_FOCUSED = "skill_focused"
    EXPERIENCE_FOCUSED = "experience_focused"
    CERTIFICATION_FOCUSED = "certification_focused"
    RESUME_FORMAT = "resume_format"
    CAREER_PROGRESSION = "career_progression"


class FeedbackTone(Enum):
    """Tone of feedback delivery"""
    PROFESSIONAL = "professional"
    ENCOURAGING = "encouraging"
    CONSTRUCTIVE = "constructive"
    DETAILED = "detailed"
    CONCISE = "concise"


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"  # For testing without API costs


@dataclass
class FeedbackRequest:
    """Request structure for feedback generation"""
    candidate_name: Optional[str] = None
    resume_data: Dict[str, Any] = None
    job_description: Dict[str, Any] = None
    analysis_results: Dict[str, Any] = None
    feedback_type: FeedbackType = FeedbackType.COMPREHENSIVE
    tone: FeedbackTone = FeedbackTone.PROFESSIONAL
    focus_areas: List[str] = None
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    include_resources: bool = True
    max_length: int = 800  # Reduced from 1000 to limit verbosity
    max_skills_per_section: int = 10  # Limit skills per section
    max_recommendations: int = 5  # Limit recommendations
    max_tips: int = 5  # Limit tips and advice


@dataclass
class FeedbackSection:
    """Individual feedback section"""
    title: str
    content: str
    priority: int  # 1-5, 1 being highest priority
    category: str
    actionable_items: List[str]
    resources: List[Dict[str, str]] = None


@dataclass
class GeneratedFeedback:
    """Complete feedback response structure"""
    candidate_name: str
    position_title: str
    overall_score: float
    suitability_verdict: str
    confidence_level: str
    
    # Main feedback sections
    executive_summary: str
    strengths: List[str]
    areas_for_improvement: List[FeedbackSection]
    skill_recommendations: List[FeedbackSection]
    experience_suggestions: List[FeedbackSection]
    certification_recommendations: List[FeedbackSection]
    resume_enhancement_tips: List[str]
    career_progression_advice: List[str]
    
    # Metadata
    generation_timestamp: str
    feedback_type: str
    tone: str
    llm_provider: str
    processing_time: float
    
    # Additional resources
    learning_resources: List[Dict[str, str]] = None
    industry_insights: List[str] = None
    next_steps: List[str] = None


class LLMFeedbackGenerator:
    """Main class for generating personalized feedback using LLMs"""
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.OPENAI,
                 api_key: Optional[str] = None,
                 model_name: Optional[str] = None,
                 base_url: Optional[str] = None):
        """
        Initialize the feedback generator
        
        Args:
            provider: LLM provider to use
            api_key: API key for the provider
            model_name: Specific model to use
            base_url: Base URL for API calls (for local models)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.model_name = model_name or self._get_default_model()
        self.base_url = base_url
        
        # Import template manager and config manager
        from .feedback_templates import template_manager
        from .feedback_config import config_manager
        self.template_manager = template_manager
        self.config_manager = config_manager
        
        # Feedback templates and prompts (legacy support)
        self.prompt_templates = self._load_prompt_templates()
    
    def _truncate_text(self, text: str, max_length: int = 300) -> str:
        """Truncate text to reasonable length"""
        if not text or len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        # Try to truncate at sentence boundary
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.7:
            truncated = truncated[:last_period + 1]
        else:
            # Truncate at word boundary
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:
                truncated = truncated[:last_space]
            truncated += "..."
        
        return truncated
    
    def _limit_list_items(self, items: List[str], max_items: int = 5) -> List[str]:
        """Limit list items to reasonable number"""
        if not items:
            return []
        return items[:max_items]
    
    def _create_summary_text(self, items: List[str], max_display: int, item_type: str) -> str:
        """Create summary text for truncated lists"""
        if not items:
            return f"No {item_type} identified"
        
        if len(items) <= max_display:
            return f"{len(items)} {item_type} identified"
        else:
            return f"Top {max_display} of {len(items)} {item_type} (view details for complete list)"
        self.resource_database = self._load_resource_database()
        
        # Configuration
        self.max_retries = 3
        self.retry_delay = 2
        self.timeout = 30
        
        logger.info(f"Initialized LLM Feedback Generator with provider: {provider.value}")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables"""
        if self.provider == LLMProvider.OPENAI:
            return os.getenv('OPENAI_API_KEY')
        elif self.provider == LLMProvider.ANTHROPIC:
            return os.getenv('ANTHROPIC_API_KEY')
        return None
    
    def _get_default_model(self) -> str:
        """Get default model for the provider"""
        model_defaults = {
            LLMProvider.OPENAI: "gpt-4",
            LLMProvider.ANTHROPIC: "claude-3-sonnet-20240229",
            LLMProvider.LOCAL: "llama-2-70b-chat",
            LLMProvider.MOCK: "mock-model"
        }
        return model_defaults.get(self.provider, "gpt-3.5-turbo")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different feedback types"""
        return {
            "comprehensive": """
You are an expert HR consultant and career advisor. Analyze the following candidate's resume against the job requirements and provide comprehensive, actionable feedback.

CANDIDATE INFORMATION:
Name: {candidate_name}
Position Applied: {position_title}
Company: {company_name}

RESUME DATA:
{resume_summary}

JOB REQUIREMENTS:
{job_requirements}

ANALYSIS RESULTS:
Overall Score: {overall_score}/100
Suitability: {suitability_verdict}
Component Breakdown: {component_analysis}

INSTRUCTIONS:
1. Provide personalized, constructive feedback in a {tone} tone
2. Focus on specific, actionable improvements
3. Include skill gaps and how to bridge them
4. Suggest relevant certifications and training
5. Provide resume enhancement recommendations
6. Include career progression advice
7. Be specific about missing requirements
8. Suggest timeline for improvements

Format your response as structured feedback with clear sections.
""",
            
            "skill_focused": """
You are a technical skills assessor. Analyze the candidate's skills against job requirements and provide detailed skill-focused feedback.

CANDIDATE SKILLS: {candidate_skills}
REQUIRED SKILLS: {required_skills}
SKILL GAPS: {skill_gaps}
SKILL MATCHES: {skill_matches}

Provide specific recommendations for:
1. Priority skills to develop
2. Learning resources and courses
3. Hands-on project suggestions
4. Certification paths
5. Timeline for skill development
""",
            
            "experience_focused": """
You are an experience evaluator. Analyze the candidate's work experience against job requirements.

CANDIDATE EXPERIENCE: {candidate_experience}
REQUIRED EXPERIENCE: {required_experience}
EXPERIENCE GAPS: {experience_gaps}

Provide recommendations for:
1. How to gain relevant experience
2. Transferable skills from current experience
3. Project opportunities to build experience
4. Networking and mentorship suggestions
""",
            
            "certification_focused": """
You are a certification advisor. Recommend relevant certifications and training.

CURRENT CERTIFICATIONS: {current_certifications}
INDUSTRY REQUIREMENTS: {industry_requirements}
MISSING CERTIFICATIONS: {missing_certifications}

Provide:
1. Priority certification recommendations
2. Training pathways and timelines
3. Cost-benefit analysis of certifications
4. Alternative credentials and micro-learning options
"""
        }
    
    def _load_resource_database(self) -> Dict[str, List[Dict[str, str]]]:
        """Load database of learning resources and recommendations"""
        return {
            "programming_languages": [
                {"name": "Python Fundamentals", "url": "https://www.coursera.org/learn/python", "provider": "Coursera", "type": "course"},
                {"name": "JavaScript Complete Guide", "url": "https://www.udemy.com/course/javascript-the-complete-guide", "provider": "Udemy", "type": "course"},
                {"name": "Java Programming", "url": "https://www.oracle.com/java/technologies/javase-training", "provider": "Oracle", "type": "certification"}
            ],
            "web_development": [
                {"name": "Full Stack Web Development", "url": "https://www.freecodecamp.org/learn/", "provider": "FreeCodeCamp", "type": "free_course"},
                {"name": "React Developer Certification", "url": "https://reactjs.org/community/courses.html", "provider": "React Community", "type": "certification"}
            ],
            "data_science": [
                {"name": "Data Science Specialization", "url": "https://www.coursera.org/specializations/jhu-data-science", "provider": "Johns Hopkins - Coursera", "type": "specialization"},
                {"name": "Kaggle Learn", "url": "https://www.kaggle.com/learn", "provider": "Kaggle", "type": "free_course"}
            ],
            "cloud_computing": [
                {"name": "AWS Certified Solutions Architect", "url": "https://aws.amazon.com/certification/", "provider": "Amazon", "type": "certification"},
                {"name": "Google Cloud Professional", "url": "https://cloud.google.com/certification", "provider": "Google", "type": "certification"}
            ],
            "project_management": [
                {"name": "PMP Certification", "url": "https://www.pmi.org/certifications/project-management-pmp", "provider": "PMI", "type": "certification"},
                {"name": "Agile and Scrum", "url": "https://www.scrumalliance.org/get-certified", "provider": "Scrum Alliance", "type": "certification"}
            ]
        }
    
    def generate_feedback(self, request: FeedbackRequest) -> GeneratedFeedback:
        """
        Generate comprehensive feedback for a candidate
        
        Args:
            request: FeedbackRequest containing all necessary information
            
        Returns:
            GeneratedFeedback: Complete feedback response
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generating {request.feedback_type.value} feedback for candidate")
            
            # Prepare context for LLM
            context = self._prepare_context(request)
            
            # Generate different sections of feedback
            if request.feedback_type == FeedbackType.COMPREHENSIVE:
                feedback = self._generate_comprehensive_feedback(context, request)
            elif request.feedback_type == FeedbackType.SKILL_FOCUSED:
                feedback = self._generate_skill_focused_feedback(context, request)
            elif request.feedback_type == FeedbackType.EXPERIENCE_FOCUSED:
                feedback = self._generate_experience_focused_feedback(context, request)
            elif request.feedback_type == FeedbackType.CERTIFICATION_FOCUSED:
                feedback = self._generate_certification_focused_feedback(context, request)
            else:
                feedback = self._generate_comprehensive_feedback(context, request)
            
            # Add metadata
            feedback.generation_timestamp = datetime.now().isoformat()
            feedback.feedback_type = request.feedback_type.value
            feedback.tone = request.tone.value
            feedback.llm_provider = self.provider.value
            feedback.processing_time = time.time() - start_time
            
            # Add resources and next steps
            feedback.learning_resources = self._get_relevant_resources(context)
            feedback.next_steps = self._generate_next_steps(context)
            
            logger.info(f"Feedback generated successfully in {feedback.processing_time:.2f} seconds")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return self._generate_fallback_feedback(request, str(e))
    
    def _prepare_context(self, request: FeedbackRequest) -> Dict[str, Any]:
        """Prepare context information for LLM prompts"""
        context = {
            "candidate_name": request.candidate_name or "Candidate",
            "position_title": request.position_title or "Position",
            "company_name": request.company_name or "Company",
            "resume_data": request.resume_data or {},
            "job_description": request.job_description or {},
            "analysis_results": request.analysis_results or {},
            "tone": request.tone.value,
            "include_resources": request.include_resources
        }
        
        # Extract key information
        if request.resume_data:
            context["candidate_skills"] = request.resume_data.get("skills", [])
            context["candidate_experience"] = request.resume_data.get("work_experience", [])
            context["candidate_certifications"] = request.resume_data.get("certifications", [])
            context["candidate_education"] = request.resume_data.get("education", [])
        
        if request.job_description:
            context["required_skills"] = request.job_description.get("required_skills", [])
            context["preferred_skills"] = request.job_description.get("preferred_skills", [])
            context["required_experience"] = request.job_description.get("experience_requirements", "")
            context["required_certifications"] = request.job_description.get("certifications", [])
        
        if request.analysis_results:
            context["overall_score"] = request.analysis_results.get("overall_score", 0)
            context["suitability_verdict"] = request.analysis_results.get("suitability_verdict", "Unknown")
            context["confidence_level"] = request.analysis_results.get("confidence_level", "Unknown")
            context["component_breakdown"] = request.analysis_results.get("component_breakdown", [])
            context["strengths"] = request.analysis_results.get("strengths", [])
            context["weaknesses"] = request.analysis_results.get("weaknesses", [])
        
        return context
    
    def _generate_comprehensive_feedback(self, context: Dict[str, Any], request: FeedbackRequest) -> GeneratedFeedback:
        """Generate comprehensive feedback covering all aspects"""
        
        # Use LLM to generate main feedback content
        llm_response = self._call_llm(
            self.prompt_templates["comprehensive"].format(**context),
            max_tokens=request.max_length
        )
        
        # Parse LLM response and structure it
        feedback_sections = self._parse_llm_response(llm_response)
        
        # Create comprehensive feedback object
        feedback = GeneratedFeedback(
            candidate_name=context["candidate_name"],
            position_title=context["position_title"],
            overall_score=context.get("overall_score", 0),
            suitability_verdict=context.get("suitability_verdict", "Unknown"),
            confidence_level=context.get("confidence_level", "Unknown"),
            
            executive_summary=feedback_sections.get("executive_summary", ""),
            strengths=feedback_sections.get("strengths", []),
            areas_for_improvement=self._create_feedback_sections(feedback_sections.get("improvements", [])),
            skill_recommendations=self._create_feedback_sections(feedback_sections.get("skill_recommendations", [])),
            experience_suggestions=self._create_feedback_sections(feedback_sections.get("experience_suggestions", [])),
            certification_recommendations=self._create_feedback_sections(feedback_sections.get("certification_recommendations", [])),
            resume_enhancement_tips=feedback_sections.get("resume_tips", []),
            career_progression_advice=feedback_sections.get("career_advice", []),
            
            generation_timestamp="",
            feedback_type="",
            tone="",
            llm_provider="",
            processing_time=0.0
        )
        
        return feedback
    
    def _generate_skill_focused_feedback(self, context: Dict[str, Any], request: FeedbackRequest) -> GeneratedFeedback:
        """Generate skill-focused feedback"""
        # Analyze skill gaps
        skill_gaps = self._analyze_skill_gaps(context)
        context["skill_gaps"] = skill_gaps
        
        llm_response = self._call_llm(
            self.prompt_templates["skill_focused"].format(**context),
            max_tokens=request.max_length
        )
        
        feedback_sections = self._parse_llm_response(llm_response)
        
        return GeneratedFeedback(
            candidate_name=context["candidate_name"],
            position_title=context["position_title"],
            overall_score=context.get("overall_score", 0),
            suitability_verdict=context.get("suitability_verdict", "Unknown"),
            confidence_level=context.get("confidence_level", "Unknown"),
            
            executive_summary=f"Skill-focused feedback for {context['position_title']} position",
            strengths=context.get("strengths", []),
            areas_for_improvement=self._create_feedback_sections([]),
            skill_recommendations=self._create_feedback_sections(feedback_sections.get("skill_recommendations", [])),
            experience_suggestions=self._create_feedback_sections([]),
            certification_recommendations=self._create_feedback_sections([]),
            resume_enhancement_tips=[],
            career_progression_advice=[],
            
            generation_timestamp="",
            feedback_type="",
            tone="",
            llm_provider="",
            processing_time=0.0
        )
    
    def _generate_experience_focused_feedback(self, context: Dict[str, Any], request: FeedbackRequest) -> GeneratedFeedback:
        """Generate experience-focused feedback"""
        experience_gaps = self._analyze_experience_gaps(context)
        context["experience_gaps"] = experience_gaps
        
        llm_response = self._call_llm(
            self.prompt_templates["experience_focused"].format(**context),
            max_tokens=request.max_length
        )
        
        feedback_sections = self._parse_llm_response(llm_response)
        
        return GeneratedFeedback(
            candidate_name=context["candidate_name"],
            position_title=context["position_title"],
            overall_score=context.get("overall_score", 0),
            suitability_verdict=context.get("suitability_verdict", "Unknown"),
            confidence_level=context.get("confidence_level", "Unknown"),
            
            executive_summary=f"Experience-focused feedback for {context['position_title']} position",
            strengths=context.get("strengths", []),
            areas_for_improvement=self._create_feedback_sections([]),
            skill_recommendations=self._create_feedback_sections([]),
            experience_suggestions=self._create_feedback_sections(feedback_sections.get("experience_suggestions", [])),
            certification_recommendations=self._create_feedback_sections([]),
            resume_enhancement_tips=[],
            career_progression_advice=feedback_sections.get("career_advice", []),
            
            generation_timestamp="",
            feedback_type="",
            tone="",
            llm_provider="",
            processing_time=0.0
        )
    
    def _generate_certification_focused_feedback(self, context: Dict[str, Any], request: FeedbackRequest) -> GeneratedFeedback:
        """Generate certification-focused feedback"""
        cert_gaps = self._analyze_certification_gaps(context)
        context.update(cert_gaps)
        
        llm_response = self._call_llm(
            self.prompt_templates["certification_focused"].format(**context),
            max_tokens=request.max_length
        )
        
        feedback_sections = self._parse_llm_response(llm_response)
        
        return GeneratedFeedback(
            candidate_name=context["candidate_name"],
            position_title=context["position_title"],
            overall_score=context.get("overall_score", 0),
            suitability_verdict=context.get("suitability_verdict", "Unknown"),
            confidence_level=context.get("confidence_level", "Unknown"),
            
            executive_summary=f"Certification-focused feedback for {context['position_title']} position",
            strengths=context.get("strengths", []),
            areas_for_improvement=self._create_feedback_sections([]),
            skill_recommendations=self._create_feedback_sections([]),
            experience_suggestions=self._create_feedback_sections([]),
            certification_recommendations=self._create_feedback_sections(feedback_sections.get("certification_recommendations", [])),
            resume_enhancement_tips=[],
            career_progression_advice=[],
            
            generation_timestamp="",
            feedback_type="",
            tone="",
            llm_provider="",
            processing_time=0.0
        )
    
    def _call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make API call to LLM provider"""
        if self.provider == LLMProvider.MOCK:
            return self._mock_llm_response(prompt)
        
        for attempt in range(self.max_retries):
            try:
                if self.provider == LLMProvider.OPENAI:
                    return self._call_openai(prompt, max_tokens)
                elif self.provider == LLMProvider.ANTHROPIC:
                    return self._call_anthropic(prompt, max_tokens)
                elif self.provider == LLMProvider.LOCAL:
                    return self._call_local_model(prompt, max_tokens)
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")
                    
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise e
    
    def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are an expert HR consultant and career advisor."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Call Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    
    def _call_local_model(self, prompt: str, max_tokens: int) -> str:
        """Call local model API"""
        if not self.base_url:
            raise ValueError("Base URL required for local model")
        
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()["text"]
    
    def _mock_llm_response(self, prompt: str) -> str:
        """Generate mock response for testing"""
        return f"""
**Executive Summary:**
Based on the analysis of your resume against the position requirements, here's comprehensive feedback to help improve your candidacy.

**Strengths:**
- Strong technical background
- Relevant industry experience
- Good educational foundation

**Areas for Improvement:**

**Skill Development:**
1. **Priority Skills to Develop:**
   - Advanced Python programming
   - Cloud computing (AWS/Azure)
   - Machine learning frameworks

2. **Learning Recommendations:**
   - Take online courses in missing technical areas
   - Build portfolio projects demonstrating new skills
   - Contribute to open source projects

**Experience Enhancement:**
1. **Gain Relevant Experience:**
   - Seek projects that align with job requirements
   - Consider internships or volunteer opportunities
   - Network with professionals in the field

**Certification Recommendations:**
1. **Priority Certifications:**
   - AWS Certified Solutions Architect
   - Professional Data Science Certification
   - Project Management Professional (PMP)

**Resume Enhancement Tips:**
- Quantify achievements with specific metrics
- Highlight relevant keywords from job description
- Improve formatting and structure
- Add relevant projects section

**Career Progression Advice:**
- Focus on building skills in high-demand areas
- Consider transitional roles to gain experience
- Build a professional network in your target industry
- Keep learning and stay updated with industry trends
"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured sections"""
        sections = {
            "executive_summary": "",
            "strengths": [],
            "improvements": [],
            "skill_recommendations": [],
            "experience_suggestions": [],
            "certification_recommendations": [],
            "resume_tips": [],
            "career_advice": []
        }
        
        # Simple parsing logic - can be enhanced with more sophisticated NLP
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if "executive summary" in line.lower():
                current_section = "executive_summary"
            elif "strengths" in line.lower():
                current_section = "strengths"
            elif "improvement" in line.lower():
                current_section = "improvements"
            elif "skill" in line.lower() and "recommendation" in line.lower():
                current_section = "skill_recommendations"
            elif "experience" in line.lower():
                current_section = "experience_suggestions"
            elif "certification" in line.lower():
                current_section = "certification_recommendations"
            elif "resume" in line.lower() and "tip" in line.lower():
                current_section = "resume_tips"
            elif "career" in line.lower():
                current_section = "career_advice"
            elif current_section and line.startswith('-'):
                # Add to current section
                if current_section in ["strengths", "resume_tips", "career_advice"]:
                    sections[current_section].append(line[1:].strip())
                else:
                    sections[current_section].append({"content": line[1:].strip(), "priority": 1})
            elif current_section == "executive_summary" and not line.startswith('#'):
                sections[current_section] += line + " "
        
        return sections
    
    def _create_feedback_sections(self, items: List[Dict[str, Any]]) -> List[FeedbackSection]:
        """Create FeedbackSection objects from parsed content"""
        sections = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                sections.append(FeedbackSection(
                    title=f"Recommendation {i+1}",
                    content=item.get("content", ""),
                    priority=item.get("priority", 3),
                    category="general",
                    actionable_items=[item.get("content", "")]
                ))
            else:
                sections.append(FeedbackSection(
                    title=f"Recommendation {i+1}",
                    content=str(item),
                    priority=3,
                    category="general",
                    actionable_items=[str(item)]
                ))
        return sections
    
    def _analyze_skill_gaps(self, context: Dict[str, Any]) -> List[str]:
        """Analyze skill gaps between candidate and requirements"""
        candidate_skills = set(str(skill).lower() for skill in context.get("candidate_skills", []))
        required_skills = set(str(skill).lower() for skill in context.get("required_skills", []))
        
        return list(required_skills - candidate_skills)
    
    def _analyze_experience_gaps(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze experience gaps"""
        return {
            "missing_experience": "Analysis of experience requirements vs candidate background",
            "suggested_improvements": ["Gain relevant project experience", "Seek mentorship opportunities"]
        }
    
    def _analyze_certification_gaps(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze certification gaps"""
        current_certs = context.get("candidate_certifications", [])
        required_certs = context.get("required_certifications", [])
        
        return {
            "current_certifications": current_certs,
            "missing_certifications": [cert for cert in required_certs if cert not in current_certs]
        }
    
    def _get_relevant_resources(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get relevant learning resources based on context"""
        resources = []
        
        # Add resources based on missing skills
        candidate_skills = [str(skill).lower() for skill in context.get("candidate_skills", [])]
        
        if any("python" in skill for skill in candidate_skills):
            resources.extend(self.resource_database.get("programming_languages", [])[:2])
        
        if any("web" in skill or "javascript" in skill for skill in candidate_skills):
            resources.extend(self.resource_database.get("web_development", [])[:2])
        
        # Add general resources
        resources.extend([
            {"name": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/", "provider": "LinkedIn", "type": "platform"},
            {"name": "Coursera", "url": "https://www.coursera.org/", "provider": "Coursera", "type": "platform"}
        ])
        
        return resources[:5]  # Limit to top 5 resources
    
    def _generate_next_steps(self, context: Dict[str, Any]) -> List[str]:
        """Generate specific next steps for the candidate"""
        next_steps = [
            "Review and implement the skill development recommendations",
            "Update your resume based on the enhancement tips provided",
            "Research and enroll in relevant certification programs",
            "Build portfolio projects to demonstrate new skills",
            "Network with professionals in your target industry"
        ]
        
        # Customize based on suitability verdict
        suitability = context.get("suitability_verdict", "").upper()
        if suitability == "HIGH":
            next_steps.insert(0, "Apply to similar positions as you're well-qualified")
        elif suitability == "MEDIUM":
            next_steps.insert(0, "Focus on addressing the key skill gaps before applying")
        elif suitability == "LOW":
            next_steps.insert(0, "Consider gaining more experience before applying to similar roles")
        
        return next_steps
    
    def _generate_fallback_feedback(self, request: FeedbackRequest, error: str) -> GeneratedFeedback:
        """Generate basic feedback when LLM call fails"""
        return GeneratedFeedback(
            candidate_name=request.candidate_name or "Candidate",
            position_title=request.position_title or "Position",
            overall_score=0,
            suitability_verdict="Unknown",
            confidence_level="Low",
            
            executive_summary=f"Unable to generate detailed feedback due to technical issues: {error}",
            strengths=["Please review your qualifications against the job requirements"],
            areas_for_improvement=[],
            skill_recommendations=[],
            experience_suggestions=[],
            certification_recommendations=[],
            resume_enhancement_tips=["Consider having your resume reviewed by a career professional"],
            career_progression_advice=["Focus on building relevant skills and experience"],
            
            generation_timestamp=datetime.now().isoformat(),
            feedback_type=request.feedback_type.value,
            tone=request.tone.value,
            llm_provider=self.provider.value,
            processing_time=0.0,
            
            learning_resources=[],
            next_steps=["Please try generating feedback again later"]
        )
    
    def batch_generate_feedback(self, requests: List[FeedbackRequest]) -> List[GeneratedFeedback]:
        """Generate feedback for multiple candidates"""
        results = []
        
        for request in requests:
            try:
                feedback = self.generate_feedback(request)
                results.append(feedback)
            except Exception as e:
                logger.error(f"Failed to generate feedback for {request.candidate_name}: {str(e)}")
                results.append(self._generate_fallback_feedback(request, str(e)))
        
        return results


# Utility functions for easy integration
def create_feedback_generator(provider: str = "mock", api_key: str = None) -> LLMFeedbackGenerator:
    """Create a feedback generator with specified provider"""
    provider_enum = LLMProvider(provider.lower())
    return LLMFeedbackGenerator(provider=provider_enum, api_key=api_key)


def generate_candidate_feedback(resume_data: Dict[str, Any],
                              job_description: Dict[str, Any],
                              analysis_results: Dict[str, Any],
                              candidate_name: str = None,
                              feedback_type: str = "comprehensive",
                              provider: str = "mock") -> Dict[str, Any]:
    """
    High-level function to generate feedback for a candidate
    
    Args:
        resume_data: Parsed resume information
        job_description: Job requirements and description
        analysis_results: Results from resume analysis
        candidate_name: Name of the candidate
        feedback_type: Type of feedback to generate
        provider: LLM provider to use
    
    Returns:
        Dictionary containing generated feedback
    """
    generator = create_feedback_generator(provider)
    
    request = FeedbackRequest(
        candidate_name=candidate_name,
        resume_data=resume_data,
        job_description=job_description,
        analysis_results=analysis_results,
        feedback_type=FeedbackType(feedback_type),
        tone=FeedbackTone.PROFESSIONAL
    )
    
    feedback = generator.generate_feedback(request)
    return asdict(feedback)


if __name__ == "__main__":
    # Example usage
    sample_resume = {
        "skills": ["Python", "SQL", "Excel"],
        "work_experience": [{"title": "Data Analyst", "company": "Tech Corp", "duration": "2 years"}],
        "certifications": [],
        "education": [{"degree": "BS Computer Science", "institution": "University"}]
    }
    
    sample_job = {
        "required_skills": ["Python", "Machine Learning", "AWS", "SQL"],
        "preferred_skills": ["Docker", "Kubernetes"],
        "experience_requirements": "3+ years in data science",
        "certifications": ["AWS Certified Solutions Architect"]
    }
    
    sample_analysis = {
        "overall_score": 65,
        "suitability_verdict": "MEDIUM",
        "confidence_level": "HIGH",
        "strengths": ["Strong SQL skills", "Relevant experience"],
        "weaknesses": ["Missing ML skills", "No cloud experience"]
    }
    
    # Generate feedback
    feedback = generate_candidate_feedback(
        resume_data=sample_resume,
        job_description=sample_job,
        analysis_results=sample_analysis,
        candidate_name="John Doe",
        feedback_type="comprehensive",
        provider="mock"
    )
    
    print("Generated Feedback:")
    print(f"Overall Score: {feedback['overall_score']}")
    print(f"Suitability: {feedback['suitability_verdict']}")
    print(f"Executive Summary: {feedback['executive_summary'][:200]}...")
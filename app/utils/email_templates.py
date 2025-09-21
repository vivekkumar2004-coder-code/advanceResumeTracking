"""
Email Template Manager

This module handles email template rendering with dynamic content
based on resume evaluation results.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailTemplateManager:
    """Manages email templates and content generation"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            # Default to templates/emails directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            templates_dir = os.path.join(base_dir, 'templates', 'emails')
        
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )
        
        # Add custom filters
        self.env.filters['format_score'] = self._format_score
        self.env.filters['format_skills'] = self._format_skills
        self.env.filters['format_date'] = self._format_date
        
    def _format_score(self, score: float) -> str:
        """Format relevance score with proper styling"""
        return f"{score:.1f}"
    
    def _format_skills(self, skills: list) -> str:
        """Format skills list for email display"""
        if not skills:
            return "None identified"
        return ", ".join(skills[:10]) + (f" and {len(skills) - 10} more" if len(skills) > 10 else "")
    
    def _format_date(self, date_obj: datetime) -> str:
        """Format date for email display"""
        return date_obj.strftime("%B %d, %Y")
    
    def get_template_for_score(self, relevance_score: float) -> str:
        """Determine appropriate template based on relevance score"""
        if relevance_score >= 70:
            return 'high_relevance.html'
        elif relevance_score >= 40:
            return 'medium_relevance.html'
        else:
            return 'low_relevance.html'
    
    def prepare_email_context(self, 
                            evaluation_result: Dict[str, Any], 
                            candidate_info: Dict[str, Any],
                            job_info: Dict[str, Any],
                            company_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare context variables for email template"""
        
        # Default company info
        if company_info is None:
            company_info = {
                'name': 'Our Company',
                'contact_email': 'hr@company.com',
                'website': 'https://company.com'
            }
        
        # Determine relevance level and match quality
        relevance_score = evaluation_result.get('relevance_score', 0)
        if relevance_score >= 70:
            match_quality = 'Excellent Match'
            relevance_level = 'High'
        elif relevance_score >= 40:
            match_quality = 'Good Match'
            relevance_level = 'Medium'
        else:
            match_quality = 'Developing Match'
            relevance_level = 'Low'
        
        # Prepare context
        context = {
            # Candidate information
            'candidate_name': candidate_info.get('name', 'Candidate'),
            'candidate_email': candidate_info.get('email', ''),
            
            # Job information
            'job_title': job_info.get('title', 'Position'),
            'job_department': job_info.get('department', ''),
            'job_location': job_info.get('location', ''),
            
            # Company information
            'company_name': company_info['name'],
            'contact_email': company_info['contact_email'],
            'company_website': company_info.get('website', ''),
            
            # Evaluation results
            'relevance_score': relevance_score,
            'skill_match_percentage': evaluation_result.get('skill_match_percentage', 0),
            'relevance_level': relevance_level,
            'match_quality': match_quality,
            'matching_skills': evaluation_result.get('matching_skills', []),
            'missing_skills': evaluation_result.get('missing_skills', []),
            'recommendations': evaluation_result.get('recommendations', []),
            'tfidf_similarity': evaluation_result.get('tfidf_similarity', 0),
            
            # Additional metrics
            'total_job_skills': evaluation_result.get('total_job_skills', 0),
            'total_matching_skills': len(evaluation_result.get('matching_skills', [])),
            
            # Dynamic links (these would be generated based on your system)
            'interview_link': self._generate_interview_link(candidate_info, job_info),
            'career_resources_link': self._generate_career_resources_link(),
            'learning_resources_link': self._generate_learning_resources_link(),
            
            # Metadata
            'evaluation_date': datetime.now(),
            'analysis_id': evaluation_result.get('analysis_id', ''),
        }
        
        return context
    
    def _generate_interview_link(self, candidate_info: Dict, job_info: Dict) -> str:
        """Generate interview scheduling link"""
        # This would integrate with your scheduling system
        base_url = "https://company.com/schedule-interview"
        candidate_id = candidate_info.get('id', '')
        job_id = job_info.get('id', '')
        return f"{base_url}?candidate={candidate_id}&job={job_id}"
    
    def _generate_career_resources_link(self) -> str:
        """Generate career resources link"""
        return "https://company.com/career-resources"
    
    def _generate_learning_resources_link(self) -> str:
        """Generate learning resources link"""
        return "https://company.com/learning-resources"
    
    def render_email_template(self, 
                            template_name: str, 
                            context: Dict[str, Any]) -> Dict[str, str]:
        """Render email template with context data"""
        try:
            template = self.env.get_template(template_name)
            html_content = template.render(**context)
            
            # Generate plain text version (simplified)
            text_content = self._html_to_text(html_content)
            
            return {
                'html': html_content,
                'text': text_content,
                'subject': self._generate_subject(context)
            }
            
        except TemplateNotFound:
            logger.error(f"Email template not found: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Error rendering email template {template_name}: {e}")
            raise
    
    def _generate_subject(self, context: Dict[str, Any]) -> str:
        """Generate email subject line based on context"""
        job_title = context.get('job_title', 'Position')
        relevance_score = context.get('relevance_score', 0)
        company_name = context.get('company_name', 'Company')
        
        if relevance_score >= 70:
            return f"🎉 Great match for {job_title} at {company_name}!"
        elif relevance_score >= 40:
            return f"📋 Your {job_title} application results from {company_name}"
        else:
            return f"🌟 Thank you for your interest in {job_title} at {company_name}"
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text (basic implementation)"""
        # This is a simplified conversion - you might want to use a library like html2text
        import re
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_content)
        
        # Replace common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def generate_personalized_email(self,
                                  evaluation_result: Dict[str, Any],
                                  candidate_info: Dict[str, Any],
                                  job_info: Dict[str, Any],
                                  company_info: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate complete personalized email"""
        
        # Prepare context
        context = self.prepare_email_context(
            evaluation_result, candidate_info, job_info, company_info
        )
        
        # Select appropriate template
        template_name = self.get_template_for_score(
            evaluation_result.get('relevance_score', 0)
        )
        
        # Render email
        email_content = self.render_email_template(template_name, context)
        
        return {
            'to_email': candidate_info.get('email'),
            'to_name': candidate_info.get('name'),
            'subject': email_content['subject'],
            'html_content': email_content['html'],
            'text_content': email_content['text'],
            'template_used': template_name,
            'relevance_score': evaluation_result.get('relevance_score', 0)
        }
    
    def get_available_templates(self) -> List[str]:
        """Get list of available email templates"""
        return list(EMAIL_TEMPLATES.keys())

# Custom email templates for different scenarios
EMAIL_TEMPLATES = {
    'high_relevance': {
        'name': 'High Relevance Match',
        'description': 'For candidates with 70%+ relevance score',
        'subject_template': '🎉 Great match for {job_title} at {company_name}!',
        'tone': 'enthusiastic'
    },
    'medium_relevance': {
        'name': 'Medium Relevance Match', 
        'description': 'For candidates with 40-69% relevance score',
        'subject_template': '📋 Your {job_title} application results from {company_name}',
        'tone': 'encouraging'
    },
    'low_relevance': {
        'name': 'Low Relevance Match',
        'description': 'For candidates with <40% relevance score',
        'subject_template': '🌟 Thank you for your interest in {job_title} at {company_name}',
        'tone': 'supportive'
    }
}

# Global template manager instance
email_templates = EmailTemplateManager()
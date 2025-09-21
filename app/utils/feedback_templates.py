"""
Feedback Templates and Prompt Configuration

This module contains comprehensive templates and prompts for generating
personalized feedback across different scenarios and contexts.

Features:
- Structured prompt templates for different feedback types
- Customizable tone and style options
- Industry-specific templates
- Multi-language support preparation
- Template versioning and management

Author: Automated Resume Relevance System
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import json


class IndustryType(Enum):
    """Different industry types for specialized feedback"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    MARKETING = "marketing"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    SALES = "sales"
    OPERATIONS = "operations"
    GENERAL = "general"


class ExperienceLevel(Enum):
    """Experience levels for tailored feedback"""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    EXECUTIVE = "executive"
    CAREER_CHANGE = "career_change"


@dataclass
class FeedbackTemplate:
    """Template structure for feedback generation"""
    name: str
    description: str
    prompt: str
    industry: IndustryType
    experience_level: ExperienceLevel
    tone_variations: Dict[str, str]
    variables: List[str]
    version: str = "1.0"


class FeedbackTemplateManager:
    """Manager for feedback templates and prompts"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.industry_specific_prompts = self._initialize_industry_prompts()
        self.tone_modifiers = self._initialize_tone_modifiers()
        self.cultural_considerations = self._initialize_cultural_considerations()
    
    def _initialize_templates(self) -> Dict[str, FeedbackTemplate]:
        """Initialize comprehensive feedback templates"""
        templates = {}
        
        # Comprehensive Analysis Template
        templates["comprehensive_analysis"] = FeedbackTemplate(
            name="Comprehensive Analysis",
            description="Complete resume analysis with all components",
            prompt="""
You are an expert HR consultant and career advisor with 15+ years of experience in talent acquisition and career development. You have helped thousands of candidates improve their profiles and land their dream jobs.

**ANALYSIS CONTEXT:**
Candidate: {candidate_name}
Position: {position_title} at {company_name}
Industry: {industry}
Experience Level: {experience_level}

**RESUME SUMMARY:**
{resume_summary}

**JOB REQUIREMENTS:**
{job_requirements}

**QUANTITATIVE ANALYSIS:**
- Overall Relevance Score: {overall_score}/100
- Suitability Verdict: {suitability_verdict}
- Confidence Level: {confidence_level}
- Component Breakdown: {component_analysis}

**DETAILED COMPONENT SCORES:**
- Semantic Similarity: {semantic_score}/100
- Keyword Matching: {keyword_score}/100
- Experience Alignment: {experience_score}/100
- Skill Coverage: {skill_score}/100
- Certification Match: {certification_score}/100

**INSTRUCTIONS:**
Provide comprehensive, actionable feedback in a {tone} tone that includes:

1. **Executive Summary** (2-3 sentences)
   - Overall assessment of candidacy strength
   - Primary focus areas for improvement
   - Timeline for readiness enhancement

2. **Key Strengths** (3-5 bullet points)
   - Highlight specific qualifications that align well
   - Quantify achievements where possible
   - Note transferable skills and experiences

3. **Critical Improvement Areas** (Prioritized list)
   For each area, provide:
   - Specific skill or qualification gap
   - Impact on candidacy (High/Medium/Low priority)
   - Concrete steps to address the gap
   - Estimated timeline for improvement
   - Resources and learning pathways

4. **Skill Development Roadmap**
   - Priority 1 skills (must-have for role)
   - Priority 2 skills (significantly improve chances)
   - Priority 3 skills (nice-to-have/future growth)
   - Specific learning resources, courses, and certifications
   - Project ideas to demonstrate new skills

5. **Experience Enhancement Strategies**
   - Ways to gain relevant experience
   - Volunteer opportunities and side projects
   - Networking and mentorship recommendations
   - Alternative pathways to build credibility

6. **Resume Optimization Recommendations**
   - Keywords to incorporate from job description
   - Formatting and structure improvements
   - Achievement quantification opportunities
   - Section reorganization suggestions

7. **Career Progression Strategy**
   - Short-term goals (3-6 months)
   - Medium-term objectives (6-12 months)
   - Long-term career trajectory alignment
   - Alternative role considerations

8. **Industry-Specific Insights**
   - Current market trends and demands
   - Emerging skills and technologies
   - Professional development opportunities
   - Network building strategies

**OUTPUT FORMAT:**
Provide structured, scannable feedback with clear headings, bullet points, and actionable items. Use specific examples and avoid generic advice. Include measurable goals and timelines where possible.

**TONE GUIDELINES:**
- Be honest but constructive
- Focus on solutions, not just problems
- Provide hope and clear pathways forward
- Use industry-appropriate language
- Balance encouragement with realism
            """,
            industry=IndustryType.GENERAL,
            experience_level=ExperienceLevel.MID_LEVEL,
            tone_variations={
                "professional": "formal, direct, and business-focused",
                "encouraging": "supportive, positive, and motivational",
                "constructive": "balanced, honest, and solution-oriented",
                "detailed": "thorough, analytical, and comprehensive",
                "concise": "brief, focused, and to-the-point"
            },
            variables=[
                "candidate_name", "position_title", "company_name", "industry", 
                "experience_level", "resume_summary", "job_requirements", 
                "overall_score", "suitability_verdict", "confidence_level",
                "component_analysis", "semantic_score", "keyword_score", 
                "experience_score", "skill_score", "certification_score", "tone"
            ]
        )
        
        # Skill Gap Analysis Template
        templates["skill_gap_analysis"] = FeedbackTemplate(
            name="Skill Gap Analysis",
            description="Focused analysis of skill mismatches and development",
            prompt="""
You are a technical skills assessor and learning specialist with expertise in career development and skill acquisition strategies.

**SKILL ANALYSIS CONTEXT:**
Position: {position_title}
Industry: {industry}
Experience Level: {experience_level}

**CANDIDATE SKILLS INVENTORY:**
Technical Skills: {candidate_technical_skills}
Soft Skills: {candidate_soft_skills}
Tools & Technologies: {candidate_tools}
Skill Proficiency Levels: {skill_proficiency_levels}

**REQUIRED SKILLS ANALYSIS:**
Must-Have Skills: {required_skills}
Preferred Skills: {preferred_skills}
Emerging Skills: {emerging_skills}

**SKILL GAP ANALYSIS:**
Missing Critical Skills: {critical_skill_gaps}
Partially Matched Skills: {partial_skill_matches}
Skill Level Gaps: {skill_level_gaps}
Outdated Skills: {outdated_skills}

**MARKET INSIGHTS:**
Industry Skill Trends: {industry_trends}
Salary Impact of Skills: {skill_salary_impact}
Skill Demand Forecast: {skill_demand_forecast}

**INSTRUCTIONS:**
Provide detailed, actionable skill development feedback:

1. **Skill Gap Priority Matrix**
   - Critical gaps (immediate attention needed)
   - Important gaps (significant impact on candidacy)
   - Nice-to-have gaps (future consideration)

2. **Skill Development Roadmap**
   For each priority skill:
   - Current skill level assessment
   - Target proficiency level needed
   - Learning pathway recommendations
   - Estimated time investment
   - Practice and application opportunities

3. **Learning Resource Recommendations**
   - Free resources (courses, tutorials, documentation)
   - Paid courses and certifications
   - Books and industry publications
   - Online communities and forums
   - Mentorship and networking opportunities

4. **Hands-On Practice Suggestions**
   - Project ideas to build portfolio
   - Open source contribution opportunities
   - Industry challenges and competitions
   - Volunteer work possibilities

5. **Skill Validation Strategies**
   - Certification programs
   - Portfolio development
   - Professional references
   - Skill assessment platforms

6. **Timeline and Milestones**
   - 30-day quick wins
   - 90-day significant progress
   - 6-month competency targets
   - 1-year mastery goals

Provide specific, measurable recommendations with clear next steps.
            """,
            industry=IndustryType.TECHNOLOGY,
            experience_level=ExperienceLevel.MID_LEVEL,
            tone_variations={
                "technical": "detailed, precise, and technically accurate",
                "practical": "hands-on, actionable, and implementation-focused",
                "motivational": "encouraging, goal-oriented, and inspiring"
            },
            variables=[
                "position_title", "industry", "experience_level", 
                "candidate_technical_skills", "candidate_soft_skills", 
                "candidate_tools", "skill_proficiency_levels",
                "required_skills", "preferred_skills", "emerging_skills",
                "critical_skill_gaps", "partial_skill_matches", 
                "skill_level_gaps", "outdated_skills",
                "industry_trends", "skill_salary_impact", "skill_demand_forecast"
            ]
        )
        
        # Experience Enhancement Template
        templates["experience_enhancement"] = FeedbackTemplate(
            name="Experience Enhancement",
            description="Focused on building relevant work experience",
            prompt="""
You are a career development specialist with expertise in helping professionals build relevant experience and advance their careers.

**EXPERIENCE ANALYSIS:**
Candidate: {candidate_name}
Target Role: {position_title}
Current Experience Level: {experience_level}
Industry Target: {industry}

**CURRENT EXPERIENCE PROFILE:**
Work History: {work_experience}
Total Years Experience: {total_experience}
Relevant Experience: {relevant_experience}
Industry Experience: {industry_experience}
Leadership Experience: {leadership_experience}
Project Experience: {project_experience}

**TARGET ROLE REQUIREMENTS:**
Required Experience: {required_experience}
Preferred Background: {preferred_background}
Key Responsibilities: {key_responsibilities}
Success Metrics: {success_metrics}

**EXPERIENCE GAPS:**
Years of Experience Gap: {experience_gap_years}
Industry Experience Gap: {industry_gap}
Functional Experience Gap: {functional_gap}
Leadership Experience Gap: {leadership_gap}
Technical Experience Gap: {technical_gap}

**INSTRUCTIONS:**
Provide strategic experience development recommendations:

1. **Experience Gap Assessment**
   - Quantify experience shortfalls
   - Identify most critical experience needs
   - Assess transferable experience value

2. **Experience Building Strategy**
   - Internal opportunities at current company
   - External project and consulting work
   - Volunteer and pro bono opportunities
   - Side projects and personal ventures

3. **Alternative Experience Pathways**
   - Transitional roles and stepping stones
   - Cross-functional project participation
   - Industry association involvement
   - Mentoring and coaching relationships

4. **Portfolio and Evidence Building**
   - Case studies and project documentation
   - Quantifiable achievement metrics
   - Professional references and testimonials
   - Industry recognition and awards

5. **Network Development**
   - Professional associations and groups
   - Industry events and conferences
   - Online community participation
   - Mentorship connections

6. **Timeline and Milestones**
   - Quick experience wins (1-3 months)
   - Significant experience building (3-12 months)
   - Long-term experience strategy (1-3 years)

Focus on practical, achievable steps to build credible experience.
            """,
            industry=IndustryType.GENERAL,
            experience_level=ExperienceLevel.MID_LEVEL,
            tone_variations={
                "strategic": "high-level, planning-focused, and forward-thinking",
                "tactical": "specific, actionable, and implementation-focused",
                "supportive": "encouraging, understanding, and empathetic"
            },
            variables=[
                "candidate_name", "position_title", "experience_level", "industry",
                "work_experience", "total_experience", "relevant_experience",
                "industry_experience", "leadership_experience", "project_experience",
                "required_experience", "preferred_background", "key_responsibilities",
                "success_metrics", "experience_gap_years", "industry_gap",
                "functional_gap", "leadership_gap", "technical_gap"
            ]
        )
        
        # Certification and Training Template
        templates["certification_training"] = FeedbackTemplate(
            name="Certification and Training",
            description="Focused on professional development and certifications",
            prompt="""
You are a professional development advisor and certification specialist with deep knowledge of industry credentials and training pathways.

**CERTIFICATION ANALYSIS:**
Target Position: {position_title}
Industry: {industry}
Experience Level: {experience_level}

**CURRENT CREDENTIALS:**
Existing Certifications: {current_certifications}
Expiring Certifications: {expiring_certifications}
In-Progress Training: {in_progress_training}
Professional Licenses: {professional_licenses}

**CERTIFICATION REQUIREMENTS:**
Required Certifications: {required_certifications}
Preferred Certifications: {preferred_certifications}
Industry Standard Certifications: {industry_standards}
Emerging Certifications: {emerging_certifications}

**TRAINING NEEDS ANALYSIS:**
Technical Training Gaps: {technical_training_gaps}
Soft Skills Training Needs: {soft_skills_training}
Leadership Development Needs: {leadership_training}
Compliance Training Requirements: {compliance_training}

**INSTRUCTIONS:**
Provide comprehensive certification and training recommendations:

1. **Certification Priority Matrix**
   - Must-have certifications for role eligibility
   - High-impact certifications for advancement
   - Specialized certifications for differentiation
   - Maintenance requirements for existing credentials

2. **Certification Roadmap**
   For each recommended certification:
   - Certification details and requirements
   - Prerequisites and preparation needed
   - Study timeline and resource requirements
   - Exam scheduling and costs
   - Maintenance and renewal requirements

3. **Training Program Recommendations**
   - Formal degree programs
   - Professional boot camps and intensives
   - Online courses and micro-learning
   - Vendor-specific training programs
   - Industry workshops and seminars

4. **Cost-Benefit Analysis**
   - Investment requirements (time, money, effort)
   - Career impact and salary potential
   - ROI calculations and payback period
   - Alternative credential options

5. **Learning Strategy**
   - Study schedule and time management
   - Learning resources and materials
   - Practice environments and labs
   - Study groups and peer support

6. **Implementation Timeline**
   - Immediate certification targets (3-6 months)
   - Medium-term goals (6-18 months)
   - Long-term professional development (1-3 years)

Prioritize certifications with highest career impact and relevance.
            """,
            industry=IndustryType.GENERAL,
            experience_level=ExperienceLevel.MID_LEVEL,
            tone_variations={
                "analytical": "data-driven, ROI-focused, and strategic",
                "practical": "actionable, realistic, and implementation-focused",
                "comprehensive": "thorough, detailed, and all-encompassing"
            },
            variables=[
                "position_title", "industry", "experience_level",
                "current_certifications", "expiring_certifications", 
                "in_progress_training", "professional_licenses",
                "required_certifications", "preferred_certifications",
                "industry_standards", "emerging_certifications",
                "technical_training_gaps", "soft_skills_training",
                "leadership_training", "compliance_training"
            ]
        )
        
        return templates
    
    def _initialize_industry_prompts(self) -> Dict[IndustryType, Dict[str, str]]:
        """Initialize industry-specific prompt modifications"""
        return {
            IndustryType.TECHNOLOGY: {
                "context": "Focus on technical skills, programming languages, frameworks, cloud technologies, and agile methodologies.",
                "priorities": "Emphasize hands-on coding experience, system design knowledge, and continuous learning.",
                "resources": "Include GitHub projects, Stack Overflow contributions, technical blogs, and open source involvement.",
                "trends": "Consider AI/ML, cloud computing, DevOps, cybersecurity, and emerging technologies."
            },
            IndustryType.HEALTHCARE: {
                "context": "Focus on clinical skills, certifications, patient care experience, and regulatory compliance.",
                "priorities": "Emphasize patient outcomes, safety protocols, continuing education, and interdisciplinary collaboration.",
                "resources": "Include medical journals, professional associations, clinical trials, and healthcare conferences.",
                "trends": "Consider telemedicine, health informatics, personalized medicine, and digital health technologies."
            },
            IndustryType.FINANCE: {
                "context": "Focus on financial analysis, risk management, regulatory knowledge, and quantitative skills.",
                "priorities": "Emphasize analytical thinking, attention to detail, ethical standards, and market knowledge.",
                "resources": "Include CFA, FRM, financial modeling courses, and industry publications.",
                "trends": "Consider fintech, cryptocurrency, ESG investing, and regulatory technology."
            },
            IndustryType.MARKETING: {
                "context": "Focus on digital marketing, analytics, creative skills, and customer insights.",
                "priorities": "Emphasize campaign performance, brand building, customer engagement, and ROI measurement.",
                "resources": "Include Google Analytics, social media platforms, marketing automation tools, and creative portfolios.",
                "trends": "Consider influencer marketing, personalization, marketing automation, and customer experience."
            }
        }
    
    def _initialize_tone_modifiers(self) -> Dict[str, str]:
        """Initialize tone modification guidelines"""
        return {
            "professional": {
                "style": "Use formal language, business terminology, and structured presentation",
                "approach": "Direct, factual, and results-oriented communication",
                "examples": "Provide data-driven examples and industry benchmarks"
            },
            "encouraging": {
                "style": "Use positive language, motivational phrasing, and supportive tone",
                "approach": "Focus on potential, growth opportunities, and achievable goals",
                "examples": "Highlight success stories and provide confidence-building examples"
            },
            "constructive": {
                "style": "Balance honest assessment with solution-oriented recommendations",
                "approach": "Acknowledge challenges while providing clear improvement pathways",
                "examples": "Show before/after scenarios and incremental progress steps"
            },
            "detailed": {
                "style": "Provide comprehensive analysis with thorough explanations",
                "approach": "Deep dive into each component with supporting evidence",
                "examples": "Include multiple options, alternatives, and detailed methodologies"
            },
            "concise": {
                "style": "Use brief, focused language with key points emphasized",
                "approach": "Prioritize most important recommendations and quick wins",
                "examples": "Provide bullet points, checklists, and summary recommendations"
            }
        }
    
    def _initialize_cultural_considerations(self) -> Dict[str, Dict[str, str]]:
        """Initialize cultural adaptation guidelines"""
        return {
            "global": {
                "communication": "Use inclusive language and avoid cultural assumptions",
                "examples": "Provide diverse industry examples and global perspectives",
                "resources": "Include international certifications and global career paths"
            },
            "regional": {
                "job_market": "Consider local job market conditions and opportunities",
                "networking": "Suggest region-specific professional networks and events",
                "regulations": "Account for local professional licensing and requirements"
            }
        }
    
    def get_template(self, template_name: str, 
                    industry: IndustryType = IndustryType.GENERAL,
                    experience_level: ExperienceLevel = ExperienceLevel.MID_LEVEL) -> Optional[FeedbackTemplate]:
        """Get a specific feedback template"""
        template = self.templates.get(template_name)
        if template:
            # Customize template based on industry and experience level
            template = self._customize_template(template, industry, experience_level)
        return template
    
    def _customize_template(self, template: FeedbackTemplate, 
                          industry: IndustryType, 
                          experience_level: ExperienceLevel) -> FeedbackTemplate:
        """Customize template based on industry and experience level"""
        # Add industry-specific context
        industry_context = self.industry_specific_prompts.get(industry, {})
        
        # Modify prompt based on experience level
        experience_modifications = self._get_experience_level_modifications(experience_level)
        
        # Create customized template
        customized_prompt = template.prompt
        
        if industry_context:
            customized_prompt += f"\n\n**INDUSTRY-SPECIFIC CONSIDERATIONS:**\n{industry_context.get('context', '')}"
        
        if experience_modifications:
            customized_prompt += f"\n\n**EXPERIENCE LEVEL ADAPTATIONS:**\n{experience_modifications}"
        
        # Return customized template
        return FeedbackTemplate(
            name=template.name,
            description=template.description,
            prompt=customized_prompt,
            industry=industry,
            experience_level=experience_level,
            tone_variations=template.tone_variations,
            variables=template.variables,
            version=template.version
        )
    
    def _get_experience_level_modifications(self, experience_level: ExperienceLevel) -> str:
        """Get experience level specific modifications"""
        modifications = {
            ExperienceLevel.ENTRY_LEVEL: """
- Focus on educational background and academic projects
- Emphasize internships, volunteer work, and transferable skills
- Provide guidance on building initial professional experience
- Suggest entry-level positions and career starter programs
- Include mentorship and networking recommendations for beginners
            """,
            ExperienceLevel.MID_LEVEL: """
- Balance skill development with leadership opportunities
- Focus on specialization and expertise deepening
- Provide guidance on career advancement and promotion readiness
- Suggest industry recognition and thought leadership opportunities
- Include professional development and continuous learning recommendations
            """,
            ExperienceLevel.SENIOR_LEVEL: """
- Focus on strategic thinking and leadership capabilities
- Emphasize team management and organizational impact
- Provide guidance on executive presence and industry influence
- Suggest board positions, speaking opportunities, and thought leadership
- Include succession planning and mentoring responsibilities
            """,
            ExperienceLevel.EXECUTIVE: """
- Focus on vision, strategy, and organizational transformation
- Emphasize stakeholder management and business results
- Provide guidance on executive positioning and market presence
- Suggest board appointments, advisory roles, and industry leadership
- Include legacy building and succession planning considerations
            """,
            ExperienceLevel.CAREER_CHANGE: """
- Focus on transferable skills and relevant experience translation
- Emphasize educational programs and skill acquisition strategies
- Provide guidance on network building in new industry
- Suggest transitional roles and stepping stone opportunities
- Include industry immersion and cultural adaptation recommendations
            """
        }
        return modifications.get(experience_level, "")
    
    def list_available_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific template"""
        template = self.templates.get(template_name)
        if template:
            return {
                "name": template.name,
                "description": template.description,
                "industry": template.industry.value,
                "experience_level": template.experience_level.value,
                "variables": template.variables,
                "version": template.version,
                "tone_variations": list(template.tone_variations.keys())
            }
        return None
    
    def validate_template_variables(self, template_name: str, provided_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required variables are provided for a template"""
        template = self.templates.get(template_name)
        if not template:
            return {"valid": False, "error": f"Template '{template_name}' not found"}
        
        missing_variables = []
        for var in template.variables:
            if var not in provided_variables:
                missing_variables.append(var)
        
        return {
            "valid": len(missing_variables) == 0,
            "missing_variables": missing_variables,
            "provided_variables": list(provided_variables.keys()),
            "required_variables": template.variables
        }


# Singleton instance for global access
template_manager = FeedbackTemplateManager()


# Convenience functions
def get_comprehensive_template(industry: str = "general", experience: str = "mid_level") -> Optional[FeedbackTemplate]:
    """Get comprehensive analysis template"""
    return template_manager.get_template(
        "comprehensive_analysis",
        IndustryType(industry.lower()),
        ExperienceLevel(experience.lower())
    )


def get_skill_gap_template(industry: str = "technology", experience: str = "mid_level") -> Optional[FeedbackTemplate]:
    """Get skill gap analysis template"""
    return template_manager.get_template(
        "skill_gap_analysis",
        IndustryType(industry.lower()),
        ExperienceLevel(experience.lower())
    )


def list_template_names() -> List[str]:
    """List all available template names"""
    return template_manager.list_available_templates()


def get_template_variables(template_name: str) -> List[str]:
    """Get required variables for a template"""
    info = template_manager.get_template_info(template_name)
    return info["variables"] if info else []


if __name__ == "__main__":
    # Example usage
    print("Available Templates:")
    for template_name in list_template_names():
        info = template_manager.get_template_info(template_name)
        print(f"- {info['name']}: {info['description']}")
        print(f"  Variables: {len(info['variables'])}")
        print(f"  Tone Variations: {info['tone_variations']}")
        print()
    
    # Get a specific template
    template = get_comprehensive_template("technology", "mid_level")
    if template:
        print(f"Template: {template.name}")
        print(f"Industry: {template.industry.value}")
        print(f"Experience Level: {template.experience_level.value}")
        print(f"Variables: {template.variables[:5]}...")  # First 5 variables
"""
Advanced Resume Parser Module

This module provides comprehensive text extraction and entity parsing for resume files.
Supports PDF (using PyMuPDF and pdfplumber) and DOCX (using python-docx) formats.
Extracts structured information including skills, certifications, experience, and education.
Enhanced with skill normalization for improved matching accuracy.
"""

import re
import fitz  # PyMuPDF
import pdfplumber
import docx
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from .skill_normalizer import SkillNormalizer, create_skill_normalizer
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import os
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """
    Advanced resume parser for extracting structured information from PDF and DOCX files.
    Enhanced with skill normalization capabilities.
    """
    
    def __init__(self, use_skill_normalization: bool = True):
        # Initialize skill normalizer if requested
        self.skill_normalizer = create_skill_normalizer(min_similarity_threshold=0.7) if use_skill_normalization else None
        
        # Common section headers that might appear in resumes
        self.section_patterns = {
            'personal_info': [
                r'personal\s+information', r'contact\s+information', r'contact\s+details',
                r'personal\s+details', r'profile', r'about\s+me'
            ],
            'summary': [
                r'summary', r'professional\s+summary', r'career\s+summary', r'objective',
                r'career\s+objective', r'professional\s+objective', r'profile\s+summary'
            ],
            'experience': [
                r'experience', r'work\s+experience', r'professional\s+experience',
                r'employment\s+history', r'career\s+history', r'work\s+history',
                r'professional\s+background', r'employment'
            ],
            'education': [
                r'education', r'educational\s+background', r'academic\s+background',
                r'qualifications', r'academic\s+qualifications'
            ],
            'skills': [
                r'skills', r'technical\s+skills', r'core\s+competencies',
                r'key\s+skills', r'expertise', r'competencies', r'abilities'
            ],
            'certifications': [
                r'certifications', r'certificates', r'professional\s+certifications',
                r'licenses', r'credentials', r'achievements'
            ],
            'projects': [
                r'projects', r'key\s+projects', r'notable\s+projects',
                r'project\s+experience', r'project\s+work'
            ]
        }
        
        # Skills patterns for better extraction
        self.technical_skills = [
            # Programming languages
            r'\b(?:python|java|javascript|js|typescript|ts|c\+\+|cpp|c#|csharp|php|ruby|go|rust|swift|kotlin|scala|r|matlab|perl|shell|bash|powershell)\b',
            # Web technologies
            r'\b(?:html5?|css3?|react|reactjs|angular|angularjs|vue|vuejs|node\.?js|nodejs|express|django|flask|fastapi|spring|springboot|laravel|rails|asp\.net|bootstrap|jquery)\b',
            # Databases
            r'\b(?:sql|mysql|postgresql|postgres|mongodb|oracle|sqlite|redis|elasticsearch|cassandra|dynamodb|neo4j|nosql)\b',
            # Cloud platforms
            r'\b(?:aws|amazon\s+web\s+services|azure|microsoft\s+azure|gcp|google\s+cloud|heroku|digitalocean|linode)\b',
            # DevOps tools
            r'\b(?:docker|kubernetes|k8s|jenkins|gitlab|github|git|ci/cd|terraform|ansible|chef|puppet|vagrant)\b',
            # Data science
            r'\b(?:pandas|numpy|matplotlib|seaborn|plotly|jupyter|scikit-learn|sklearn|tensorflow|pytorch|keras|spark|hadoop|tableau|powerbi|excel)\b',
            # Others
            r'\b(?:api|rest|restful|graphql|microservices|agile|scrum|kanban|jira|confluence|linux|unix|windows|macos)\b'
        ]
        
        # Certification patterns
        self.certification_patterns = [
            r'\b(?:aws\s+certified|azure\s+certified|google\s+cloud\s+certified)\b',
            r'\b(?:cisco|ccna|ccnp|ccie)\b',
            r'\b(?:pmp|prince2|itil|cisa|cissp|cism)\b',
            r'\b(?:mcsa|mcse|mcts|mcp)\b',
            r'\b(?:oracle\s+certified|ocp|oca)\b',
            r'\b(?:comptia|security\+|network\+|a\+)\b',
            r'\b(?:certified\s+kubernetes|ckad|cka)\b',
            r'\b(?:scrum\s+master|product\s+owner|csm|cpo)\b'
        ]

    def parse_resume(self, file_path: str) -> Dict:
        """
        Main method to parse a resume file and extract structured information
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            Dict: Structured resume information
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._parse_pdf_resume(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._parse_docx_resume(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {str(e)}")
            return {
                'error': f"Failed to parse resume: {str(e)}",
                'raw_text': '',
                'sections': {},
                'entities': {}
            }

    def _parse_pdf_resume(self, file_path: str) -> Dict:
        """
        Parse PDF resume using both PyMuPDF and pdfplumber for comprehensive extraction
        """
        result = {
            'raw_text': '',
            'sections': {},
            'entities': {},
            'metadata': {}
        }
        
        try:
            # Method 1: PyMuPDF for basic text extraction and metadata
            with fitz.open(file_path) as doc:
                result['metadata'] = {
                    'page_count': doc.page_count,
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'file_size': os.path.getsize(file_path)
                }
                
                # Extract text from all pages
                text_blocks = []
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    text_blocks.append(page.get_text())
                
                result['raw_text'] = '\n'.join(text_blocks)
            
            # Method 2: pdfplumber for better structure preservation
            structured_text = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Extract text with better formatting preservation
                    page_text = page.extract_text()
                    if page_text:
                        structured_text.append(page_text)
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            table_text = self._process_table(table)
                            structured_text.append(table_text)
            
            # Use the better structured text if available
            if structured_text:
                result['raw_text'] = '\n\n'.join(structured_text)
            
            # Extract sections and entities
            result['sections'] = self._extract_sections(result['raw_text'])
            result['entities'] = self._extract_entities(result['raw_text'], result['sections'])
            
        except Exception as e:
            logger.error(f"Error in PDF parsing: {str(e)}")
            result['error'] = f"PDF parsing failed: {str(e)}"
        
        return result

    def _parse_docx_resume(self, file_path: str) -> Dict:
        """
        Parse DOCX resume with structure preservation
        """
        result = {
            'raw_text': '',
            'sections': {},
            'entities': {},
            'metadata': {}
        }
        
        try:
            doc = docx.Document(file_path)
            
            # Extract metadata
            props = doc.core_properties
            result['metadata'] = {
                'title': props.title or '',
                'author': props.author or '',
                'created': props.created.isoformat() if props.created else '',
                'modified': props.modified.isoformat() if props.modified else '',
                'file_size': os.path.getsize(file_path)
            }
            
            # Extract text with structure preservation
            full_text = []
            
            for element in doc.element.body:
                if isinstance(element, CT_P):
                    # It's a paragraph
                    paragraph = Paragraph(element, doc)
                    text = paragraph.text.strip()
                    if text:
                        # Check if it's a heading (bold, larger font, etc.)
                        is_heading = self._is_heading_paragraph(paragraph)
                        if is_heading:
                            full_text.append(f"\n=== {text} ===\n")
                        else:
                            full_text.append(text)
                            
                elif isinstance(element, CT_Tbl):
                    # It's a table
                    table = Table(element, doc)
                    table_text = self._process_docx_table(table)
                    full_text.append(table_text)
            
            result['raw_text'] = '\n'.join(full_text)
            
            # Extract sections and entities
            result['sections'] = self._extract_sections(result['raw_text'])
            result['entities'] = self._extract_entities(result['raw_text'], result['sections'])
            
        except Exception as e:
            logger.error(f"Error in DOCX parsing: {str(e)}")
            result['error'] = f"DOCX parsing failed: {str(e)}"
        
        return result

    def _is_heading_paragraph(self, paragraph) -> bool:
        """
        Determine if a paragraph is likely a heading based on formatting
        """
        try:
            # Check if paragraph has bold formatting
            for run in paragraph.runs:
                if run.bold:
                    return True
            
            # Check if it's a short line (likely a heading)
            if len(paragraph.text.strip()) < 50 and paragraph.text.strip().isupper():
                return True
                
            # Check if it matches section patterns
            text_lower = paragraph.text.lower().strip()
            for section_type, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.match(pattern, text_lower):
                        return True
                        
        except Exception:
            pass
        
        return False

    def _process_table(self, table: List[List[str]]) -> str:
        """
        Process table data from pdfplumber
        """
        if not table:
            return ""
        
        processed_rows = []
        for row in table:
            if row and any(cell for cell in row if cell):  # Skip empty rows
                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                processed_rows.append(" | ".join(cleaned_row))
        
        return "\n".join(processed_rows)

    def _process_docx_table(self, table: Table) -> str:
        """
        Process table data from docx
        """
        table_text = []
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                cell_text = cell.text.strip().replace('\n', ' ')
                row_text.append(cell_text)
            if any(text for text in row_text):  # Skip empty rows
                table_text.append(" | ".join(row_text))
        
        return "\n".join(table_text)

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract different sections from resume text
        """
        sections = {}
        text_lower = text.lower()
        
        for section_type, patterns in self.section_patterns.items():
            section_content = self._find_section_content(text, patterns)
            if section_content:
                sections[section_type] = section_content
        
        return sections

    def _find_section_content(self, text: str, patterns: List[str]) -> str:
        """
        Find content for a specific section using regex patterns
        """
        text_lines = text.split('\n')
        content_lines = []
        capturing = False
        
        for i, line in enumerate(text_lines):
            line_lower = line.lower().strip()
            
            # Check if this line starts a section we're looking for
            if any(re.search(pattern, line_lower) for pattern in patterns):
                capturing = True
                content_lines = []
                continue
            
            # Check if this line starts a different section
            elif capturing and line_lower and any(
                re.search(pattern, line_lower) 
                for section_patterns in self.section_patterns.values() 
                for pattern in section_patterns
            ):
                break
            
            # Collect content if we're in the right section
            elif capturing:
                content_lines.append(line.strip())
        
        # Clean up and return content
        content = '\n'.join(content_lines).strip()
        return content if len(content) > 10 else ''  # Only return substantial content

    def _extract_entities(self, text: str, sections: Dict[str, str]) -> Dict:
        """
        Extract specific entities like skills, certifications, experience details.
        Enhanced with skill normalization when available.
        """
        entities = {
            'skills': self._extract_skills(text, sections.get('skills', '')),
            'certifications': self._extract_certifications(text),
            'experience': self._extract_experience_details(sections.get('experience', '')),
            'education': self._extract_education_details(sections.get('education', '')),
            'contact_info': self._extract_contact_info(text),
            'personal_info': self._extract_personal_info(text)
        }
        
        # Add normalized skills and certifications if skill normalizer is available
        if self.skill_normalizer:
            entities['normalized_skills'] = self._normalize_skills(entities['skills'])
            entities['normalized_certifications'] = self._normalize_certifications(entities['certifications'])
        
        return entities

    def _extract_skills(self, text: str, skills_section: str) -> Dict:
        """
        Extract technical and soft skills
        """
        # Prioritize skills section if available
        search_text = skills_section if skills_section else text
        search_text_lower = search_text.lower()
        
        technical_skills = []
        for pattern in self.technical_skills:
            matches = re.findall(pattern, search_text_lower, re.IGNORECASE)
            technical_skills.extend(matches)
        
        # Remove duplicates and clean up
        technical_skills = list(set([skill.strip() for skill in technical_skills]))
        
        # Extract soft skills
        soft_skills_patterns = [
            r'\b(?:leadership|communication|teamwork|problem[\s-]solving|analytical|creative|organized|detail[\s-]oriented)\b',
            r'\b(?:time\s+management|project\s+management|collaboration|adaptability|critical\s+thinking)\b',
            r'\b(?:decision\s+making|mentoring|training|presentation|negotiation|customer\s+service)\b'
        ]
        
        soft_skills = []
        for pattern in soft_skills_patterns:
            matches = re.findall(pattern, search_text_lower, re.IGNORECASE)
            soft_skills.extend(matches)
        
        soft_skills = list(set([skill.strip() for skill in soft_skills]))
        
        return {
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'all_skills': technical_skills + soft_skills
        }

    def _extract_certifications(self, text: str) -> List[str]:
        """
        Extract certifications and professional credentials
        """
        certifications = []
        text_lower = text.lower()
        
        for pattern in self.certification_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            certifications.extend(matches)
        
        # Also look for general certification patterns
        cert_general_patterns = [
            r'certified\s+[\w\s]+',
            r'[\w\s]+\s+certified',
            r'[\w\s]+\s+certification'
        ]
        
        for pattern in cert_general_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            # Filter matches to avoid too generic results
            filtered_matches = [
                match.strip() for match in matches 
                if len(match.strip()) > 5 and len(match.strip()) < 50
            ]
            certifications.extend(filtered_matches)
        
        return list(set(certifications))

    def _extract_experience_details(self, experience_section: str) -> List[Dict]:
        """
        Extract detailed experience information
        """
        if not experience_section:
            return []
        
        experiences = []
        
        # Split by lines and look for job entries
        lines = experience_section.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_job:
                    experiences.append(current_job)
                    current_job = {}
                continue
            
            # Look for job titles and companies
            if self._looks_like_job_title(line):
                if current_job:
                    experiences.append(current_job)
                current_job = {'title': line, 'description': []}
            
            # Look for dates
            elif self._looks_like_date_range(line):
                if current_job:
                    current_job['duration'] = line
            
            # Everything else is description
            else:
                if current_job:
                    if 'description' not in current_job:
                        current_job['description'] = []
                    current_job['description'].append(line)
        
        # Don't forget the last job
        if current_job:
            experiences.append(current_job)
        
        # Clean up descriptions
        for exp in experiences:
            if 'description' in exp:
                exp['description'] = '\n'.join(exp['description'])
        
        return experiences

    def _looks_like_job_title(self, line: str) -> bool:
        """
        Heuristic to determine if a line looks like a job title
        """
        # Common job title indicators
        job_indicators = [
            'developer', 'engineer', 'manager', 'analyst', 'consultant',
            'specialist', 'coordinator', 'director', 'lead', 'senior',
            'junior', 'intern', 'associate', 'executive', 'officer'
        ]
        
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in job_indicators)

    def _looks_like_date_range(self, line: str) -> bool:
        """
        Heuristic to determine if a line contains date ranges
        """
        date_patterns = [
            r'\d{4}\s*-\s*\d{4}',
            r'\d{4}\s*-\s*present',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
            r'\d{1,2}/\d{4}',
            r'\d{4}'
        ]
        
        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in date_patterns)

    def _extract_education_details(self, education_section: str) -> List[Dict]:
        """
        Extract education information
        """
        if not education_section:
            return []
        
        education_entries = []
        lines = education_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for degree patterns
            degree_patterns = [
                r'\b(bachelor|master|phd|doctorate|associate|diploma|certificate)\b.*\b(in|of)\s+([^,\n]+)',
                r'\b(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|b\.?a\.?)\s+([^,\n]+)',
                r'\b(degree)\s+in\s+([^,\n]+)'
            ]
            
            for pattern in degree_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    groups = match.groups()
                    education_entries.append({
                        'degree': groups[0] if len(groups) > 0 else 'Unknown',
                        'field': groups[-1].strip() if len(groups) > 1 else 'Unknown',
                        'full_text': line
                    })
                    break
        
        return education_entries

    def _extract_contact_info(self, text: str) -> Dict:
        """
        Extract contact information
        """
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone pattern
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b\d{10}\b',
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact_info['phone'] = phone_match.group()
                break
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        return contact_info

    def _extract_personal_info(self, text: str) -> Dict:
        """
        Extract personal information like name
        """
        personal_info = {}
        
        # Try to extract name from the beginning of the resume
        lines = text.split('\n')
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line.split()) <= 4:
                # Likely a name if it's 2-4 words and doesn't contain common resume words
                common_words = ['resume', 'cv', 'curriculum', 'vitae', 'phone', 'email', 'address']
                if not any(word in line.lower() for word in common_words):
                    personal_info['name'] = line
                    break
        
        return personal_info

    def _normalize_skills(self, skills_data: Dict) -> Dict[str, Any]:
        """
        Normalize extracted skills using the skill normalizer.
        
        Args:
            skills_data: Dict containing technical_skills, soft_skills, etc.
            
        Returns:
            Dict with normalized skill data
        """
        if not self.skill_normalizer:
            return skills_data
        
        # Combine all skill types for normalization
        all_skills = []
        if 'technical_skills' in skills_data:
            all_skills.extend(skills_data['technical_skills'])
        if 'soft_skills' in skills_data:
            all_skills.extend(skills_data['soft_skills'])
        
        # Normalize the skill list
        normalized_result = self.skill_normalizer.normalize_skill_list(all_skills)
        
        return {
            'original_skills': skills_data,
            'all_skills_normalized': normalized_result,
            'normalized_technical_skills': [
                skill for skill in normalized_result['normalized_skills']
                if skill['category'] not in ['soft_skills', 'unknown'] and skill['confidence'] > 0.6
            ],
            'normalized_soft_skills': [
                skill for skill in normalized_result['normalized_skills']
                if skill['category'] == 'soft_skills' and skill['confidence'] > 0.6
            ],
            'skill_statistics': normalized_result['statistics'],
            'category_distribution': normalized_result['category_distribution'],
            'skill_vectors': normalized_result['skill_vectors']
        }
    
    def _normalize_certifications(self, certifications: List[str]) -> Dict[str, Any]:
        """
        Normalize extracted certifications using the skill normalizer.
        
        Args:
            certifications: List of certification strings
            
        Returns:
            Dict with normalized certification data
        """
        if not self.skill_normalizer or not certifications:
            return {'original_certifications': certifications, 'normalized': []}
        
        # Normalize the certification list
        normalized_result = self.skill_normalizer.normalize_certification_list(certifications)
        
        return {
            'original_certifications': certifications,
            'normalized_certifications': normalized_result['normalized_certifications'],
            'certification_statistics': normalized_result['statistics'],
            'category_distribution': normalized_result['category_distribution'],
            'high_confidence_certifications': [
                cert for cert in normalized_result['normalized_certifications']
                if cert['confidence'] > 0.8
            ]
        }


def extract_resume_entities(file_path: str) -> Dict:
    """
    Convenience function to extract entities from a resume file
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        Dict: Extracted resume information and entities
    """
    parser = ResumeParser(use_skill_normalization=True)
    return parser.parse_resume(file_path)


def parse_resume_file(file_path: str) -> Dict:
    """
    Convenience function to parse a resume file
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Dict: Extracted resume information and entities
    """
    parser = ResumeParser(use_skill_normalization=True)  # Enable skill normalization by default
    return parser.parse_resume(file_path)


# Legacy function for backward compatibility
def parse_resume_file_legacy(file_path: str) -> Dict:
    """
    Legacy function for backward compatibility
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Dict: Extracted resume information and entities
    """
    parser = ResumeParser(use_skill_normalization=False)  # Disable for legacy compatibility


# Example usage and testing function
def test_resume_parser():
    """
    Test function to demonstrate the resume parser capabilities
    """
    parser = ResumeParser(use_skill_normalization=True)  # Enable skill normalization
    
    # Test with sample text
    sample_text = """
    John Doe
    Senior Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in Python development
    
    TECHNICAL SKILLS
    Programming Languages: Python, JavaScript, Java, SQL
    Frameworks: Django, React, Flask
    Databases: PostgreSQL, MongoDB
    Cloud: AWS, Docker, Kubernetes
    
    PROFESSIONAL EXPERIENCE
    Senior Software Engineer | TechCorp Inc | 2020 - Present
    - Led development of microservices architecture
    - Implemented CI/CD pipelines using Jenkins
    - Mentored junior developers
    
    Software Engineer | StartupCo | 2018 - 2020
    - Developed web applications using Django
    - Optimized database performance
    
    EDUCATION
    Bachelor of Science in Computer Science | University of Tech | 2018
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    Certified Scrum Master
    """
    
    result = {
        'raw_text': sample_text,
        'sections': parser._extract_sections(sample_text),
        'entities': {}
    }
    
    result['entities'] = parser._extract_entities(sample_text, result['sections'])
    
    print("=== Resume Parser Test Results ===")
    print(f"Sections found: {list(result['sections'].keys())}")
    print(f"Skills: {result['entities']['skills']['technical_skills'][:5]}")
    print(f"Certifications: {result['entities']['certifications']}")
    print(f"Contact: {result['entities']['contact_info']}")
    
    return result

if __name__ == "__main__":
    test_resume_parser()
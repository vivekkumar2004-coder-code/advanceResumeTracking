"""
Skill Normalizer Module

This module provides functionality to normalize extracted skills and certifications
by mapping them to a standardized skill taxonomy using fuzzy matching algorithms.
Prepares normalized data for semantic similarity engine integration.

Author: AI Assistant
Date: September 2025
"""

import re
import json
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import numpy as np
from fuzzywuzzy import fuzz, process
from fuzzywuzzy.process import extract
import jellyfish


class SkillTaxonomy:
    """Standardized skill taxonomy with hierarchical categories and mappings."""
    
    def __init__(self):
        self.skill_categories = self._build_skill_taxonomy()
        self.certification_mappings = self._build_certification_mappings()
        self.skill_synonyms = self._build_skill_synonyms()
        self.reverse_mapping = self._build_reverse_mapping()
        
    def _build_skill_taxonomy(self) -> Dict[str, Dict[str, List[str]]]:
        """Build comprehensive skill taxonomy with categories and subcategories."""
        return {
            "programming_languages": {
                "compiled": ["Java", "C++", "C#", "Go", "Rust", "C", "Kotlin", "Swift", "Objective-C"],
                "interpreted": ["Python", "JavaScript", "Ruby", "PHP", "Perl", "R", "MATLAB"],
                "functional": ["Haskell", "Scala", "Clojure", "F#", "Erlang", "Elixir"],
                "web_languages": ["HTML", "CSS", "TypeScript", "Sass", "SCSS", "Less"],
                "scripting": ["Bash", "PowerShell", "Shell", "Zsh", "Fish", "AWK", "Sed"]
            },
            "web_technologies": {
                "frontend_frameworks": ["React", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", "Gatsby"],
                "backend_frameworks": ["Django", "Flask", "FastAPI", "Express.js", "Spring Boot", "Rails", "Laravel"],
                "css_frameworks": ["Bootstrap", "Tailwind CSS", "Material-UI", "Bulma", "Foundation"],
                "build_tools": ["Webpack", "Vite", "Parcel", "Rollup", "Gulp", "Grunt"],
                "testing": ["Jest", "Mocha", "Cypress", "Selenium", "Playwright", "Jasmine"]
            },
            "databases": {
                "relational": ["MySQL", "PostgreSQL", "SQL Server", "Oracle", "SQLite", "MariaDB"],
                "nosql": ["MongoDB", "Redis", "Cassandra", "CouchDB", "Neo4j", "DynamoDB"],
                "data_warehouses": ["Snowflake", "Redshift", "BigQuery", "Databricks", "Teradata"],
                "orm": ["SQLAlchemy", "Hibernate", "Prisma", "TypeORM", "Sequelize"]
            },
            "cloud_platforms": {
                "aws": ["AWS", "EC2", "S3", "Lambda", "RDS", "ECS", "EKS", "CloudFormation"],
                "azure": ["Azure", "Azure Functions", "Azure SQL", "Azure DevOps", "AKS"],
                "gcp": ["Google Cloud", "GCP", "App Engine", "Cloud Functions", "BigQuery", "GKE"],
                "containerization": ["Docker", "Kubernetes", "OpenShift", "Podman", "Helm"]
            },
            "data_science": {
                "libraries": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras"],
                "visualization": ["Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI", "D3.js"],
                "big_data": ["Apache Spark", "Hadoop", "Kafka", "Airflow", "Flink", "Storm"],
                "ml_ops": ["MLflow", "Kubeflow", "SageMaker", "Weights & Biases", "DVC"]
            },
            "devops": {
                "ci_cd": ["Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "Travis CI", "Azure DevOps"],
                "monitoring": ["Prometheus", "Grafana", "ELK Stack", "Splunk", "Datadog", "New Relic"],
                "infrastructure": ["Terraform", "Ansible", "Chef", "Puppet", "CloudFormation", "Pulumi"],
                "version_control": ["Git", "SVN", "Mercurial", "Perforce", "Bazaar"]
            },
            "mobile_development": {
                "native_ios": ["Swift", "Objective-C", "Xcode", "iOS SDK", "Core Data", "UIKit"],
                "native_android": ["Kotlin", "Java", "Android Studio", "Android SDK", "Room", "Jetpack"],
                "cross_platform": ["React Native", "Flutter", "Xamarin", "Ionic", "Cordova"]
            },
            "soft_skills": {
                "leadership": ["Team Leadership", "Project Management", "Strategic Planning", "Mentoring"],
                "communication": ["Public Speaking", "Technical Writing", "Documentation", "Presentations"],
                "problem_solving": ["Analytical Thinking", "Debugging", "Troubleshooting", "Research"],
                "collaboration": ["Agile", "Scrum", "Kanban", "Cross-functional Teams", "Stakeholder Management"]
            },
            "security": {
                "application": ["OWASP", "Penetration Testing", "Vulnerability Assessment", "Secure Coding"],
                "network": ["Firewall", "VPN", "SSL/TLS", "Network Security", "Intrusion Detection"],
                "cloud_security": ["IAM", "Security Groups", "WAF", "KMS", "Secrets Management"],
                "compliance": ["SOC 2", "HIPAA", "GDPR", "PCI DSS", "ISO 27001"]
            }
        }
    
    def _build_certification_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Build standardized certification mappings."""
        return {
            "cloud_certifications": {
                "aws": ["AWS Solutions Architect", "AWS Developer", "AWS SysOps", "AWS DevOps Engineer",
                        "AWS Security", "AWS Data Analytics", "AWS Machine Learning"],
                "azure": ["Azure Fundamentals", "Azure Administrator", "Azure Developer", "Azure Solutions Architect",
                         "Azure DevOps Engineer", "Azure Security Engineer", "Azure Data Engineer"],
                "gcp": ["Google Cloud Architect", "Google Cloud Engineer", "Google Cloud Developer",
                       "Google Cloud Data Engineer", "Google Cloud Security Engineer"]
            },
            "programming_certifications": {
                "java": ["Oracle Certified Java Programmer", "Oracle Certified Java Developer", "Spring Certification"],
                "python": ["Python Institute Certifications", "Django Certification"],
                "microsoft": [".NET Certification", "C# Certification", "Azure Developer"],
                "javascript": ["Node.js Certification", "React Certification"]
            },
            "project_management": {
                "agile": ["Scrum Master", "Product Owner", "Agile Coach", "SAFe"],
                "traditional": ["PMP", "PRINCE2", "CAPM", "Project Management Professional"]
            },
            "data_certifications": {
                "analytics": ["Tableau Certified", "Power BI Certification", "Google Analytics"],
                "big_data": ["Cloudera Certification", "Hortonworks Certification", "Databricks Certification"],
                "machine_learning": ["TensorFlow Certification", "AWS ML Specialty", "Google ML Engineer"]
            },
            "security_certifications": {
                "general": ["CISSP", "CISM", "CISA", "Security+", "CEH", "OSCP"],
                "cloud_security": ["AWS Security Specialty", "Azure Security Engineer", "CCSP"]
            },
            "infrastructure": {
                "devops": ["Docker Certification", "Kubernetes Certification", "Terraform Certification"],
                "networking": ["CCNA", "CCNP", "Network+", "CISSP"]
            }
        }
    
    def _build_skill_synonyms(self) -> Dict[str, List[str]]:
        """Build comprehensive skill synonyms for better fuzzy matching."""
        return {
            # Programming Languages
            "JavaScript": ["JS", "ECMAScript", "Node.js", "NodeJS"],
            "Python": ["Python3", "Python 3", "Py"],
            "Java": ["Java 8", "Java 11", "Java 17", "JDK", "JRE"],
            "C#": ["C Sharp", "CSharp", "C-Sharp", ".NET"],
            "C++": ["C Plus Plus", "CPlusPlus", "C plus plus"],
            "TypeScript": ["TS", "TypeScript"],
            "PHP": ["PHP7", "PHP8", "Hypertext Preprocessor"],
            
            # Frameworks
            "React": ["ReactJS", "React.js"],
            "Angular": ["AngularJS", "Angular 2+", "Angular2"],
            "Vue.js": ["Vue", "VueJS"],
            "Django": ["Django Framework", "Django REST"],
            "Flask": ["Flask Framework", "Flask API"],
            "Spring Boot": ["Spring", "Spring Framework"],
            "Express.js": ["Express", "ExpressJS"],
            
            # Databases
            "MySQL": ["My SQL", "MySQL Database"],
            "PostgreSQL": ["Postgres", "PostgresSQL"],
            "MongoDB": ["Mongo DB", "Mongo"],
            "SQL Server": ["Microsoft SQL Server", "MS SQL", "MSSQL"],
            
            # Cloud Platforms
            "Amazon Web Services": ["AWS", "Amazon AWS"],
            "Google Cloud Platform": ["GCP", "Google Cloud"],
            "Microsoft Azure": ["Azure", "Azure Cloud"],
            
            # Tools
            "Git": ["Git Version Control", "GitHub", "GitLab"],
            "Docker": ["Docker Container", "Containerization"],
            "Kubernetes": ["K8s", "Kube", "K8"],
            "Jenkins": ["Jenkins CI", "Jenkins CI/CD"],
            
            # Methodologies
            "Agile": ["Agile Methodology", "Agile Development"],
            "Scrum": ["Scrum Methodology", "Scrum Framework"],
            "DevOps": ["Dev Ops", "Development Operations"],
            
            # Certifications
            "AWS Certified Solutions Architect": ["AWS Solutions Architect", "AWS SA", "Solutions Architect Associate"],
            "Certified Scrum Master": ["CSM", "Scrum Master Certification"],
            "Project Management Professional": ["PMP", "PMP Certification"],
        }
    
    def _build_reverse_mapping(self) -> Dict[str, str]:
        """Build reverse mapping from skills to their canonical forms."""
        reverse_map = {}
        
        # Map all skills in taxonomy to their canonical forms
        for category, subcategories in self.skill_categories.items():
            for subcategory, skills in subcategories.items():
                for skill in skills:
                    reverse_map[skill.lower()] = skill
        
        # Map all synonyms to their canonical forms
        for canonical, synonyms in self.skill_synonyms.items():
            for synonym in synonyms:
                reverse_map[synonym.lower()] = canonical
        
        return reverse_map
    
    def get_all_skills(self) -> Set[str]:
        """Get all skills from the taxonomy."""
        skills = set()
        for category, subcategories in self.skill_categories.items():
            for subcategory, skill_list in subcategories.items():
                skills.update(skill_list)
        return skills
    
    def get_all_certifications(self) -> Set[str]:
        """Get all certifications from the mappings."""
        certs = set()
        for category, subcategories in self.certification_mappings.items():
            for subcategory, cert_list in subcategories.items():
                certs.update(cert_list)
        return certs


class SkillNormalizer:
    """Main class for normalizing skills and certifications using fuzzy matching."""
    
    def __init__(self, min_similarity_threshold: float = 0.8):
        self.taxonomy = SkillTaxonomy()
        self.min_similarity_threshold = min_similarity_threshold
        self.skill_vectors_cache = {}
        
        # Prepare skill lists for fuzzy matching
        self.all_skills = list(self.taxonomy.get_all_skills())
        self.all_certifications = list(self.taxonomy.get_all_certifications())
        self.all_synonyms = list(self.taxonomy.skill_synonyms.keys())
        
        # Combined search space
        self.skill_search_space = self.all_skills + self.all_synonyms
        self.cert_search_space = self.all_certifications
    
    def normalize_skill(self, skill: str) -> Dict[str, Any]:
        """
        Normalize a single skill using fuzzy matching.
        
        Args:
            skill: Raw skill string to normalize
            
        Returns:
            Dict containing normalized skill, confidence, category, and metadata
        """
        if not skill or not skill.strip():
            return {
                "original": skill,
                "normalized": None,
                "confidence": 0.0,
                "category": None,
                "subcategory": None,
                "match_type": "no_match"
            }
        
        skill_clean = self._clean_skill_text(skill)
        
        # Try exact match first
        if skill_clean.lower() in self.taxonomy.reverse_mapping:
            canonical = self.taxonomy.reverse_mapping[skill_clean.lower()]
            category_info = self._find_skill_category(canonical)
            return {
                "original": skill,
                "normalized": canonical,
                "confidence": 1.0,
                "category": category_info["category"],
                "subcategory": category_info["subcategory"],
                "match_type": "exact"
            }
        
        # Fuzzy matching
        matches = process.extract(
            skill_clean, 
            self.skill_search_space, 
            scorer=fuzz.token_sort_ratio,
            limit=3
        )
        
        if not matches or matches[0][1] < (self.min_similarity_threshold * 100):
            return {
                "original": skill,
                "normalized": skill_clean,  # Keep original if no good match
                "confidence": 0.0,
                "category": "unknown",
                "subcategory": "unknown",
                "match_type": "no_match"
            }
        
        best_match, confidence = matches[0]
        
        # Get canonical form
        canonical = self.taxonomy.reverse_mapping.get(best_match.lower(), best_match)
        category_info = self._find_skill_category(canonical)
        
        return {
            "original": skill,
            "normalized": canonical,
            "confidence": confidence / 100.0,
            "category": category_info["category"],
            "subcategory": category_info["subcategory"],
            "match_type": "fuzzy",
            "alternatives": [{"skill": match, "confidence": conf / 100.0} 
                           for match, conf in matches[1:]]
        }
    
    def normalize_certification(self, certification: str) -> Dict[str, Any]:
        """
        Normalize a certification using fuzzy matching.
        
        Args:
            certification: Raw certification string to normalize
            
        Returns:
            Dict containing normalized certification and metadata
        """
        if not certification or not certification.strip():
            return {
                "original": certification,
                "normalized": None,
                "confidence": 0.0,
                "category": None,
                "subcategory": None,
                "match_type": "no_match"
            }
        
        cert_clean = self._clean_skill_text(certification)
        
        # Fuzzy matching for certifications
        matches = process.extract(
            cert_clean,
            self.cert_search_space,
            scorer=fuzz.token_set_ratio,
            limit=3
        )
        
        if not matches or matches[0][1] < (self.min_similarity_threshold * 100):
            return {
                "original": certification,
                "normalized": cert_clean,
                "confidence": 0.0,
                "category": "unknown",
                "subcategory": "unknown",
                "match_type": "no_match"
            }
        
        best_match, confidence = matches[0]
        category_info = self._find_certification_category(best_match)
        
        return {
            "original": certification,
            "normalized": best_match,
            "confidence": confidence / 100.0,
            "category": category_info["category"],
            "subcategory": category_info["subcategory"],
            "match_type": "fuzzy",
            "alternatives": [{"certification": match, "confidence": conf / 100.0} 
                           for match, conf in matches[1:]]
        }
    
    def normalize_skill_list(self, skills: List[str]) -> Dict[str, Any]:
        """
        Normalize a list of skills and return comprehensive analysis.
        
        Args:
            skills: List of raw skill strings
            
        Returns:
            Dict containing normalized skills, statistics, and categories
        """
        normalized_skills = []
        category_counts = defaultdict(int)
        confidence_scores = []
        
        for skill in skills:
            normalized = self.normalize_skill(skill)
            normalized_skills.append(normalized)
            
            if normalized["category"]:
                category_counts[normalized["category"]] += 1
            confidence_scores.append(normalized["confidence"])
        
        # Calculate statistics
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        high_confidence_count = sum(1 for score in confidence_scores if score > 0.8)
        
        return {
            "normalized_skills": normalized_skills,
            "statistics": {
                "total_skills": len(skills),
                "normalized_skills": len([s for s in normalized_skills if s["normalized"]]),
                "average_confidence": avg_confidence,
                "high_confidence_matches": high_confidence_count,
                "low_confidence_matches": len(skills) - high_confidence_count
            },
            "category_distribution": dict(category_counts),
            "skill_vectors": self._generate_skill_vectors(normalized_skills)
        }
    
    def normalize_certification_list(self, certifications: List[str]) -> Dict[str, Any]:
        """
        Normalize a list of certifications.
        
        Args:
            certifications: List of raw certification strings
            
        Returns:
            Dict containing normalized certifications and analysis
        """
        normalized_certs = []
        category_counts = defaultdict(int)
        confidence_scores = []
        
        for cert in certifications:
            normalized = self.normalize_certification(cert)
            normalized_certs.append(normalized)
            
            if normalized["category"]:
                category_counts[normalized["category"]] += 1
            confidence_scores.append(normalized["confidence"])
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return {
            "normalized_certifications": normalized_certs,
            "statistics": {
                "total_certifications": len(certifications),
                "normalized_certifications": len([c for c in normalized_certs if c["normalized"]]),
                "average_confidence": avg_confidence,
                "high_confidence_matches": sum(1 for score in confidence_scores if score > 0.8)
            },
            "category_distribution": dict(category_counts)
        }
    
    def calculate_skill_similarity(self, skills1: List[str], skills2: List[str]) -> Dict[str, Any]:
        """
        Calculate semantic similarity between two skill sets.
        
        Args:
            skills1: First set of skills
            skills2: Second set of skills
            
        Returns:
            Dict containing similarity scores and analysis
        """
        normalized1 = self.normalize_skill_list(skills1)
        normalized2 = self.normalize_skill_list(skills2)
        
        skills_set1 = {s["normalized"] for s in normalized1["normalized_skills"] if s["normalized"]}
        skills_set2 = {s["normalized"] for s in normalized2["normalized_skills"] if s["normalized"]}
        
        # Calculate Jaccard similarity
        intersection = skills_set1.intersection(skills_set2)
        union = skills_set1.union(skills_set2)
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # Calculate category overlap
        categories1 = set(normalized1["category_distribution"].keys())
        categories2 = set(normalized2["category_distribution"].keys())
        category_overlap = len(categories1.intersection(categories2)) / len(categories1.union(categories2)) if categories1.union(categories2) else 0.0
        
        return {
            "jaccard_similarity": jaccard_similarity,
            "category_overlap": category_overlap,
            "common_skills": list(intersection),
            "unique_to_first": list(skills_set1 - skills_set2),
            "unique_to_second": list(skills_set2 - skills_set1),
            "skill_vectors": {
                "skills1": normalized1["skill_vectors"],
                "skills2": normalized2["skill_vectors"]
            }
        }
    
    def _clean_skill_text(self, text: str) -> str:
        """Clean and standardize skill text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^(experience\s+with|knowledge\s+of|proficient\s+in|expert\s+in)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+(programming|language|framework|library|tool|platform|database)$', '', text, flags=re.IGNORECASE)
        
        # Handle version numbers
        text = re.sub(r'\s+v?\d+(\.\d+)*$', '', text)
        
        # Remove parentheses content
        text = re.sub(r'\([^)]*\)', '', text)
        
        return text.strip()
    
    def _find_skill_category(self, skill: str) -> Dict[str, str]:
        """Find the category and subcategory for a skill."""
        for category, subcategories in self.taxonomy.skill_categories.items():
            for subcategory, skills in subcategories.items():
                if skill in skills:
                    return {"category": category, "subcategory": subcategory}
        return {"category": "unknown", "subcategory": "unknown"}
    
    def _find_certification_category(self, certification: str) -> Dict[str, str]:
        """Find the category and subcategory for a certification."""
        for category, subcategories in self.taxonomy.certification_mappings.items():
            for subcategory, certs in subcategories.items():
                if certification in certs:
                    return {"category": category, "subcategory": subcategory}
        return {"category": "unknown", "subcategory": "unknown"}
    
    def _generate_skill_vectors(self, normalized_skills: List[Dict]) -> Dict[str, float]:
        """Generate skill category vectors for semantic analysis."""
        category_vector = defaultdict(float)
        total_skills = len(normalized_skills)
        
        if total_skills == 0:
            return {}
        
        for skill_info in normalized_skills:
            if skill_info["category"] and skill_info["category"] != "unknown":
                # Weight by confidence
                weight = skill_info["confidence"]
                category_vector[skill_info["category"]] += weight
        
        # Normalize vectors
        for category in category_vector:
            category_vector[category] /= total_skills
            
        return dict(category_vector)
    
    def get_skill_recommendations(self, current_skills: List[str], target_role: str = None) -> Dict[str, Any]:
        """
        Get skill recommendations based on current skills and target role.
        
        Args:
            current_skills: List of current skills
            target_role: Optional target role for recommendations
            
        Returns:
            Dict containing skill recommendations and analysis
        """
        normalized = self.normalize_skill_list(current_skills)
        current_categories = set(normalized["category_distribution"].keys())
        
        # Define role-specific skill requirements
        role_requirements = {
            "full_stack_developer": ["programming_languages", "web_technologies", "databases", "devops"],
            "data_scientist": ["programming_languages", "data_science", "databases", "cloud_platforms"],
            "devops_engineer": ["devops", "cloud_platforms", "databases", "programming_languages"],
            "mobile_developer": ["mobile_development", "programming_languages", "databases"],
            "security_engineer": ["security", "cloud_platforms", "devops", "programming_languages"]
        }
        
        recommendations = []
        missing_categories = []
        
        if target_role and target_role.lower() in role_requirements:
            required_categories = role_requirements[target_role.lower()]
            missing_categories = [cat for cat in required_categories if cat not in current_categories]
            
            # Recommend specific skills from missing categories
            for category in missing_categories:
                if category in self.taxonomy.skill_categories:
                    # Get popular skills from each subcategory
                    for subcategory, skills in self.taxonomy.skill_categories[category].items():
                        recommendations.extend(skills[:3])  # Top 3 skills per subcategory
        
        return {
            "current_skill_analysis": normalized,
            "target_role": target_role,
            "missing_categories": missing_categories,
            "recommended_skills": recommendations[:15],  # Limit to top 15
            "skill_gap_analysis": {
                "coverage_score": len(current_categories) / len(role_requirements.get(target_role.lower(), [])) if target_role else 0,
                "strength_areas": list(current_categories),
                "improvement_areas": missing_categories
            }
        }


def create_skill_normalizer(min_similarity_threshold: float = 0.8) -> SkillNormalizer:
    """Factory function to create a SkillNormalizer instance."""
    return SkillNormalizer(min_similarity_threshold)


# Example usage and testing
if __name__ == "__main__":
    # Initialize the skill normalizer
    normalizer = SkillNormalizer(min_similarity_threshold=0.7)
    
    # Test skill normalization
    test_skills = [
        "python programming", "react js", "node js", "my sql", "AWS cloud",
        "machine learning", "deep learning", "javascript", "html css",
        "kubernetes", "docker containers", "jenkins ci cd", "git version control"
    ]
    
    print("=== Skill Normalization Test ===")
    for skill in test_skills:
        normalized = normalizer.normalize_skill(skill)
        print(f"'{skill}' -> '{normalized['normalized']}' (confidence: {normalized['confidence']:.2f}, category: {normalized['category']})")
    
    # Test certification normalization
    test_certs = [
        "AWS Solutions Architect Associate", "Scrum Master Certification",
        "PMP Project Management", "Google Cloud Professional",
        "Oracle Java Developer Certified"
    ]
    
    print("\n=== Certification Normalization Test ===")
    for cert in test_certs:
        normalized = normalizer.normalize_certification(cert)
        print(f"'{cert}' -> '{normalized['normalized']}' (confidence: {normalized['confidence']:.2f})")
    
    # Test skill list normalization
    print("\n=== Skill List Analysis ===")
    result = normalizer.normalize_skill_list(test_skills)
    print(f"Total skills: {result['statistics']['total_skills']}")
    print(f"Average confidence: {result['statistics']['average_confidence']:.2f}")
    print("Category distribution:", result['category_distribution'])
    
    # Test skill recommendations
    print("\n=== Skill Recommendations ===")
    recommendations = normalizer.get_skill_recommendations(test_skills, "data_scientist")
    print(f"Coverage score: {recommendations['skill_gap_analysis']['coverage_score']:.2f}")
    print("Recommended skills:", recommendations['recommended_skills'][:5])
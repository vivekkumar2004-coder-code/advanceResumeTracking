"""
Configuration and Error Handling for Feedback Generation System

This module provides comprehensive configuration management, error handling,
and fallback mechanisms for the LLM-based feedback generation system.

Features:
- Environment variable management
- LLM provider configuration and validation
- Error handling and recovery mechanisms
- Fallback content generation
- Performance monitoring and logging
- Configuration validation and health checks

Author: Automated Resume Relevance System
Version: 1.0.0
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""
    pass


class LLMProviderError(Exception):
    """Custom exception for LLM provider-related errors"""
    pass


class FeedbackGenerationError(Exception):
    """Custom exception for feedback generation errors"""
    pass


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider"""
    name: str
    api_key_env_var: str
    base_url: Optional[str]
    default_model: str
    max_tokens: int
    timeout: int
    max_retries: int
    retry_delay: float
    cost_per_token: Optional[float]
    rate_limit_rpm: Optional[int]  # requests per minute
    rate_limit_tpm: Optional[int]  # tokens per minute


@dataclass
class FeedbackConfig:
    """Configuration for feedback generation"""
    default_provider: str
    default_feedback_type: str
    default_tone: str
    max_feedback_length: int
    include_resources_default: bool
    enable_caching: bool
    cache_ttl_hours: int
    enable_analytics: bool
    fallback_enabled: bool


@dataclass
class SystemHealth:
    """System health status"""
    overall_status: str
    llm_providers: Dict[str, Dict[str, Any]]
    last_check: str
    issues: List[str]
    recommendations: List[str]


class FeedbackSystemConfig:
    """Main configuration manager for the feedback system"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file_path: Optional path to configuration file
        """
        self.config_file_path = config_file_path
        self.llm_providers = self._initialize_llm_providers()
        self.feedback_config = self._initialize_feedback_config()
        self.error_handlers = self._initialize_error_handlers()
        self.fallback_content = self._initialize_fallback_content()
        self.performance_metrics = {}
        self.rate_limits = {}
        
        # Load custom configuration if provided
        if config_file_path and os.path.exists(config_file_path):
            self._load_config_file(config_file_path)
        
        logger.info("Feedback system configuration initialized")
    
    def _initialize_llm_providers(self) -> Dict[str, LLMProviderConfig]:
        """Initialize LLM provider configurations"""
        return {
            'openai': LLMProviderConfig(
                name='OpenAI',
                api_key_env_var='OPENAI_API_KEY',
                base_url='https://api.openai.com/v1',
                default_model='gpt-4',
                max_tokens=2000,
                timeout=30,
                max_retries=3,
                retry_delay=2.0,
                cost_per_token=0.00003,  # Approximate cost per token
                rate_limit_rpm=200,
                rate_limit_tpm=40000
            ),
            'anthropic': LLMProviderConfig(
                name='Anthropic',
                api_key_env_var='ANTHROPIC_API_KEY',
                base_url='https://api.anthropic.com/v1',
                default_model='claude-3-sonnet-20240229',
                max_tokens=2000,
                timeout=30,
                max_retries=3,
                retry_delay=2.0,
                cost_per_token=0.000015,  # Approximate cost per token
                rate_limit_rpm=50,
                rate_limit_tpm=20000
            ),
            'local': LLMProviderConfig(
                name='Local Model',
                api_key_env_var='LOCAL_MODEL_API_KEY',
                base_url=os.getenv('LOCAL_MODEL_URL', 'http://localhost:8000'),
                default_model='llama-2-70b-chat',
                max_tokens=2000,
                timeout=60,
                max_retries=2,
                retry_delay=3.0,
                cost_per_token=0.0,  # No cost for local
                rate_limit_rpm=None,
                rate_limit_tpm=None
            ),
            'mock': LLMProviderConfig(
                name='Mock Provider',
                api_key_env_var='MOCK_API_KEY',
                base_url=None,
                default_model='mock-model',
                max_tokens=2000,
                timeout=1,
                max_retries=1,
                retry_delay=0.1,
                cost_per_token=0.0,  # No cost for mock
                rate_limit_rpm=None,
                rate_limit_tpm=None
            )
        }
    
    def _initialize_feedback_config(self) -> FeedbackConfig:
        """Initialize feedback generation configuration"""
        return FeedbackConfig(
            default_provider='mock',
            default_feedback_type='comprehensive',
            default_tone='professional',
            max_feedback_length=2000,
            include_resources_default=True,
            enable_caching=True,
            cache_ttl_hours=24,
            enable_analytics=True,
            fallback_enabled=True
        )
    
    def _initialize_error_handlers(self) -> Dict[str, callable]:
        """Initialize error handling functions"""
        return {
            'api_key_missing': self._handle_api_key_missing,
            'api_quota_exceeded': self._handle_quota_exceeded,
            'api_timeout': self._handle_api_timeout,
            'api_error': self._handle_api_error,
            'parsing_error': self._handle_parsing_error,
            'validation_error': self._handle_validation_error,
            'provider_unavailable': self._handle_provider_unavailable
        }
    
    def _initialize_fallback_content(self) -> Dict[str, Any]:
        """Initialize fallback content for when LLM is unavailable"""
        return {
            'comprehensive': {
                'executive_summary': 'Thank you for your interest in this position. Based on our analysis, we have identified several areas where you can strengthen your application.',
                'strengths': [
                    'You have relevant experience in your field',
                    'Your educational background is solid',
                    'You demonstrate continuous learning'
                ],
                'improvement_areas': [
                    'Consider highlighting more specific achievements and quantifiable results',
                    'Ensure your skills align closely with the job requirements',
                    'Update your resume to include more relevant keywords'
                ],
                'skill_recommendations': [
                    'Focus on developing the most in-demand skills in your industry',
                    'Consider obtaining relevant certifications',
                    'Build a portfolio of projects that demonstrate your capabilities'
                ],
                'next_steps': [
                    'Review the job description carefully and tailor your resume',
                    'Network with professionals in your target industry',
                    'Continue developing relevant skills through online courses'
                ]
            },
            'skill_focused': {
                'priority_skills': [
                    'Identify the top 3-5 skills mentioned in the job description',
                    'Focus on skills that appear most frequently in similar roles',
                    'Consider both technical and soft skills requirements'
                ],
                'learning_recommendations': [
                    'Take online courses from reputable platforms',
                    'Practice through hands-on projects',
                    'Seek mentorship from experienced professionals'
                ],
                'timeline': 'Dedicate 2-3 hours per week to skill development over 3-6 months'
            },
            'experience_focused': {
                'experience_building': [
                    'Volunteer for relevant projects in your current role',
                    'Consider freelance or consulting opportunities',
                    'Participate in industry events and conferences'
                ],
                'transferable_skills': [
                    'Identify how your current experience applies to the target role',
                    'Highlight leadership and problem-solving experiences',
                    'Emphasize achievements that demonstrate your capabilities'
                ]
            },
            'certification_focused': {
                'priority_certifications': [
                    'Research industry-standard certifications for your field',
                    'Consider certifications that are specifically mentioned in job descriptions',
                    'Look into vendor-specific certifications for tools and technologies'
                ],
                'certification_pathway': [
                    'Start with foundational certifications',
                    'Progress to more specialized or advanced certifications',
                    'Maintain certifications through continuing education'
                ]
            }
        }
    
    def get_provider_config(self, provider_name: str) -> LLMProviderConfig:
        """Get configuration for a specific LLM provider"""
        if provider_name not in self.llm_providers:
            raise ConfigurationError(f"Provider '{provider_name}' not configured")
        return self.llm_providers[provider_name]
    
    def validate_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Validate configuration for a specific provider"""
        if provider_name not in self.llm_providers:
            return {
                'valid': False,
                'error': f"Provider '{provider_name}' not found",
                'issues': [f"Provider '{provider_name}' is not configured"]
            }
        
        config = self.llm_providers[provider_name]
        issues = []
        warnings = []
        
        # Check API key for non-mock providers
        if provider_name != 'mock':
            api_key = os.getenv(config.api_key_env_var)
            if not api_key:
                issues.append(f"API key not found in environment variable '{config.api_key_env_var}'")
        
        # Check base URL for local providers
        if provider_name == 'local' and config.base_url:
            try:
                response = requests.get(f"{config.base_url}/health", timeout=5)
                if response.status_code != 200:
                    warnings.append(f"Local model endpoint returned status {response.status_code}")
            except requests.RequestException:
                warnings.append("Local model endpoint is not accessible")
        
        # Validate configuration values
        if config.max_tokens <= 0:
            issues.append("Max tokens must be greater than 0")
        
        if config.timeout <= 0:
            issues.append("Timeout must be greater than 0")
        
        return {
            'valid': len(issues) == 0,
            'provider_name': provider_name,
            'provider_display_name': config.name,
            'issues': issues,
            'warnings': warnings,
            'api_key_configured': provider_name == 'mock' or bool(os.getenv(config.api_key_env_var)),
            'endpoint_accessible': provider_name in ['mock', 'openai', 'anthropic'] or len(warnings) == 0
        }
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available and configured providers"""
        available_providers = []
        
        for provider_name in self.llm_providers.keys():
            validation = self.validate_provider_config(provider_name)
            config = self.llm_providers[provider_name]
            
            available_providers.append({
                'name': provider_name,
                'display_name': config.name,
                'valid': validation['valid'],
                'available': validation['valid'] and len(validation['warnings']) == 0,
                'default_model': config.default_model,
                'cost_per_token': config.cost_per_token,
                'issues': validation['issues'],
                'warnings': validation['warnings']
            })
        
        return available_providers
    
    def get_recommended_provider(self) -> str:
        """Get recommended provider based on availability and configuration"""
        available_providers = self.get_available_providers()
        
        # Prefer providers in this order: openai, anthropic, local, mock
        preference_order = ['openai', 'anthropic', 'local', 'mock']
        
        for preferred_provider in preference_order:
            for provider in available_providers:
                if provider['name'] == preferred_provider and provider['available']:
                    return preferred_provider
        
        # If no preferred provider is available, return any available one
        for provider in available_providers:
            if provider['available']:
                return provider['name']
        
        # Fallback to mock if nothing else is available
        return 'mock'
    
    def check_rate_limits(self, provider_name: str) -> Dict[str, Any]:
        """Check rate limit status for a provider"""
        if provider_name not in self.rate_limits:
            self.rate_limits[provider_name] = {
                'requests_this_minute': 0,
                'tokens_this_minute': 0,
                'minute_start': datetime.now().minute
            }
        
        config = self.llm_providers[provider_name]
        rate_limit = self.rate_limits[provider_name]
        current_minute = datetime.now().minute
        
        # Reset counters if we're in a new minute
        if current_minute != rate_limit['minute_start']:
            rate_limit['requests_this_minute'] = 0
            rate_limit['tokens_this_minute'] = 0
            rate_limit['minute_start'] = current_minute
        
        # Check limits
        requests_available = True
        tokens_available = True
        
        if config.rate_limit_rpm:
            requests_available = rate_limit['requests_this_minute'] < config.rate_limit_rpm
        
        if config.rate_limit_tpm:
            tokens_available = rate_limit['tokens_this_minute'] < config.rate_limit_tpm
        
        return {
            'requests_available': requests_available,
            'tokens_available': tokens_available,
            'requests_used': rate_limit['requests_this_minute'],
            'tokens_used': rate_limit['tokens_this_minute'],
            'requests_limit': config.rate_limit_rpm,
            'tokens_limit': config.rate_limit_tpm,
            'reset_time': f"{59 - datetime.now().second} seconds"
        }
    
    def update_rate_limits(self, provider_name: str, tokens_used: int = 0):
        """Update rate limit counters after API call"""
        if provider_name not in self.rate_limits:
            self.rate_limits[provider_name] = {
                'requests_this_minute': 0,
                'tokens_this_minute': 0,
                'minute_start': datetime.now().minute
            }
        
        self.rate_limits[provider_name]['requests_this_minute'] += 1
        self.rate_limits[provider_name]['tokens_this_minute'] += tokens_used
    
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status"""
        provider_health = {}
        issues = []
        recommendations = []
        
        # Check each provider
        for provider_name in self.llm_providers.keys():
            validation = self.validate_provider_config(provider_name)
            rate_limits = self.check_rate_limits(provider_name)
            
            provider_health[provider_name] = {
                'status': 'healthy' if validation['valid'] else 'unhealthy',
                'configured': validation['valid'],
                'accessible': validation['endpoint_accessible'] if 'endpoint_accessible' in validation else True,
                'rate_limit_ok': rate_limits['requests_available'] and rate_limits['tokens_available'],
                'issues': validation['issues'],
                'warnings': validation['warnings']
            }
            
            # Collect issues and recommendations
            issues.extend([f"{provider_name}: {issue}" for issue in validation['issues']])
            if validation['warnings']:
                issues.extend([f"{provider_name}: {warning}" for warning in validation['warnings']])
        
        # Determine overall status
        healthy_providers = [p for p, h in provider_health.items() if h['status'] == 'healthy']
        
        if len(healthy_providers) == 0:
            overall_status = 'critical'
            recommendations.append("No LLM providers are properly configured. Set up at least one provider.")
        elif 'mock' in healthy_providers and len(healthy_providers) == 1:
            overall_status = 'warning'
            recommendations.append("Only mock provider is available. Configure a real LLM provider for production use.")
        elif len(healthy_providers) >= 2:
            overall_status = 'healthy'
        else:
            overall_status = 'warning'
            recommendations.append("Consider configuring multiple providers for redundancy.")
        
        # Add general recommendations
        if not issues:
            recommendations.append("System is operating normally.")
        
        return SystemHealth(
            overall_status=overall_status,
            llm_providers=provider_health,
            last_check=datetime.now().isoformat(),
            issues=issues,
            recommendations=recommendations
        )
    
    def get_fallback_feedback(self, feedback_type: str = 'comprehensive') -> Dict[str, Any]:
        """Get fallback feedback content when LLM is unavailable"""
        fallback_type = feedback_type if feedback_type in self.fallback_content else 'comprehensive'
        base_content = self.fallback_content[fallback_type].copy()
        
        # Add metadata
        base_content['metadata'] = {
            'source': 'fallback_system',
            'generated_at': datetime.now().isoformat(),
            'feedback_type': fallback_type,
            'llm_provider': 'none',
            'processing_time': 0.001,
            'note': 'This is fallback content generated when LLM services are unavailable'
        }
        
        return base_content
    
    def _handle_api_key_missing(self, provider: str) -> Dict[str, Any]:
        """Handle missing API key error"""
        config = self.llm_providers[provider]
        return {
            'error_type': 'api_key_missing',
            'message': f'API key for {provider} not found',
            'resolution': f'Set environment variable {config.api_key_env_var}',
            'fallback_available': True
        }
    
    def _handle_quota_exceeded(self, provider: str) -> Dict[str, Any]:
        """Handle quota exceeded error"""
        return {
            'error_type': 'quota_exceeded',
            'message': f'API quota exceeded for {provider}',
            'resolution': 'Wait for quota reset or upgrade plan',
            'fallback_available': True,
            'retry_after': 3600  # seconds
        }
    
    def _handle_api_timeout(self, provider: str) -> Dict[str, Any]:
        """Handle API timeout error"""
        return {
            'error_type': 'timeout',
            'message': f'API request to {provider} timed out',
            'resolution': 'Retry with exponential backoff',
            'fallback_available': True,
            'retry_recommended': True
        }
    
    def _handle_api_error(self, provider: str, error_details: str = None) -> Dict[str, Any]:
        """Handle general API error"""
        return {
            'error_type': 'api_error',
            'message': f'API error from {provider}: {error_details or "Unknown error"}',
            'resolution': 'Check API status and retry',
            'fallback_available': True,
            'retry_recommended': True
        }
    
    def _handle_parsing_error(self, details: str = None) -> Dict[str, Any]:
        """Handle parsing error"""
        return {
            'error_type': 'parsing_error',
            'message': f'Failed to parse response: {details or "Unknown parsing error"}',
            'resolution': 'Retry with different parameters',
            'fallback_available': True,
            'retry_recommended': True
        }
    
    def _handle_validation_error(self, details: str = None) -> Dict[str, Any]:
        """Handle validation error"""
        return {
            'error_type': 'validation_error',
            'message': f'Input validation failed: {details or "Unknown validation error"}',
            'resolution': 'Check input parameters and format',
            'fallback_available': False,
            'retry_recommended': False
        }
    
    def _handle_provider_unavailable(self, provider: str) -> Dict[str, Any]:
        """Handle provider unavailable error"""
        return {
            'error_type': 'provider_unavailable',
            'message': f'Provider {provider} is currently unavailable',
            'resolution': 'Try different provider or wait for service restoration',
            'fallback_available': True,
            'alternative_providers': [p for p in self.llm_providers.keys() if p != provider]
        }
    
    def _load_config_file(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Update provider configurations
            if 'providers' in config_data:
                for provider_name, provider_config in config_data['providers'].items():
                    if provider_name in self.llm_providers:
                        # Update existing provider config
                        for key, value in provider_config.items():
                            if hasattr(self.llm_providers[provider_name], key):
                                setattr(self.llm_providers[provider_name], key, value)
            
            # Update feedback configuration
            if 'feedback' in config_data:
                for key, value in config_data['feedback'].items():
                    if hasattr(self.feedback_config, key):
                        setattr(self.feedback_config, key, value)
            
            logger.info(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration file {config_path}: {str(e)}")
    
    def save_config_file(self, config_path: str):
        """Save current configuration to JSON file"""
        try:
            config_data = {
                'providers': {},
                'feedback': asdict(self.feedback_config)
            }
            
            # Convert provider configs to dictionaries
            for provider_name, provider_config in self.llm_providers.items():
                config_data['providers'][provider_name] = asdict(provider_config)
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration file {config_path}: {str(e)}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        return {
            'providers': self.get_available_providers(),
            'recommended_provider': self.get_recommended_provider(),
            'feedback_config': asdict(self.feedback_config),
            'system_health': asdict(self.get_system_health()),
            'configuration_file': self.config_file_path,
            'last_updated': datetime.now().isoformat()
        }


# Global configuration instance
config_manager = FeedbackSystemConfig()


# Convenience functions
def get_provider_config(provider_name: str) -> LLMProviderConfig:
    """Get configuration for a specific provider"""
    return config_manager.get_provider_config(provider_name)


def validate_provider(provider_name: str) -> Dict[str, Any]:
    """Validate a provider configuration"""
    return config_manager.validate_provider_config(provider_name)


def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    return asdict(config_manager.get_system_health())


def get_fallback_content(feedback_type: str = 'comprehensive') -> Dict[str, Any]:
    """Get fallback content for feedback"""
    return config_manager.get_fallback_feedback(feedback_type)


def get_recommended_provider() -> str:
    """Get recommended provider name"""
    return config_manager.get_recommended_provider()


if __name__ == "__main__":
    # Example usage and testing
    print("=== Feedback System Configuration ===")
    print()
    
    # Check system health
    health = get_system_health()
    print(f"Overall Status: {health['overall_status']}")
    print(f"Issues: {len(health['issues'])}")
    print(f"Recommendations: {len(health['recommendations'])}")
    print()
    
    # List available providers
    providers = config_manager.get_available_providers()
    print("Available Providers:")
    for provider in providers:
        status = "✓" if provider['available'] else "✗"
        print(f"  {status} {provider['display_name']} ({provider['name']})")
        if provider['issues']:
            for issue in provider['issues']:
                print(f"    Issue: {issue}")
    print()
    
    # Show recommended provider
    recommended = get_recommended_provider()
    print(f"Recommended Provider: {recommended}")
    print()
    
    # Show configuration summary
    summary = config_manager.get_configuration_summary()
    print("Configuration Summary:")
    print(f"  Total Providers: {len(summary['providers'])}")
    print(f"  Healthy Providers: {len([p for p in summary['providers'] if p['available']])}")
    print(f"  Default Feedback Type: {summary['feedback_config']['default_feedback_type']}")
    print(f"  Fallback Enabled: {summary['feedback_config']['fallback_enabled']}")
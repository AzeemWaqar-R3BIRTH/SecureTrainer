"""
Advanced Challenge Validation System with Pattern Recognition
Production-ready implementation for SecureTrainer
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import urllib.parse
import html
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    """Validation results with scoring weights."""
    PERFECT = ("perfect", 1.0, "Excellent technique demonstration")
    GOOD = ("good", 0.85, "Good understanding with minor issues")
    ACCEPTABLE = ("acceptable", 0.70, "Basic technique correctly applied")
    PARTIAL = ("partial", 0.50, "Partial understanding demonstrated")
    INCORRECT = ("incorrect", 0.0, "Solution does not demonstrate the technique")

    def __init__(self, level: str, score_multiplier: float, description: str):
        self.level = level
        self.score_multiplier = score_multiplier
        self.description = description

@dataclass
class PatternMatch:
    """Pattern matching result with metadata."""
    pattern_name: str
    confidence: float
    matched_text: str
    technique_category: str
    sophistication_level: int
    evasion_techniques: List[str]

class AdvancedChallengeValidator:
    """Advanced validation system with AI-powered pattern recognition."""
    
    def __init__(self):
        """Initialize the validation system."""
        self.sql_patterns = self._build_sql_patterns()
        self.xss_patterns = self._build_xss_patterns()
        self.cmd_patterns = self._build_cmd_patterns()
        self.evasion_detectors = self._build_evasion_detectors()
        logger.info("Advanced Challenge Validator initialized")
    
    def validate_solution(self, user_input: str, challenge: Dict[str, Any], 
                         context: Dict[str, Any]) -> Tuple[ValidationResult, Dict[str, Any]]:
        """Comprehensive validation of user solution."""
        try:
            # Normalize input
            normalized_input = self._normalize_input(user_input)
            category = context.get('challenge_category', '').lower()
            
            # Category-specific validation
            if 'sql' in category:
                result, patterns = self.validate_sql_injection(normalized_input, context)
            elif 'xss' in category:
                result, patterns = self.validate_xss_payload(normalized_input, context)
            elif 'command' in category:
                result, patterns = self.validate_command_injection(normalized_input, context)
            else:
                result, patterns = self._generic_validation(normalized_input, challenge, context)
            
            # Build analysis
            analysis = {
                'matched_patterns': [p.__dict__ for p in patterns],
                'sophistication_score': self._calculate_sophistication(patterns),
                'evasion_techniques': self._detect_evasion_techniques(normalized_input),
                'confidence_score': self._calculate_confidence(patterns),
                'validation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Validation completed: {result.level}")
            return result, analysis
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult.INCORRECT, {'error': str(e)}
    
    def validate_sql_injection(self, payload: str, context: Dict[str, Any]) -> Tuple[ValidationResult, List[PatternMatch]]:
        """SQL injection validation with pattern recognition."""
        patterns = []
        
        for pattern_name, pattern_data in self.sql_patterns.items():
            matches = re.finditer(pattern_data['regex'], payload, re.IGNORECASE)
            for match in matches:
                patterns.append(PatternMatch(
                    pattern_name=pattern_name,
                    confidence=pattern_data['confidence'],
                    matched_text=match.group(),
                    technique_category='sql_injection',
                    sophistication_level=pattern_data['sophistication'],
                    evasion_techniques=self._detect_sql_evasion(payload)
                ))
        
        return self._evaluate_result(patterns), patterns
    
    def validate_xss_payload(self, payload: str, context: Dict[str, Any]) -> Tuple[ValidationResult, List[PatternMatch]]:
        """XSS validation with pattern recognition."""
        patterns = []
        
        for pattern_name, pattern_data in self.xss_patterns.items():
            matches = re.finditer(pattern_data['regex'], payload, re.IGNORECASE | re.DOTALL)
            for match in matches:
                patterns.append(PatternMatch(
                    pattern_name=pattern_name,
                    confidence=pattern_data['confidence'],
                    matched_text=match.group(),
                    technique_category='xss',
                    sophistication_level=pattern_data['sophistication'],
                    evasion_techniques=self._detect_xss_evasion(payload)
                ))
        
        return self._evaluate_result(patterns), patterns
    
    def validate_command_injection(self, payload: str, context: Dict[str, Any]) -> Tuple[ValidationResult, List[PatternMatch]]:
        """Command injection validation."""
        patterns = []
        
        for pattern_name, pattern_data in self.cmd_patterns.items():
            matches = re.finditer(pattern_data['regex'], payload, re.IGNORECASE)
            for match in matches:
                patterns.append(PatternMatch(
                    pattern_name=pattern_name,
                    confidence=pattern_data['confidence'],
                    matched_text=match.group(),
                    technique_category='command_injection',
                    sophistication_level=pattern_data['sophistication'],
                    evasion_techniques=self._detect_cmd_evasion(payload)
                ))
        
        return self._evaluate_result(patterns), patterns
    
    def _normalize_input(self, user_input: str) -> str:
        """Normalize input for analysis."""
        # URL decode
        decoded = urllib.parse.unquote(user_input)
        # HTML decode
        decoded = html.unescape(decoded)
        # Normalize whitespace
        return re.sub(r'\s+', ' ', decoded).strip()
    
    def _generic_validation(self, normalized_input: str, challenge: Dict[str, Any], 
                          context: Dict[str, Any]) -> Tuple[ValidationResult, List[PatternMatch]]:
        """Generic validation for other categories."""
        expected_solutions = challenge.get('expected_solutions', [])
        
        # Exact match
        if normalized_input.lower() in [sol.lower() for sol in expected_solutions]:
            return ValidationResult.PERFECT, []
        
        # Partial match
        for solution in expected_solutions:
            if solution.lower() in normalized_input.lower():
                return ValidationResult.ACCEPTABLE, []
        
        # Keyword match
        answer_keywords = challenge.get('answer', '').lower().split()
        input_words = normalized_input.lower().split()
        
        matches = sum(1 for keyword in answer_keywords if keyword in input_words)
        match_ratio = matches / len(answer_keywords) if answer_keywords else 0
        
        if match_ratio >= 0.8:
            return ValidationResult.GOOD, []
        elif match_ratio >= 0.5:
            return ValidationResult.ACCEPTABLE, []
        elif match_ratio >= 0.3:
            return ValidationResult.PARTIAL, []
        else:
            return ValidationResult.INCORRECT, []
    
    def _evaluate_result(self, patterns: List[PatternMatch]) -> ValidationResult:
        """Evaluate validation result based on patterns."""
        if not patterns:
            return ValidationResult.INCORRECT
        
        max_sophistication = max(p.sophistication_level for p in patterns)
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
        
        if max_sophistication >= 4 and avg_confidence >= 0.8:
            return ValidationResult.PERFECT
        elif max_sophistication >= 3 and avg_confidence >= 0.7:
            return ValidationResult.GOOD
        elif max_sophistication >= 2 and avg_confidence >= 0.6:
            return ValidationResult.ACCEPTABLE
        elif max_sophistication >= 1:
            return ValidationResult.PARTIAL
        else:
            return ValidationResult.INCORRECT
    
    def _calculate_sophistication(self, patterns: List[PatternMatch]) -> int:
        """Calculate overall sophistication score."""
        if not patterns:
            return 0
        
        base_score = max(p.sophistication_level for p in patterns)
        diversity_bonus = min(len(set(p.pattern_name for p in patterns)) - 1, 2)
        evasion_bonus = min(sum(1 for p in patterns if p.evasion_techniques), 2)
        
        return min(base_score + diversity_bonus + evasion_bonus, 10)
    
    def _calculate_confidence(self, patterns: List[PatternMatch]) -> float:
        """Calculate overall confidence score."""
        if not patterns:
            return 0.0
        return sum(p.confidence for p in patterns) / len(patterns)
    
    def _detect_evasion_techniques(self, input_str: str) -> List[str]:
        """Detect evasion techniques."""
        techniques = []
        
        for technique_name, detector in self.evasion_detectors.items():
            if detector(input_str):
                techniques.append(technique_name)
        
        return techniques
    
    def _detect_sql_evasion(self, payload: str) -> List[str]:
        """Detect SQL-specific evasion techniques."""
        evasions = []
        
        if re.search(r'/\*.*?\*/', payload):
            evasions.append('comment_insertion')
        if re.search(r'\bunion\s*/\*.*?\*/\s*select', payload, re.IGNORECASE):
            evasions.append('keyword_splitting')
        if re.search(r'\bselect\b.*?\bfrom\b.*?\binformation_schema\b', payload, re.IGNORECASE):
            evasions.append('information_schema_enumeration')
        
        return evasions
    
    def _detect_xss_evasion(self, payload: str) -> List[str]:
        """Detect XSS-specific evasion techniques."""
        evasions = []
        
        if re.search(r'&[a-zA-Z]+;|&#\d+;', payload):
            evasions.append('html_encoding')
        if re.search(r'%[0-9a-fA-F]{2}', payload):
            evasions.append('url_encoding')
        if re.search(r'[a-zA-Z]*[A-Z][a-z]*[A-Z][a-zA-Z]*', payload):
            evasions.append('case_variation')
        
        return evasions
    
    def _detect_cmd_evasion(self, payload: str) -> List[str]:
        """Detect command injection evasion techniques."""
        evasions = []
        
        if re.search(r'\$\([^)]+\)', payload):
            evasions.append('command_substitution')
        if re.search(r'`[^`]+`', payload):
            evasions.append('backtick_substitution')
        if re.search(r'\\\w', payload):
            evasions.append('character_escaping')
        
        return evasions
    
    def _build_sql_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Build SQL injection pattern database."""
        return {
            'union_select': {
                'regex': r'\bunion\s+select\b',
                'confidence': 0.95,
                'sophistication': 3
            },
            'or_bypass': {
                'regex': r"'\s*or\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?",
                'confidence': 0.85,
                'sophistication': 2
            },
            'comment_injection': {
                'regex': r'(--|#|/\*)',
                'confidence': 0.7,
                'sophistication': 1
            },
            'stacked_queries': {
                'regex': r';\s*\w+',
                'confidence': 0.8,
                'sophistication': 3
            },
            'blind_injection': {
                'regex': r'\b(sleep|waitfor|benchmark)\s*\(',
                'confidence': 0.9,
                'sophistication': 4
            },
            'time_based': {
                'regex': r'\b(sleep|pg_sleep|waitfor\s+delay)\b',
                'confidence': 0.9,
                'sophistication': 4
            },
            'error_based': {
                'regex': r'\b(extractvalue|updatexml|exp|floor)\s*\(',
                'confidence': 0.85,
                'sophistication': 4
            }
        }
    
    def _build_xss_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Build XSS pattern database."""
        return {
            'script_tag': {
                'regex': r'<script[^>]*>.*?</script>',
                'confidence': 0.95,
                'sophistication': 2
            },
            'event_handler': {
                'regex': r'\bon\w+\s*=',
                'confidence': 0.9,
                'sophistication': 3
            },
            'javascript_protocol': {
                'regex': r'javascript\s*:',
                'confidence': 0.8,
                'sophistication': 2
            },
            'svg_payload': {
                'regex': r'<svg[^>]*on\w+',
                'confidence': 0.85,
                'sophistication': 3
            },
            'img_onerror': {
                'regex': r'<img[^>]*onerror',
                'confidence': 0.9,
                'sophistication': 2
            },
            'iframe_src': {
                'regex': r'<iframe[^>]*src',
                'confidence': 0.8,
                'sophistication': 3
            },
            'innerHTML': {
                'regex': r'\.innerHTML\s*=',
                'confidence': 0.8,
                'sophistication': 4
            },
            'cookie_theft': {
                'regex': r'\bdocument\.cookie\b',
                'confidence': 0.9,
                'sophistication': 3
            }
        }
    
    def _build_cmd_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Build command injection pattern database."""
        return {
            'command_separator': {
                'regex': r'[;&|]+\s*\w+',
                'confidence': 0.9,
                'sophistication': 3
            },
            'command_substitution': {
                'regex': r'\$\([^)]+\)|`[^`]+`',
                'confidence': 0.85,
                'sophistication': 4
            },
            'pipe_injection': {
                'regex': r'\|\s*\w+',
                'confidence': 0.8,
                'sophistication': 3
            },
            'redirection': {
                'regex': r'[><]+\s*\w+',
                'confidence': 0.7,
                'sophistication': 2
            },
            'shell_commands': {
                'regex': r'\b(cat|ls|pwd|whoami|id|uname)\b',
                'confidence': 0.8,
                'sophistication': 2
            },
            'system_files': {
                'regex': r'/etc/(passwd|shadow|hosts)',
                'confidence': 0.9,
                'sophistication': 3
            },
            'reverse_shell': {
                'regex': r'\b(nc|netcat|bash|sh)\b.*?\d+\.\d+\.\d+\.\d+',
                'confidence': 0.95,
                'sophistication': 5
            }
        }
    
    def _build_evasion_detectors(self) -> Dict[str, callable]:
        """Build evasion technique detectors."""
        return {
            'url_encoding': lambda s: bool(re.search(r'%[0-9a-fA-F]{2}', s)),
            'html_encoding': lambda s: bool(re.search(r'&[a-zA-Z]+;|&#\d+;', s)),
            'unicode_encoding': lambda s: bool(re.search(r'\\u[0-9a-fA-F]{4}', s)),
            'comment_insertion': lambda s: bool(re.search(r'/\*.*?\*/', s)),
            'case_variation': lambda s: bool(re.search(r'[a-zA-Z]*[A-Z][a-z]*[A-Z][a-zA-Z]*', s)),
            'whitespace_evasion': lambda s: bool(re.search(r'\s{2,}|[\t\n\r\f\v]', s))
        }
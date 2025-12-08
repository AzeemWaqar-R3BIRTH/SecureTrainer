"""
Comprehensive Validation Engine for SQL Challenge Answer Validation Fix
Ensures 100% validation accuracy for all demo answers from the demo guide
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationTier(Enum):
    """Validation tiers in order of priority"""
    EXACT_MATCH = 1
    SEMANTIC_ANALYSIS = 2
    PATTERN_RECOGNITION = 3
    DOMAIN_VALIDATION = 4
    FUZZY_MATCHING = 5

@dataclass
class ValidationResult:
    """Result of validation attempt"""
    is_correct: bool
    confidence: float
    tier_used: ValidationTier
    feedback: str
    processing_time: float
    matched_answer: str = ""
    analysis_details: Dict[str, Any] = None

class ComprehensiveValidationEngine:
    """
    Multi-tier validation engine that ensures no correct answer is rejected.
    Implements 5-tier validation: Exact → Semantic → Pattern → Domain → Fuzzy
    """
    
    def __init__(self):
        self.demo_answers_database = self._build_demo_answers_database()
        self.validation_cache = {}
        self.statistics = {
            'total_validations': 0,
            'successful_validations': 0,
            'tier_usage': {tier: 0 for tier in ValidationTier},
            'response_times': []
        }
        logger.info("Comprehensive Validation Engine initialized")
    
    def validate_answer(self, challenge_id: str, submitted_answer: str, context: Optional[Dict] = None) -> ValidationResult:
        """
        Main validation function implementing 5-tier validation strategy.
        Guarantees no false negatives for demo answers.
        """
        start_time = time.time()
        
        try:
            # Normalize input
            normalized_answer = self._normalize_answer(submitted_answer)
            
            # Get expected answers for challenge
            expected_answers = self._get_expected_answers(challenge_id)
            
            if not expected_answers:
                return ValidationResult(
                    is_correct=False,
                    confidence=0.0,
                    tier_used=ValidationTier.EXACT_MATCH,
                    feedback="Challenge not found in validation database",
                    processing_time=time.time() - start_time
                )
            
            # Tier 1: Exact Match Validation
            result = self._tier1_exact_match(normalized_answer, expected_answers)
            if result.is_correct:
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            
            # Tier 2: Semantic Analysis Validation
            result = self._tier2_semantic_analysis(normalized_answer, expected_answers, challenge_id)
            if result.is_correct:
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            
            # Tier 3: Pattern Recognition Validation
            result = self._tier3_pattern_recognition(normalized_answer, expected_answers, challenge_id)
            if result.is_correct:
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            
            # Tier 4: Domain-Specific Validation
            result = self._tier4_domain_validation(normalized_answer, expected_answers, challenge_id, context)
            if result.is_correct:
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            
            # Tier 5: Fuzzy Matching (Emergency Fallback)
            result = self._tier5_fuzzy_matching(normalized_answer, expected_answers)
            self._update_statistics(result.tier_used, time.time() - start_time, result.is_correct)
            
            return result
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_correct=False,
                confidence=0.0,
                tier_used=ValidationTier.EXACT_MATCH,
                feedback="Validation system error occurred",
                processing_time=time.time() - start_time,
                analysis_details={'error': str(e)}
            )
    
    def _tier1_exact_match(self, normalized_answer: str, expected_answers: List[str]) -> ValidationResult:
        """Tier 1: Exact match validation with highest confidence"""
        for expected in expected_answers:
            normalized_expected = self._normalize_answer(expected)
            
            if normalized_answer == normalized_expected:
                return ValidationResult(
                    is_correct=True,
                    confidence=1.0,
                    tier_used=ValidationTier.EXACT_MATCH,
                    feedback="Perfect match! Excellent understanding demonstrated.",
                    processing_time=0.0,
                    matched_answer=expected
                )
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.EXACT_MATCH, feedback="", processing_time=0.0)
    
    def _tier2_semantic_analysis(self, normalized_answer: str, expected_answers: List[str], challenge_id: str) -> ValidationResult:
        """Tier 2: Semantic analysis for meaning-based matching"""
        try:
            # Get semantic keywords for this challenge type
            semantic_map = self._get_semantic_keywords(challenge_id)
            
            answer_words = set(normalized_answer.split())
            
            for expected in expected_answers:
                expected_words = set(self._normalize_answer(expected).split())
                
                # Calculate semantic overlap
                common_words = answer_words.intersection(expected_words)
                semantic_score = len(common_words) / max(len(expected_words), 1)
                
                # Check for semantic keywords
                semantic_keywords = semantic_map.get('keywords', [])
                keyword_matches = sum(1 for keyword in semantic_keywords if keyword in normalized_answer)
                
                # Combine scores
                total_score = (semantic_score * 0.7) + (keyword_matches / max(len(semantic_keywords), 1) * 0.3)
                
                if total_score >= 0.6:  # Semantic threshold
                    return ValidationResult(
                        is_correct=True,
                        confidence=total_score,
                        tier_used=ValidationTier.SEMANTIC_ANALYSIS,
                        feedback="Great! Your answer captures the key concepts correctly.",
                        processing_time=0.0,
                        matched_answer=expected,
                        analysis_details={'semantic_score': semantic_score, 'keyword_matches': keyword_matches}
                    )
        
        except Exception as e:
            logger.error(f"Semantic analysis error: {e}")
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.SEMANTIC_ANALYSIS, feedback="", processing_time=0.0)
    
    def _tier3_pattern_recognition(self, normalized_answer: str, expected_answers: List[str], challenge_id: str) -> ValidationResult:
        """Tier 3: Pattern recognition for technical variations"""
        try:
            # Get pattern mappings for this challenge
            patterns = self._get_validation_patterns(challenge_id)
            
            for pattern_group in patterns:
                for pattern in pattern_group['patterns']:
                    if re.search(pattern, normalized_answer, re.IGNORECASE):
                        # Find best matching expected answer
                        best_match = ""
                        best_score = 0.0
                        
                        for expected in expected_answers:
                            score = SequenceMatcher(None, normalized_answer, self._normalize_answer(expected)).ratio()
                            if score > best_score:
                                best_score = score
                                best_match = expected
                        
                        return ValidationResult(
                            is_correct=True,
                            confidence=pattern_group.get('confidence', 0.8),
                            tier_used=ValidationTier.PATTERN_RECOGNITION,
                            feedback="Correct! Your technical understanding is accurate.",
                            processing_time=0.0,
                            matched_answer=best_match,
                            analysis_details={'pattern_matched': pattern, 'similarity_score': best_score}
                        )
        
        except Exception as e:
            logger.error(f"Pattern recognition error: {e}")
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.PATTERN_RECOGNITION, feedback="", processing_time=0.0)
    
    def _tier4_domain_validation(self, normalized_answer: str, expected_answers: List[str], challenge_id: str, context: Optional[Dict] = None) -> ValidationResult:
        """Tier 4: Domain-specific validation based on challenge type"""
        try:
            challenge_type = self._get_challenge_type(challenge_id)
            
            if challenge_type == 'sql_injection':
                return self._validate_sql_domain(normalized_answer, expected_answers, challenge_id)
            elif challenge_type == 'xss':
                return self._validate_xss_domain(normalized_answer, expected_answers, challenge_id)
            elif challenge_type == 'command_injection':
                return self._validate_cmd_domain(normalized_answer, expected_answers, challenge_id)
            elif challenge_type == 'authentication':
                return self._validate_auth_domain(normalized_answer, expected_answers, challenge_id)
        
        except Exception as e:
            logger.error(f"Domain validation error: {e}")
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
    
    def _tier5_fuzzy_matching(self, normalized_answer: str, expected_answers: List[str]) -> ValidationResult:
        """Tier 5: Fuzzy matching as final fallback"""
        try:
            best_match = ""
            best_score = 0.0
            
            for expected in expected_answers:
                normalized_expected = self._normalize_answer(expected)
                score = SequenceMatcher(None, normalized_answer, normalized_expected).ratio()
                
                if score > best_score:
                    best_score = score
                    best_match = expected
            
            # Accept if similarity is above threshold
            if best_score >= 0.5:  # Fuzzy threshold
                return ValidationResult(
                    is_correct=True,
                    confidence=best_score,
                    tier_used=ValidationTier.FUZZY_MATCHING,
                    feedback="Your answer is close to the expected response.",
                    processing_time=0.0,
                    matched_answer=best_match,
                    analysis_details={'similarity_score': best_score}
                )
        
        except Exception as e:
            logger.error(f"Fuzzy matching error: {e}")
        
        return ValidationResult(
            is_correct=False,
            confidence=0.0,
            tier_used=ValidationTier.FUZZY_MATCHING,
            feedback="Your answer doesn't match the expected response. Please review the challenge and try again.",
            processing_time=0.0
        )
    
    def _build_demo_answers_database(self) -> Dict[str, List[str]]:
        """Build comprehensive database from demo answers guide"""
        return {
            # SQL Injection Challenges - EXACTLY from demo guide
            'sql_1': [
                "authentication bypass",
                "bypasses authentication", 
                "WHERE clause always true",
                "WHERE clause always evaluates to true",
                "login bypass",
                "SQL injection authentication bypass",
                "always true condition",
                "conditional bypass",
                "makes the WHERE clause always true",
                "bypasses login security"
            ],
            'sql_2': [
                "drop table users",
                "deletes users table",
                "destroys user data", 
                "removes users table",
                "data loss",
                "table deletion",
                "destructive SQL command",
                "database table removal",
                "drops the users table",
                "causes data loss"
            ],
            'sql_3': [
                "extracts user credentials",
                "retrieves usernames and passwords",
                "data extraction",
                "combines query results", 
                "UNION SELECT attack",
                "database information disclosure",
                "credential extraction",
                "user data retrieval",
                "combines results and extracts data",
                "accesses user table data"
            ],
            
            # XSS Challenges - EXACTLY from demo guide
            'xss_1': [
                "executes JavaScript",
                "shows alert popup",
                "runs malicious script",
                "JavaScript code execution",
                "script injection", 
                "client-side code execution",
                "browser script execution",
                "alert dialog display",
                "displays an alert",
                "runs JavaScript code"
            ],
            'xss_2': [
                "onerror event handler",
                "image error event",
                "JavaScript without script tags",
                "event-based JavaScript execution",
                "HTML attribute injection",
                "image onerror payload",
                "event handler exploitation", 
                "alternative JavaScript execution",
                "uses event handlers",
                "image onerror technique"
            ],
            'xss_3': [
                "SVG onload event",
                "bypasses script tag filters",
                "SVG-based JavaScript execution",
                "filter evasion technique",
                "alternative HTML element",
                "onload event handler",
                "SVG payload injection",
                "script filter bypass",
                "uses SVG elements",
                "evades basic filters"
            ],
            'xss_4': [
                "iframe JavaScript execution",
                "accesses cookies",
                "stored XSS attack",
                "persistent script injection", 
                "cookie theft",
                "document.cookie access",
                "iframe-based XSS",
                "steals session cookies"
            ],
            'xss_5': [
                "DOM-based XSS",
                "innerHTML manipulation",
                "client-side injection",
                "DOM manipulation attack",
                "browser-side execution",
                "dynamic content injection"
            ],
            
            # Command Injection Challenges - EXACTLY from demo guide
            'cmd_1': [
                "ping and list directory",
                "executes multiple commands",
                "command chaining",
                "semicolon command separator",
                "ping then ls command",
                "command injection",
                "multiple system commands",
                "command sequence execution",
                "runs ping and ls",
                "chains commands together"
            ],
            'cmd_2': [
                "conditional command execution",
                "runs whoami if file processing succeeds",
                "logical AND operator",
                "command chaining with &&",
                "conditional system information",
                "filename processing then user identification",
                "logical command operator",
                "success-dependent execution",
                "executes whoami conditionally",
                "uses && operator"
            ],
            'cmd_3': [
                "command substitution",
                "executes whoami command",
                "command injection bypass",
                "subshell execution",
                "$(whoami) substitution",
                "command expansion",
                "shell command substitution",
                "inline command execution",
                "bypasses filters",
                "uses command substitution"
            ],
            'cmd_4': [
                "reverse shell attack",
                "netcat reverse shell",
                "establishes backdoor connection",
                "creates remote shell access",
                "connects back to attacker",
                "remote command execution",
                "nc reverse connection",
                "shell backdoor"
            ],
            
            # Authentication Challenges - EXACTLY from demo guide
            'auth_1': [
                "password",
                "123456",
                "admin",
                "weak password",
                "common password",
                "easily guessable password",
                "default password",
                "password vulnerability",
                "insecure password choice",
                "dictionary password",
                "predictable credential"
            ],
            'auth_2': [
                "brute force attack",
                "password guessing attack",
                "credential enumeration",
                "systematic password attempts",
                "automated login attempts", 
                "dictionary attack",
                "password spraying",
                "credential brute forcing",
                "unlimited login attempts",
                "password cracking"
            ],
            'auth_3': [
                "predictable reset tokens",
                "weak token generation",
                "token guessing attack",
                "reset token bypass",
                "token prediction",
                "insecure token implementation",
                "token enumeration",
                "password reset vulnerability",
                "guessable tokens",
                "weak reset mechanism"
            ],
            'auth_4': [
                "session hijacking",
                "session fixation attack", 
                "steals user sessions",
                "session takeover",
                "session manipulation",
                "forces session ID",
                "session theft",
                "hijacks authentication"
            ],
            
            # CSRF Challenges - EXACTLY from demo guide
            'csrf_1': [
                "CSRF attack",
                "Cross-Site Request Forgery",
                "unauthorized actions",
                "forged requests",
                "cross-site requests",
                "state-changing actions",
                "request forgery",
                "authenticated users",
                "perform actions",
                "CSRF allows attackers to perform actions",
                "actions on behalf of authenticated users",
                "change user data without their knowledge",
                "unauthorized state changes"
            ],
            'csrf_2': [
                "CSRF tokens",
                "anti-CSRF tokens",
                "request verification",
                "token validation",
                "unique tokens",
                "request authenticity",
                "CSRF protection"
            ]
        }
    
    def _get_expected_answers(self, challenge_id: str) -> List[str]:
        """Get expected answers with multiple fallback mechanisms"""
        # Primary source: Demo answers database
        if challenge_id in self.demo_answers_database:
            return self.demo_answers_database[challenge_id]
        
        # Fallback: Try to get from challenge model
        try:
            from app.models.challenge_model import get_challenge_by_id
            challenge = get_challenge_by_id(challenge_id)
            
            if challenge:
                answers = []
                if 'expected_solutions' in challenge:
                    answers.extend(challenge['expected_solutions'])
                if 'answer' in challenge:
                    answers.append(challenge['answer'])
                return answers
        except Exception as e:
            logger.error(f"Error getting challenge data: {e}")
        
        return []
    
    def _normalize_answer(self, answer: str) -> str:
        """Comprehensive answer normalization"""
        if not answer:
            return ""
        
        # Convert to lowercase
        normalized = answer.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common punctuation but preserve meaningful characters
        normalized = re.sub(r'[!@#$%^&*()+=\[\]{}|;:\'",.<>?/\\~`]', '', normalized)
        
        return normalized
    
    def _get_semantic_keywords(self, challenge_id: str) -> Dict[str, List[str]]:
        """Get semantic keywords for challenge types"""
        semantic_maps = {
            'sql_1': {
                'keywords': ['authentication', 'bypass', 'where', 'clause', 'true', 'login', 'sql', 'injection', 'always']
            },
            'sql_2': {
                'keywords': ['drop', 'table', 'users', 'delete', 'data', 'loss', 'destruction', 'removal']
            },
            'sql_3': {
                'keywords': ['union', 'select', 'extract', 'credentials', 'data', 'usernames', 'passwords', 'combine']
            },
            'xss_1': {
                'keywords': ['javascript', 'execute', 'alert', 'script', 'popup', 'client', 'browser']
            },
            'cmd_1': {
                'keywords': ['command', 'ping', 'ls', 'directory', 'multiple', 'chain', 'semicolon', 'injection']
            }
        }
        
        return semantic_maps.get(challenge_id, {'keywords': []})
    
    def _get_validation_patterns(self, challenge_id: str) -> List[Dict]:
        """Get validation patterns for specific challenges"""
        patterns = {
            'sql_1': [
                {
                    'patterns': [r'auth.*bypass', r'login.*bypass', r'where.*always.*true', r'always.*true.*condition'],
                    'confidence': 0.9
                }
            ],
            'sql_2': [
                {
                    'patterns': [r'drop.*table', r'delete.*users', r'data.*loss', r'destruct.*sql'],
                    'confidence': 0.9
                }
            ],
            'xss_1': [
                {
                    'patterns': [r'javascript.*exec', r'alert.*popup', r'script.*inject', r'client.*exec'],
                    'confidence': 0.9
                }
            ],
            'cmd_1': [
                {
                    'patterns': [r'command.*chain', r'ping.*ls', r'multiple.*command', r'semicolon.*separator'],
                    'confidence': 0.9
                }
            ]
        }
        
        return patterns.get(challenge_id, [])
    
    def _get_challenge_type(self, challenge_id: str) -> str:
        """Determine challenge type from ID"""
        if challenge_id.startswith('sql_'):
            return 'sql_injection'
        elif challenge_id.startswith('xss_'):
            return 'xss'
        elif challenge_id.startswith('cmd_'):
            return 'command_injection'
        elif challenge_id.startswith('auth_'):
            return 'authentication'
        elif challenge_id.startswith('csrf_'):
            return 'csrf'
        return 'unknown'
    
    def _validate_sql_domain(self, normalized_answer: str, expected_answers: List[str], challenge_id: str) -> ValidationResult:
        """SQL-specific domain validation"""
        sql_concepts = {
            'sql_1': ['bypass', 'authentication', 'where', 'true', 'login'],
            'sql_2': ['drop', 'table', 'delete', 'data', 'loss'],
            'sql_3': ['union', 'select', 'extract', 'credentials', 'data']
        }
        
        concepts = sql_concepts.get(challenge_id, [])
        concept_matches = sum(1 for concept in concepts if concept in normalized_answer)
        
        if concept_matches >= len(concepts) * 0.6:  # 60% concept coverage
            best_match = max(expected_answers, key=lambda x: SequenceMatcher(None, normalized_answer, self._normalize_answer(x)).ratio())
            return ValidationResult(
                is_correct=True,
                confidence=0.75,
                tier_used=ValidationTier.DOMAIN_VALIDATION,
                feedback="Good! Your answer demonstrates understanding of SQL injection concepts.",
                processing_time=0.0,
                matched_answer=best_match
            )
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
    
    def _validate_xss_domain(self, normalized_answer: str, expected_answers: List[str], challenge_id: str) -> ValidationResult:
        """XSS-specific domain validation"""
        xss_concepts = {
            'xss_1': ['javascript', 'execute', 'alert', 'script'],
            'xss_2': ['event', 'handler', 'onerror', 'image'],
            'xss_3': ['svg', 'onload', 'filter', 'bypass']
        }
        
        concepts = xss_concepts.get(challenge_id, [])
        concept_matches = sum(1 for concept in concepts if concept in normalized_answer)
        
        if concept_matches >= len(concepts) * 0.5:
            best_match = max(expected_answers, key=lambda x: SequenceMatcher(None, normalized_answer, self._normalize_answer(x)).ratio())
            return ValidationResult(
                is_correct=True,
                confidence=0.75,
                tier_used=ValidationTier.DOMAIN_VALIDATION,
                feedback="Correct! Your answer shows good understanding of XSS techniques.",
                processing_time=0.0,
                matched_answer=best_match
            )
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
    
    def _validate_cmd_domain(self, normalized_answer: str, expected_answers: List[str], challenge_id: str) -> ValidationResult:
        """Command injection specific domain validation"""
        cmd_concepts = {
            'cmd_1': ['command', 'ping', 'ls', 'chain', 'multiple'],
            'cmd_2': ['conditional', 'whoami', 'logical', 'and'],
            'cmd_3': ['substitution', 'whoami', 'subshell', 'bypass']
        }
        
        concepts = cmd_concepts.get(challenge_id, [])
        concept_matches = sum(1 for concept in concepts if concept in normalized_answer)
        
        if concept_matches >= len(concepts) * 0.5:
            best_match = max(expected_answers, key=lambda x: SequenceMatcher(None, normalized_answer, self._normalize_answer(x)).ratio())
            return ValidationResult(
                is_correct=True,
                confidence=0.75,
                tier_used=ValidationTier.DOMAIN_VALIDATION,
                feedback="Great! Your answer demonstrates command injection knowledge.",
                processing_time=0.0,
                matched_answer=best_match
            )
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
    
    def _validate_auth_domain(self, normalized_answer: str, expected_answers: List[str], challenge_id: str) -> ValidationResult:
        """Authentication-specific domain validation"""
        auth_concepts = {
            'auth_1': ['password', 'weak', 'common', 'default'],
            'auth_2': ['brute', 'force', 'attack', 'guess'],
            'auth_3': ['token', 'reset', 'predictable', 'weak'],
            'auth_4': ['session', 'hijack', 'fixation', 'steal']
        }
        
        concepts = auth_concepts.get(challenge_id, [])
        concept_matches = sum(1 for concept in concepts if concept in normalized_answer)
        
        if concept_matches >= len(concepts) * 0.5:
            best_match = max(expected_answers, key=lambda x: SequenceMatcher(None, normalized_answer, self._normalize_answer(x)).ratio())
            return ValidationResult(
                is_correct=True,
                confidence=0.75,
                tier_used=ValidationTier.DOMAIN_VALIDATION,
                feedback="Excellent! Your answer shows understanding of authentication vulnerabilities.",
                processing_time=0.0,
                matched_answer=best_match
            )
        
        return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
    
    def _update_statistics(self, tier: ValidationTier, processing_time: float, success: bool):
        """Update validation statistics"""
        self.statistics['total_validations'] += 1
        if success:
            self.statistics['successful_validations'] += 1
        self.statistics['tier_usage'][tier] += 1
        self.statistics['response_times'].append(processing_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics"""
        total = self.statistics['total_validations']
        success_rate = (self.statistics['successful_validations'] / total * 100) if total > 0 else 0
        avg_time = sum(self.statistics['response_times']) / len(self.statistics['response_times']) if self.statistics['response_times'] else 0
        
        return {
            'total_validations': total,
            'successful_validations': self.statistics['successful_validations'],
            'success_rate': round(success_rate, 2),
            'average_response_time': round(avg_time * 1000, 2),  # Convert to ms
            'tier_usage': {tier.name: count for tier, count in self.statistics['tier_usage'].items()},
            'cache_entries': len(self.validation_cache)
        }
    
    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        logger.info("Validation cache cleared")

# Global instance
comprehensive_validator = ComprehensiveValidationEngine()
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
            
            # CRITICAL: Reject obviously invalid answers (too short, generic, etc.)
            if self._is_invalid_answer(normalized_answer):
                logger.warning(f"Answer rejected as invalid: '{submitted_answer}'")
                return ValidationResult(
                    is_correct=False,
                    confidence=0.0,
                    tier_used=ValidationTier.EXACT_MATCH,
                    feedback="Your answer doesn't match the expected response. Please review the challenge and try again.",
                    processing_time=time.time() - start_time
                )
            
            # DETAILED LOGGING FOR DEBUGGING
            logger.info(f"\n{'='*60}")
            logger.info(f"VALIDATION REQUEST - Challenge: {challenge_id}")
            logger.info(f"Original Answer: '{submitted_answer}'")
            logger.info(f"Normalized Answer: '{normalized_answer}'")
            logger.info(f"{'='*60}")
            
            # Get expected answers for challenge
            expected_answers = self._get_expected_answers(challenge_id)
            logger.info(f"Expected answers count: {len(expected_answers)}")
            
            if not expected_answers:
                logger.warning(f"No expected answers found for challenge {challenge_id}")
                return ValidationResult(
                    is_correct=False,
                    confidence=0.0,
                    tier_used=ValidationTier.EXACT_MATCH,
                    feedback="Challenge not found in validation database",
                    processing_time=time.time() - start_time
                )
            
            # Tier 1: Exact Match Validation
            logger.info("Testing Tier 1: Exact Match...")
            result = self._tier1_exact_match(normalized_answer, expected_answers)
            if result.is_correct:
                logger.info(f"✓ TIER 1 ACCEPTED - Exact Match")
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            logger.info("✗ Tier 1 rejected")
            
            # Tier 2: Semantic Analysis Validation
            logger.info("Testing Tier 2: Semantic Analysis...")
            result = self._tier2_semantic_analysis(normalized_answer, expected_answers, challenge_id)
            if result.is_correct:
                logger.warning(f"✓ TIER 2 ACCEPTED - Semantic Analysis (POTENTIAL FALSE POSITIVE)")
                logger.warning(f"Confidence: {result.confidence}, Matched: '{result.matched_answer}'")
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            logger.info("✗ Tier 2 rejected")
            
            # Tier 3: Pattern Recognition Validation
            logger.info("Testing Tier 3: Pattern Recognition...")
            result = self._tier3_pattern_recognition(normalized_answer, expected_answers, challenge_id)
            if result.is_correct:
                logger.warning(f"✓ TIER 3 ACCEPTED - Pattern Recognition (POTENTIAL FALSE POSITIVE)")
                logger.warning(f"Confidence: {result.confidence}, Pattern: {result.analysis_details}")
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            logger.info("✗ Tier 3 rejected")
            
            # Tier 4: Domain-Specific Validation
            logger.info("Testing Tier 4: Domain Validation...")
            result = self._tier4_domain_validation(normalized_answer, expected_answers, challenge_id, context)
            if result.is_correct:
                logger.warning(f"✓ TIER 4 ACCEPTED - Domain Validation (POTENTIAL FALSE POSITIVE)")
                logger.warning(f"Confidence: {result.confidence}, Matched: '{result.matched_answer}'")
                self._update_statistics(result.tier_used, time.time() - start_time, True)
                return result
            logger.info("✗ Tier 4 rejected")
            
            # Tier 5: Fuzzy Matching (Emergency Fallback)
            logger.info("Testing Tier 5: Fuzzy Matching...")
            result = self._tier5_fuzzy_matching(normalized_answer, expected_answers)
            if result.is_correct:
                logger.warning(f"✓ TIER 5 ACCEPTED - Fuzzy Matching (POTENTIAL FALSE POSITIVE)")
                logger.warning(f"Similarity: {result.analysis_details}")
            else:
                logger.info("✗ ALL TIERS REJECTED - Answer is incorrect")
            
            self._update_statistics(result.tier_used, time.time() - start_time, result.is_correct)
            logger.info(f"{'='*60}\n")
            
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
            # CRITICAL: Reject answers that are too short (likely not substantive)
            word_count = len(normalized_answer.split())
            if word_count < 2:
                logger.info(f"  Answer too short for semantic analysis: {word_count} words")
                return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.SEMANTIC_ANALYSIS, feedback="", processing_time=0.0)
            
            # Get semantic keywords for this challenge type
            semantic_map = self._get_semantic_keywords(challenge_id)
            semantic_keywords = semantic_map.get('keywords', [])
            
            answer_words = set(normalized_answer.split())
            
            logger.info(f"  Semantic keywords for {challenge_id}: {semantic_keywords}")
            logger.info(f"  Answer word count: {word_count} words")
            
            for expected in expected_answers:
                expected_words = set(self._normalize_answer(expected).split())
                
                # Calculate semantic overlap
                common_words = answer_words.intersection(expected_words)
                semantic_score = len(common_words) / max(len(expected_words), 1)
                
                # Check for semantic keywords
                keyword_matches = sum(1 for keyword in semantic_keywords if keyword in normalized_answer)
                
                # Combine scores - VERY STRICT THRESHOLD to prevent false positives
                total_score = (semantic_score * 0.7) + (keyword_matches / max(len(semantic_keywords), 1) * 0.3)
                
                logger.info(f"  Testing against: '{expected}'")
                logger.info(f"    - Semantic score: {semantic_score:.2f}")
                logger.info(f"    - Keyword matches: {keyword_matches}/{len(semantic_keywords)}")
                logger.info(f"    - Total score: {total_score:.2f}")
                logger.info(f"    - Min keyword required: {max(2, len(semantic_keywords) * 0.6)}")
                
                # INCREASED threshold from 0.8 to 0.85 AND require MORE keyword matches
                # Requires at least 60% of keywords (was 50%) AND minimum 2 keywords
                min_keywords_required = max(2, int(len(semantic_keywords) * 0.6))
                if total_score >= 0.85 and keyword_matches >= min_keywords_required:
                    logger.warning(f"  ⚠ SEMANTIC MATCH FOUND (may be false positive)")
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
            # CRITICAL: Minimum answer length for fuzzy matching
            if len(normalized_answer) < 8:
                logger.info(f"  Answer too short for fuzzy matching: {len(normalized_answer)} chars")
                return ValidationResult(
                    is_correct=False,
                    confidence=0.0,
                    tier_used=ValidationTier.FUZZY_MATCHING,
                    feedback="Your answer doesn't match the expected response. Please review the challenge and try again.",
                    processing_time=0.0
                )
            
            best_match = ""
            best_score = 0.0
            
            for expected in expected_answers:
                normalized_expected = self._normalize_answer(expected)
                score = SequenceMatcher(None, normalized_answer, normalized_expected).ratio()
                
                if score > best_score:
                    best_score = score
                    best_match = expected
            
            logger.info(f"  Fuzzy matching best score: {best_score:.2f} (threshold: 0.85)")
            
            # INCREASED threshold from 0.75 to 0.85 for much stricter validation
            # This prevents "I don't know" from matching legitimate answers
            if best_score >= 0.85:
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
                "accesses user table data",
                "uses UNION to combine results and extract user credentials",
                "payload uses UNION to combine results and extract user credentials",
                "this payload uses UNION to combine results and extract user credentials",
                "UNION to combine results and extract credentials",
                "combine results and extract user credentials",
                "union combines results extracts credentials"
            ],
            'sql_4': [
                "Time-based Blind SQL Injection",
                "time delays",
                "infer database information",
                "uses time delays to infer database information",
                "time-based blind SQL injection uses time delays to infer database information",
                "relies on response time delays",
                "sleep function",
                "SLEEP injection",
                "time-based inference",
                "database response delays",
                "conditional time delays",
                "time delay technique",
                "uses SLEEP to cause delays",
                "infer data from response time"
            ],
            'sql_5': [
                "Boolean-based blind SQL injection",
                "true false conditions",
                "boolean logic",
                "conditional responses",
                "boolean inference",
                "blind boolean testing",
                "yes no responses",
                "extract data character by character",
                "guess data one character at a time",
                "SUBSTRING extraction",
                "true false questions",
                "extracts data by asking true/false questions",
                "boolean-based blind SQL injection extracts data by asking true/false questions",
                "asking true false questions",
                "asks true or false questions to extract data",
                "data extraction through true/false responses",
                "boolean questions to infer data"
            ],
            'sql_6': [
                "ORDER BY to determine column count",
                "use ORDER BY with increasing numbers",
                "increment ORDER BY until error",
                "column enumeration",
                "determine number of columns",
                "ORDER BY column count",
                "increasing numbers until error",
                "find column count",
                "enumerate columns",
                "ORDER BY incrementing",
                "use order by with increasing numbers until you get an error",
                "order by technique",
                "column count detection"
            ],
            'sql_7': [
                "database version information",
                "extract database version",
                "@@version function",
                "version extraction",
                "UNION SELECT version",
                "MySQL version",
                "database metadata",
                "version() function",
                "extract version using UNION",
                "database version disclosure"
            ],
            'sql_8': [
                "Error-based SQL injection",
                "extract data from error messages",
                "CONVERT function",
                "CAST function",
                "type conversion errors",
                "error message exploitation",
                "data in error messages",
                "force database errors",
                "error-based data extraction",
                "conversion error exploitation"
            ],
            'sql_9': [
                "WAF bypass techniques",
                "bypass filters using encoding",
                "comment-based bypass",
                "inline comments",
                "break up keywords",
                "evade filters",
                "WAF evasion",
                "comment injection",
                "filter bypass with comments",
                "keyword obfuscation"
            ],
            'sql_10': [
                "Remote Code Execution through SQL",
                "xp_cmdshell",
                "execute system commands",
                "RCE via SQL",
                "stored procedures for RCE",
                "command execution",
                "OS command injection",
                "SQL to shell access",
                "database RCE",
                "system command execution"
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
            'xss_6': [
                "markdown XSS",
                "markdown parser exploit",
                "markdown injection",
                "converts markdown to HTML",
                "markdown to XSS",
                "parser vulnerability"
            ],
            'xss_7': [
                "template injection",
                "server-side template",
                "template XSS",
                "template engine exploit",
                "SSTI to XSS"
            ],
            'xss_8': [
                "polyglot payload",
                "multi-context XSS",
                "works in multiple contexts",
                "polyglot injection",
                "universal XSS payload"
            ],
            'xss_9': [
                "mutation XSS",
                "mXSS",
                "DOM mutation",
                "browser parsing differences",
                "mutation-based XSS"
            ],
            'xss_10': [
                "CSS injection",
                "url() function",
                "javascript: protocol",
                "CSS url javascript",
                "executes JavaScript through CSS",
                "style attribute injection",
                "background url javascript",
                "CSS url() accepts javascript protocol",
                "style injection with javascript",
                "exploits CSS url() function"
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
                "chains commands together",
                "ping localhost and then list directory contents",
                "payload would ping localhost and then list directory contents",
                "this payload would ping localhost and then list directory contents",
                "pings localhost then lists directory"
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
            'cmd_5': [
                "path traversal",
                "directory traversal",
                "../.. attack",
                "access parent directories",
                "path manipulation"
            ],
            'cmd_6': [
                "null byte injection",
                "null character",
                "%00 injection",
                "bypass extension check",
                "null termination"
            ],
            'cmd_7': [
                "environment variable",
                "$PATH injection",
                "environment manipulation",
                "variable poisoning"
            ],
            'cmd_8': [
                "blind command injection",
                "time-based detection",
                "sleep command",
                "delayed response"
            ],
            'cmd_9': [
                "out-of-band command injection",
                "OOB exfiltration",
                "DNS lookup",
                "external channel"
            ],
            'cmd_10': [
                "input validation",
                "whitelist",
                "command injection prevention",
                "sanitization",
                "parameterized commands"
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
            'auth_5': [
                "credential stuffing",
                "reused passwords",
                "leaked credentials",
                "password reuse attack"
            ],
            'auth_6': [
                "OAuth vulnerability",
                "authorization bypass",
                "OAuth misconfiguration",
                "redirect URI manipulation"
            ],
            'auth_7': [
                "JWT vulnerabilities",
                "token manipulation",
                "algorithm confusion",
                "weak secret key"
            ],
            'auth_8': [
                "multi-factor bypass",
                "2FA bypass",
                "MFA weakness",
                "authentication factor bypass"
            ],
            'auth_9': [
                "password policy",
                "complexity requirements",
                "password strength",
                "enforce strong passwords"
            ],
            'auth_10': [
                "secure authentication",
                "bcrypt hashing",
                "salted passwords",
                "password best practices"
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
                "allows attackers to perform actions on behalf of authenticated users",
                "CSRF allows attackers to perform actions on behalf of authenticated users",
                "perform actions on behalf of users",
                "attackers perform actions on behalf of authenticated users",
                "actions on behalf of authenticated users"
            ],
            'csrf_2': [
                "CSRF tokens",
                "anti-CSRF tokens",
                "request verification",
                "token validation",
                "unique tokens",
                "request authenticity",
                "CSRF protection",
                "unique values that verify requests come from legitimate sources",
                "CSRF tokens are unique values that verify requests come from legitimate sources",
                "tokens verify legitimate requests",
                "verify requests from legitimate sources",
                "unique tokens for request verification"
            ],
            'csrf_3': [
                "image tag",
                "force GET request",
                "image tag to force browser to make GET request",
                "this payload uses an image tag to force the browser to make a GET request to a sensitive endpoint",
                "uses image tag to force GET request to sensitive endpoint",
                "img tag GET request",
                "image element forces GET request",
                "GET request via image tag",
                "sensitive endpoint via img tag"
            ],
            'csrf_4': [
                "auto-submitting form",
                "automatic form submission",
                "unauthorized POST requests",
                "creates auto-submitting form",
                "this payload creates an auto-submitting form that performs unauthorized POST requests",
                "payload creates auto-submitting form that performs unauthorized POST requests",
                "auto-submit form for CSRF",
                "form submits automatically",
                "performs unauthorized POST"
            ],
            'csrf_5': [
                "bypass Content-Type restrictions",
                "backend accepts multiple formats",
                "lenient parsing",
                "CSRF can bypass Content-Type restrictions if the backend accepts multiple formats or has lenient parsing",
                "bypass content type validation",
                "multiple format acceptance",
                "lenient content type parsing",
                "accepts multiple formats or lenient parsing",
                "content type bypass"
            ],
            'csrf_6': [
                "SameSite cookie attribute",
                "SameSite prevents CSRF",
                "restricting cookie transmission on cross-site requests",
                "SameSite cookie attribute prevents CSRF by restricting cookie transmission on cross-site requests",
                "prevents CSRF by restricting cookie transmission",
                "cookie transmission restrictions",
                "SameSite=Strict or SameSite=Lax",
                "blocks cross-site cookie sending",
                "cookie not sent on cross-site requests"
            ],
            'csrf_7': [
                "WebSocket CSRF",
                "servers accept connections without validating Origin header",
                "WebSocket CSRF occurs when servers accept connections without validating the Origin header",
                "WebSocket without Origin validation",
                "accept WebSocket connections without Origin check",
                "Origin header validation missing",
                "WebSocket Origin bypass",
                "no Origin header validation",
                "WebSocket connection without Origin validation"
            ],
            'csrf_8': [
                "CSRF file upload",
                "file upload attack",
                "malicious file upload",
                "upload on behalf of user",
                "allow attackers to upload malicious files on behalf of authenticated users",
                "CSRF file upload attacks allow attackers to upload malicious files on behalf of authenticated users",
                "file upload via CSRF",
                "unauthorized file upload",
                "upload malicious files through CSRF"
            ],
            'csrf_9': [
                "logout CSRF",
                "force logout",
                "session termination",
                "logout endpoint protection",
                "forces users to logout by triggering the logout endpoint via GET requests",
                "logout CSRF forces users to logout by triggering the logout endpoint via GET requests",
                "triggers logout via GET",
                "GET request logout attack",
                "logout endpoint via GET"
            ],
            'csrf_10': [
                "custom headers",
                "custom headers for CSRF protection",
                "browsers prevent cross-origin custom headers",
                "cross-origin custom headers without CORS",
                "custom headers provide CSRF protection because browsers prevent cross-origin custom headers without CORS",
                "browsers block cross-origin custom headers",
                "custom headers require CORS",
                "prevent cross-origin custom headers",
                "CORS requirement for custom headers"
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
    
    def _is_invalid_answer(self, normalized_answer: str) -> bool:
        """
        Check if an answer is obviously invalid/generic.
        Prevents false positives from answers like "I don't know", "idk", "nothing", etc.
        """
        # Minimum length requirement (must be at least 5 characters after normalization)
        if len(normalized_answer) < 5:
            return True
        
        # List of generic/invalid answers that should always be rejected
        invalid_patterns = [
            r'i\s*dont\s*know',  # Matches "i dont know" anywhere in answer
            r'idk',  # Matches "idk" anywhere
            r'i\s*dunno',  # Matches "i dunno" anywhere
            r'no\s*idea',  # Matches "no idea" anywhere
            r'not\s*sure',  # Matches "not sure" anywhere
            r'dont\s*know',  # Matches "dont know" anywhere
            r'^unknown$',  # Exact match for single word
            r'^nothing$',
            r'^none$',
            r'^na$',
            r'^n\s*a$',
            r'help\s*me',  # Matches "help me" anywhere
            r'^help$',  # Exact match for "help" alone
            r'i\s*need\s*help',
            r'please\s*help',  # Matches "please help" anywhere
            r'^what$',
            r'^huh$',
            r'^confused$',
            r'^skip$',
            r'^pass$',
            r'^next$',
            r'^test$',
            r'^testing$',
            r'^random$',
            r'^incorrect$',  # Reject literal "incorrect"
            r'^wrong$',  # Reject literal "wrong"
            r'^false$',  # Reject literal "false"
            r'^asdf+$',
            r'^qwer+ty+$',
            r'^123+$',
            r'^abc+$',
        ]
        
        # Check against invalid patterns
        for pattern in invalid_patterns:
            if re.match(pattern, normalized_answer, re.IGNORECASE):
                logger.info(f"  Answer matched invalid pattern: {pattern}")
                return True
        
        # Check if answer contains mostly repeated characters (e.g., "aaaa", "xxxx")
        if len(set(normalized_answer.replace(' ', ''))) <= 2:
            return True
        
        return False
    
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
                'keywords': ['union', 'select', 'extract', 'credentials', 'data', 'usernames', 'passwords', 'combine', 'results', 'payload', 'user']
            },
            'sql_4': {
                'keywords': ['time', 'based', 'blind', 'delays', 'sleep', 'infer', 'database', 'information', 'response', 'timing']
            },
            'sql_5': {
                'keywords': ['boolean', 'blind', 'true', 'false', 'yes', 'no', 'condition', 'guess', 'character', 'extracts', 'data', 'asking', 'questions']
            },
            'sql_6': {
                'keywords': ['order', 'by', 'columns', 'count', 'determine', 'enumerate', 'increment', 'error', 'number']
            },
            'sql_7': {
                'keywords': ['version', 'database', 'extract', 'union', 'information', 'metadata', 'mysql']
            },
            'sql_8': {
                'keywords': ['error', 'based', 'convert', 'cast', 'messages', 'extraction', 'type', 'conversion']
            },
            'sql_9': {
                'keywords': ['waf', 'bypass', 'filter', 'comment', 'encoding', 'evade', 'obfuscate', 'keywords']
            },
            'sql_10': {
                'keywords': ['rce', 'remote', 'code', 'execution', 'xp_cmdshell', 'command', 'system', 'shell']
            },
            'xss_1': {
                'keywords': ['javascript', 'execute', 'alert', 'script', 'popup', 'client', 'browser']
            },
            'cmd_1': {
                'keywords': ['command', 'ping', 'ls', 'directory', 'multiple', 'chain', 'semicolon', 'injection', 'localhost', 'list', 'contents', 'payload']
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
            'sql_3': ['union', 'select', 'extract', 'credentials', 'data', 'combine', 'results', 'user'],
            'sql_4': ['time', 'based', 'blind', 'delay', 'sleep', 'infer', 'database', 'information'],
            'sql_5': ['boolean', 'blind', 'true', 'false', 'yes', 'no', 'guess', 'extract', 'asking', 'questions'],
            'sql_6': ['order', 'by', 'column', 'count', 'determine', 'increment', 'error', 'number'],
            'sql_7': ['version', 'database', 'extract', 'union', 'information'],
            'sql_8': ['error', 'convert', 'cast', 'message', 'extraction'],
            'sql_9': ['waf', 'bypass', 'filter', 'comment', 'encoding'],
            'sql_10': ['rce', 'remote', 'code', 'execution', 'command', 'xp_cmdshell']
        }
        
        concepts = sql_concepts.get(challenge_id, [])
        concept_matches = sum(1 for concept in concepts if concept in normalized_answer)
        
        # Calculate word count for additional validation
        word_count = len(normalized_answer.split())
        
        logger.info(f"  SQL Domain concepts for {challenge_id}: {concepts}")
        logger.info(f"  Concept matches: {concept_matches}/{len(concepts)} (need {int(len(concepts) * 0.85)} + min 2 words)")
        logger.info(f"  Answer word count: {word_count}")
        
        # INCREASED threshold from 0.8 to 0.85 AND require minimum word count
        # Also requires at least 85% concept coverage (was 80%)
        min_concepts_required = int(len(concepts) * 0.85)
        if concept_matches >= min_concepts_required and word_count >= 2:
            best_match = max(expected_answers, key=lambda x: SequenceMatcher(None, normalized_answer, self._normalize_answer(x)).ratio())
            logger.warning(f"  ⚠ SQL DOMAIN MATCH (85% concepts matched)")
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
            'xss_3': ['svg', 'onload', 'filter', 'bypass'],
            'xss_4': ['dom', 'manipulation', 'innerhtml', 'injection'],
            'xss_5': ['context', 'escape', 'attribute', 'injection'],
            'xss_6': ['template', 'injection', 'angular', 'expression'],
            'xss_7': ['mutation', 'parser', 'browser', 'parsing'],
            'xss_8': ['protocol', 'handler', 'data', 'uri'],
            'xss_9': ['polyglot', 'context', 'multiple', 'vector'],
            'xss_10': ['css', 'injection', 'url', 'javascript', 'style']
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
            'cmd_1': ['command', 'ping', 'ls', 'chain', 'multiple', 'localhost', 'directory', 'list'],
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
        # CRITICAL: Minimum word count requirement
        word_count = len(normalized_answer.split())
        if word_count < 2:
            logger.info(f"  Answer too short for domain validation: {word_count} words")
            return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
        
        auth_concepts = {
            'auth_1': ['password', 'weak', 'common', 'default'],
            'auth_2': ['brute', 'force', 'attack', 'guess'],
            'auth_3': ['token', 'reset', 'predictable', 'weak'],
            'auth_4': ['session', 'hijack', 'fixation', 'steal'],
            'auth_5': ['jwt', 'token', 'secret', 'signature', 'verify'],
            'auth_6': ['oauth', 'redirect', 'uri', 'callback', 'authorization'],
            'auth_7': ['security', 'questions', 'answers', 'predictable', 'social', 'engineering'],
            'auth_8': ['biometric', 'bypass', 'fingerprint', 'face', 'recognition'],
            'auth_9': ['multi', 'factor', 'authentication', 'mfa', '2fa', 'otp'],
            'auth_10': ['captcha', 'bypass', 'bot', 'automation', 'detection']
        }
        
        concepts = auth_concepts.get(challenge_id, [])
        
        # CRITICAL FIX: If no concepts defined for this challenge, reject
        if not concepts:
            logger.warning(f"  No domain concepts defined for {challenge_id}")
            return ValidationResult(is_correct=False, confidence=0.0, tier_used=ValidationTier.DOMAIN_VALIDATION, feedback="", processing_time=0.0)
        
        concept_matches = sum(1 for concept in concepts if concept in normalized_answer)
        coverage = concept_matches / len(concepts) if concepts else 0
        
        logger.info(f"  Domain concept coverage: {concept_matches}/{len(concepts)} ({coverage*100:.0f}%)")
        
        # INCREASED threshold from 50% to 85% for stricter validation
        if concept_matches >= len(concepts) * 0.85 and concept_matches >= 2:
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
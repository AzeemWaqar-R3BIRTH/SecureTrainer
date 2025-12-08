"""
Enhanced Challenge Model with Multi-Level Variants
Production-ready implementation for SecureTrainer
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DifficultyLevel(Enum):
    """Challenge difficulty levels."""
    BEGINNER = ("beginner", 1, "Introduction to basic concepts")
    INTERMEDIATE = ("intermediate", 2, "Practical application")
    ADVANCED = ("advanced", 3, "Complex scenarios")
    EXPERT = ("expert", 4, "Professional-level challenges")

    def __init__(self, level_name: str, numeric_value: int, description: str):
        self.level_name = level_name
        self.numeric_value = numeric_value
        self.description = description

@dataclass
class ChallengeVariant:
    """Individual challenge variant with metadata."""
    id: str
    title: str
    category: str
    difficulty: DifficultyLevel
    scenario: str
    question: str
    payload_example: str
    expected_solutions: List[str]
    hints: List[str]
    score_weight: int
    estimated_time: int
    prerequisites: List[str]
    learning_objectives: List[str]
    validation_patterns: List[str]
    interactive_demo: bool
    demo_html: Optional[str] = None

class EnhancedChallengeModel:
    """Enhanced challenge model with comprehensive variants."""
    
    def __init__(self):
        """Initialize challenge model."""
        self.challenge_variants = self._build_challenge_database()
        logger.info(f"Enhanced Challenge Model initialized with {sum(len(v) for v in self.challenge_variants.values())} variants")
    
    def get_challenges_by_difficulty(self, difficulty: DifficultyLevel, category: Optional[str] = None) -> List[ChallengeVariant]:
        """Get challenges by difficulty and category."""
        challenges = []
        
        if category:
            category_challenges = self.challenge_variants.get(category, [])
            challenges = [c for c in category_challenges if c.difficulty == difficulty]
        else:
            for cat_challenges in self.challenge_variants.values():
                challenges.extend([c for c in cat_challenges if c.difficulty == difficulty])
        
        return challenges
    
    def get_adaptive_sequence(self, user_skill: float, category: Optional[str] = None, count: int = 5) -> List[ChallengeVariant]:
        """Generate adaptive challenge sequence."""
        # Determine difficulty distribution
        if user_skill < 0.3:
            dist = {"beginner": 3, "intermediate": 2}
        elif user_skill < 0.6:
            dist = {"beginner": 1, "intermediate": 3, "advanced": 1}
        elif user_skill < 0.8:
            dist = {"intermediate": 2, "advanced": 2, "expert": 1}
        else:
            dist = {"advanced": 2, "expert": 3}
        
        # Select challenges
        selected = []
        for diff_name, diff_count in dist.items():
            difficulty = next(d for d in DifficultyLevel if d.level_name == diff_name)
            candidates = self.get_challenges_by_difficulty(difficulty, category)
            selected.extend(random.sample(candidates, min(diff_count, len(candidates))))
        
        return selected[:count]
    
    def get_challenge_by_id(self, challenge_id: str) -> Optional[ChallengeVariant]:
        """Get challenge by ID."""
        for challenges in self.challenge_variants.values():
            for challenge in challenges:
                if challenge.id == challenge_id:
                    return challenge
        return None
    
    def _build_challenge_database(self) -> Dict[str, List[ChallengeVariant]]:
        """Build challenge database."""
        return {
            'sql_injection': self._build_sql_challenges(),
            'xss': self._build_xss_challenges(),
            'command_injection': self._build_cmd_challenges(),
            'authentication': self._build_auth_challenges()
        }
    
    def _build_sql_challenges(self) -> List[ChallengeVariant]:
        """Build SQL injection challenges."""
        return [
            ChallengeVariant(
                id="sql_beginner_001",
                title="Basic Authentication Bypass",
                category="sql_injection",
                difficulty=DifficultyLevel.BEGINNER,
                scenario="Login form with string concatenation",
                question="Bypass authentication using SQL injection",
                payload_example="admin' OR '1'='1' --",
                expected_solutions=["' OR '1'='1' --", "admin'--", "' OR 1=1--"],
                hints=[
                    "Use OR operator to make condition always true",
                    "Try SQL comments to ignore password check",
                    "Focus on the WHERE clause structure"
                ],
                score_weight=100,
                estimated_time=60,
                prerequisites=[],
                learning_objectives=["Understand SQL injection", "Learn OR-based bypass"],
                validation_patterns=["(?i)(or\\s+['\"]?1['\"]?\\s*=\\s*['\"]?1['\"]?)", "(?i)(or\\s+true|1=1)"],
                interactive_demo=True,
                demo_html="""
                <div class="demo-container">
                    <h4>SQL Injection Login Demo</h4>
                    <input type="text" id="username" placeholder="Username" />
                    <input type="password" id="password" placeholder="Password" />
                    <button onclick="login()">Login</button>
                    <div id="sql-query"></div>
                    <div id="result"></div>
                </div>
                <script>
                function login() {
                    const user = document.getElementById('username').value;
                    const pass = document.getElementById('password').value;
                    document.getElementById('sql-query').innerHTML = 
                        `<strong>Query:</strong> SELECT * FROM users WHERE username='${user}' AND password='${pass}'`;
                    
                    if (user.includes("' OR ") || user.includes("'--")) {
                        document.getElementById('result').innerHTML = '<div class="success">✅ SQL Injection successful!</div>';
                    } else {
                        document.getElementById('result').innerHTML = '<div class="error">❌ Login failed</div>';
                    }
                }
                </script>
                """
            ),
            ChallengeVariant(
                id="sql_intermediate_001",
                title="UNION-based Data Extraction",
                category="sql_injection",
                difficulty=DifficultyLevel.INTERMEDIATE,
                scenario="Search page vulnerable to UNION injection",
                question="Extract user data using UNION SELECT",
                payload_example="' UNION SELECT username, password FROM users--",
                expected_solutions=["UNION SELECT", "UNION ALL SELECT"],
                hints=[
                    "Use UNION to combine query results",
                    "Match the number of columns",
                    "Comment out the rest of the query"
                ],
                score_weight=200,
                estimated_time=120,
                prerequisites=["sql_beginner_001"],
                learning_objectives=["Master UNION injection", "Learn data extraction"],
                validation_patterns=["(?i)union\\s+(all\\s+)?select"],
                interactive_demo=False
            ),
            ChallengeVariant(
                id="sql_advanced_001",
                title="Blind SQL Injection",
                category="sql_injection",
                difficulty=DifficultyLevel.ADVANCED,
                scenario="Application with error suppression",
                question="Extract data using boolean-based blind injection",
                payload_example="' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--",
                expected_solutions=["SUBSTRING", "ASCII", "boolean-based"],
                hints=[
                    "Use boolean conditions to infer data",
                    "Extract data character by character",
                    "Look for true/false response patterns"
                ],
                score_weight=350,
                estimated_time=240,
                prerequisites=["sql_intermediate_001"],
                learning_objectives=["Master blind injection", "Learn inference attacks"],
                validation_patterns=["(?i)(substring|ascii|length)\\s*\\("],
                interactive_demo=False
            ),
            ChallengeVariant(
                id="sql_expert_001",
                title="Advanced WAF Bypass",
                category="sql_injection",
                difficulty=DifficultyLevel.EXPERT,
                scenario="Protected application with WAF",
                question="Bypass modern security filters",
                payload_example="admin'/**/OR/**/1=1--",
                expected_solutions=["WAF bypass", "encoding", "obfuscation"],
                hints=[
                    "Use comments to break keywords",
                    "Try encoding techniques",
                    "Experiment with alternative syntax"
                ],
                score_weight=500,
                estimated_time=360,
                prerequisites=["sql_advanced_001"],
                learning_objectives=["Master WAF evasion", "Learn advanced techniques"],
                validation_patterns=["(?i)\\/\\*.*\\*\\/", "(?i)(0x[0-9a-f]+)"],
                interactive_demo=False
            )
        ]
    
    def _build_xss_challenges(self) -> List[ChallengeVariant]:
        """Build XSS challenges."""
        return [
            ChallengeVariant(
                id="xss_beginner_001",
                title="Basic Reflected XSS",
                category="xss",
                difficulty=DifficultyLevel.BEGINNER,
                scenario="Search page reflecting user input",
                question="Execute JavaScript using script tags",
                payload_example="<script>alert('XSS')</script>",
                expected_solutions=["<script>alert", "<script>", "javascript:"],
                hints=[
                    "Try basic script tags",
                    "Use alert() function to prove execution",
                    "Look for input reflection points"
                ],
                score_weight=100,
                estimated_time=60,
                prerequisites=[],
                learning_objectives=["Understand XSS basics", "Learn payload construction"],
                validation_patterns=["(?i)<script[^>]*>", "(?i)javascript\\s*:"],
                interactive_demo=True,
                demo_html="""
                <div class="demo-container">
                    <h4>XSS Search Demo</h4>
                    <input type="text" id="search-input" placeholder="Search..." />
                    <button onclick="search()">Search</button>
                    <div>Results for: <span id="output"></span></div>
                </div>
                <script>
                function search() {
                    const input = document.getElementById('search-input').value;
                    document.getElementById('output').innerHTML = input;
                }
                </script>
                """
            ),
            ChallengeVariant(
                id="xss_intermediate_001",
                title="Event Handler XSS",
                category="xss",
                difficulty=DifficultyLevel.INTERMEDIATE,
                scenario="Profile page with HTML attribute injection",
                question="Execute JavaScript using event handlers",
                payload_example="<img src=x onerror=alert('XSS')>",
                expected_solutions=["onerror=", "onload=", "onclick="],
                hints=[
                    "Use HTML event handlers",
                    "Try img, svg, or other elements",
                    "Focus on error events"
                ],
                score_weight=200,
                estimated_time=120,
                prerequisites=["xss_beginner_001"],
                learning_objectives=["Learn event-based XSS", "Master HTML injection"],
                validation_patterns=["(?i)on\\w+\\s*="],
                interactive_demo=False
            )
        ]
    
    def _build_cmd_challenges(self) -> List[ChallengeVariant]:
        """Build command injection challenges."""
        return [
            ChallengeVariant(
                id="cmd_beginner_001",
                title="Basic Command Chaining",
                category="command_injection",
                difficulty=DifficultyLevel.BEGINNER,
                scenario="Ping utility with command injection",
                question="Execute additional commands using separators",
                payload_example="127.0.0.1; ls",
                expected_solutions=["; ls", "&& whoami", "| cat"],
                hints=[
                    "Use command separators like ;",
                    "Try logical operators && or ||",
                    "Experiment with pipes |"
                ],
                score_weight=100,
                estimated_time=60,
                prerequisites=[],
                learning_objectives=["Understand command injection", "Learn command chaining"],
                validation_patterns=["(?i)[;&|]+\\s*\\w+"],
                interactive_demo=True,
                demo_html="""
                <div class="demo-container">
                    <h4>Ping Command Demo</h4>
                    <input type="text" id="ping-input" placeholder="IP Address" />
                    <button onclick="ping()">Ping</button>
                    <div id="ping-output"></div>
                </div>
                <script>
                function ping() {
                    const input = document.getElementById('ping-input').value;
                    const output = document.getElementById('ping-output');
                    
                    if (input.includes(';') || input.includes('&&')) {
                        output.innerHTML = '<div class="success">✅ Command injection successful!</div><pre>PING result + additional command output</pre>';
                    } else {
                        output.innerHTML = '<div class="normal">PING ' + input + ': Success</div>';
                    }
                }
                </script>
                """
            )
        ]
    
    def _build_auth_challenges(self) -> List[ChallengeVariant]:
        """Build authentication challenges."""
        return [
            ChallengeVariant(
                id="auth_beginner_001",
                title="Weak Password Attack",
                category="authentication",
                difficulty=DifficultyLevel.BEGINNER,
                scenario="Login with common weak passwords",
                question="Gain access using password guessing",
                payload_example="admin/password",
                expected_solutions=["password", "123456", "admin"],
                hints=[
                    "Try common passwords",
                    "Use default credentials",
                    "Think about obvious choices"
                ],
                score_weight=100,
                estimated_time=60,
                prerequisites=[],
                learning_objectives=["Understand weak passwords", "Learn credential attacks"],
                validation_patterns=["(?i)(password|123456|admin)"],
                interactive_demo=True,
                demo_html="""
                <div class="demo-container">
                    <h4>Weak Password Demo</h4>
                    <input type="text" id="auth-user" placeholder="Username" />
                    <input type="password" id="auth-pass" placeholder="Password" />
                    <button onclick="authenticate()">Login</button>
                    <div id="auth-result"></div>
                </div>
                <script>
                function authenticate() {
                    const user = document.getElementById('auth-user').value;
                    const pass = document.getElementById('auth-pass').value;
                    const weak_passwords = ['password', '123456', 'admin', 'qwerty'];
                    
                    if (weak_passwords.includes(pass.toLowerCase())) {
                        document.getElementById('auth-result').innerHTML = '<div class="success">✅ Weak password found!</div>';
                    } else {
                        document.getElementById('auth-result').innerHTML = '<div class="error">❌ Access denied</div>';
                    }
                }
                </script>
                """
            )
        ]
"""
Intelligent Hint Generation System
Production-ready implementation for SecureTrainer

This module implements adaptive hint generation that:
1. Analyzes user struggle patterns and learning style
2. Provides contextual hints based on attempt history
3. Adapts hint complexity to user skill level
4. Generates personalized learning guidance
5. Balances help with learning independence
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HintLevel(Enum):
    """Hint complexity levels."""
    SUBTLE = ("subtle", 1, "Gentle nudge in the right direction")
    GUIDING = ("guiding", 2, "Clear direction without giving away solution")
    DETAILED = ("detailed", 3, "Specific guidance with examples")
    EXPLICIT = ("explicit", 4, "Direct instruction with near-complete solution")

    def __init__(self, level_name: str, complexity: int, description: str):
        self.level_name = level_name
        self.complexity = complexity
        self.description = description

class LearningStyle(Enum):
    """User learning style classifications."""
    INDEPENDENT = "independent"      # Prefers minimal hints, learns through experimentation
    GUIDED = "guided"               # Benefits from structured, step-by-step guidance
    VISUAL = "visual"               # Learns better with examples and demonstrations
    ANALYTICAL = "analytical"       # Prefers technical explanations and theory
    PRACTICAL = "practical"         # Learns through hands-on practice and trial

@dataclass
class HintContext:
    """Context information for hint generation."""
    user_id: str
    challenge_category: str
    difficulty_level: str
    attempt_count: int
    time_spent: float
    previous_hints: List[str]
    user_learning_style: LearningStyle
    struggle_indicators: List[str]
    skill_level: float

@dataclass
class GeneratedHint:
    """Generated hint with metadata."""
    content: str
    level: HintLevel
    reasoning: str
    effectiveness_prediction: float
    follow_up_suggestions: List[str]
    estimated_success_increase: float

class IntelligentHintGenerator:
    """
    AI-powered hint generation system for adaptive learning support.
    
    Features:
    - Contextual hint generation based on user patterns
    - Adaptive complexity based on learning style
    - Progressive hint system with escalating detail
    - Personalized learning guidance
    """
    
    def __init__(self, db_connection=None):
        """Initialize the intelligent hint generator."""
        self.db = db_connection
        self.hint_templates = self._build_hint_templates()
        self.learning_patterns = self._build_learning_patterns()
        self.struggle_detectors = self._build_struggle_detectors()
        self.hint_effectiveness_cache = {}
        
        logger.info("Intelligent Hint Generator initialized successfully")
    
    def generate_adaptive_hint(self, context: HintContext, challenge: Dict[str, Any]) -> GeneratedHint:
        """
        Generate an adaptive hint based on user context and challenge data.
        
        Args:
            context: User context and attempt information
            challenge: Challenge data and metadata
            
        Returns:
            GeneratedHint with personalized content and metadata
        """
        try:
            # Analyze user struggle patterns
            struggle_analysis = self._analyze_struggle_patterns(context)
            
            # Determine optimal hint level
            optimal_level = self._determine_hint_level(context, struggle_analysis)
            
            # Generate category-specific hint
            hint_content = self._generate_category_hint(
                challenge, context, optimal_level
            )
            
            # Personalize based on learning style
            personalized_hint = self._personalize_hint(
                hint_content, context.user_learning_style, context
            )
            
            # Predict effectiveness
            effectiveness = self._predict_hint_effectiveness(
                personalized_hint, context, challenge
            )
            
            # Generate follow-up suggestions
            follow_ups = self._generate_follow_up_suggestions(
                context, challenge, optimal_level
            )
            
            # Calculate success increase estimate
            success_increase = self._estimate_success_increase(
                optimal_level, context, effectiveness
            )
            
            # Create reasoning explanation
            reasoning = self._explain_hint_reasoning(
                optimal_level, context, struggle_analysis
            )
            
            generated_hint = GeneratedHint(
                content=personalized_hint,
                level=optimal_level,
                reasoning=reasoning,
                effectiveness_prediction=effectiveness,
                follow_up_suggestions=follow_ups,
                estimated_success_increase=success_increase
            )
            
            # Record hint for learning
            self._record_hint_generation(context, generated_hint, challenge)
            
            logger.info(f"Generated {optimal_level.level_name} hint for user {context.user_id}")
            return generated_hint
            
        except Exception as e:
            logger.error(f"Error generating hint for user {context.user_id}: {e}")
            return self._generate_fallback_hint(challenge, context)
    
    def analyze_hint_effectiveness(self, user_id: str, hint_id: str, 
                                 user_success: bool, time_to_success: float) -> None:
        """
        Analyze the effectiveness of a generated hint for continuous improvement.
        
        Args:
            user_id: User who received the hint
            hint_id: Unique identifier for the hint
            user_success: Whether user succeeded after the hint
            time_to_success: Time taken to succeed after hint
        """
        try:
            effectiveness_data = {
                'user_id': user_id,
                'hint_id': hint_id,
                'success': user_success,
                'time_to_success': time_to_success,
                'timestamp': datetime.now()
            }
            
            # Store effectiveness data
            if self.db:
                self.db.hint_effectiveness.insert_one(effectiveness_data)
            
            # Update hint effectiveness cache
            self.hint_effectiveness_cache[hint_id] = effectiveness_data
            
            logger.info(f"Recorded hint effectiveness for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error recording hint effectiveness: {e}")
    
    def get_hint_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get analytics about user's hint usage patterns and effectiveness.
        
        Args:
            user_id: User to analyze
            
        Returns:
            Dictionary containing hint analytics
        """
        try:
            if not self.db:
                return {}
            
            # Get user's hint history
            hint_history = list(self.db.hint_generations.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).limit(50))
            
            # Get effectiveness data
            effectiveness_data = list(self.db.hint_effectiveness.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).limit(50))
            
            analytics = {
                'hint_usage_patterns': self._analyze_hint_usage_patterns(hint_history),
                'effectiveness_trends': self._analyze_effectiveness_trends(effectiveness_data),
                'learning_progress': self._analyze_learning_progress(hint_history, effectiveness_data),
                'recommendations': self._generate_hint_recommendations(user_id, hint_history)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating hint analytics for user {user_id}: {e}")
            return {}
    
    def _analyze_struggle_patterns(self, context: HintContext) -> Dict[str, Any]:
        """Analyze user's struggle patterns to inform hint generation."""
        struggle_indicators = {
            'time_pressure': context.time_spent > 300,  # More than 5 minutes
            'multiple_attempts': context.attempt_count > 2,
            'hint_dependency': len(context.previous_hints) > 2,
            'category_weakness': context.skill_level < 0.5,
            'escalating_hints': self._check_escalating_hint_pattern(context.previous_hints)
        }
        
        struggle_severity = sum(struggle_indicators.values()) / len(struggle_indicators)
        
        return {
            'indicators': struggle_indicators,
            'severity': struggle_severity,
            'primary_struggle': self._identify_primary_struggle(struggle_indicators),
            'recommended_approach': self._recommend_approach(struggle_indicators)
        }
    
    def _determine_hint_level(self, context: HintContext, 
                            struggle_analysis: Dict[str, Any]) -> HintLevel:
        """Determine the optimal hint level based on context and struggle analysis."""
        
        base_level = HintLevel.GUIDING  # Default level
        
        # Adjust based on learning style
        if context.user_learning_style == LearningStyle.INDEPENDENT:
            base_level = HintLevel.SUBTLE
        elif context.user_learning_style == LearningStyle.GUIDED:
            base_level = HintLevel.DETAILED
        
        # Adjust based on struggle severity
        struggle_severity = struggle_analysis['severity']
        if struggle_severity > 0.7:
            # High struggle - provide more explicit help
            if base_level == HintLevel.SUBTLE:
                base_level = HintLevel.GUIDING
            elif base_level == HintLevel.GUIDING:
                base_level = HintLevel.DETAILED
            elif base_level == HintLevel.DETAILED:
                base_level = HintLevel.EXPLICIT
        elif struggle_severity < 0.3:
            # Low struggle - maintain independence
            if base_level == HintLevel.DETAILED:
                base_level = HintLevel.GUIDING
            elif base_level == HintLevel.EXPLICIT:
                base_level = HintLevel.DETAILED
        
        # Adjust based on attempt count
        if context.attempt_count >= 4:
            base_level = HintLevel.EXPLICIT
        elif context.attempt_count >= 3:
            base_level = HintLevel.DETAILED
        
        # Ensure progression in hint complexity
        if context.previous_hints:
            last_hint_level = self._determine_previous_hint_level(context.previous_hints[-1])
            if last_hint_level and last_hint_level.complexity >= base_level.complexity:
                # Escalate to next level
                next_levels = {
                    HintLevel.SUBTLE: HintLevel.GUIDING,
                    HintLevel.GUIDING: HintLevel.DETAILED,
                    HintLevel.DETAILED: HintLevel.EXPLICIT,
                    HintLevel.EXPLICIT: HintLevel.EXPLICIT  # Max level
                }
                base_level = next_levels.get(last_hint_level, HintLevel.EXPLICIT)
        
        return base_level
    
    def _generate_category_hint(self, challenge: Dict[str, Any], 
                              context: HintContext, level: HintLevel) -> str:
        """Generate category-specific hint content."""
        
        category = context.challenge_category.lower()
        templates = self.hint_templates.get(category, self.hint_templates['generic'])
        
        level_templates = templates.get(level.level_name, templates.get('guiding', []))
        
        if not level_templates:
            return self._generate_generic_hint(challenge, level)
        
        # Select appropriate template based on challenge specifics
        template = self._select_best_template(level_templates, challenge, context)
        
        # Fill template with challenge-specific information
        hint_content = self._fill_hint_template(template, challenge, context)
        
        return hint_content
    
    def _personalize_hint(self, base_hint: str, learning_style: LearningStyle, 
                         context: HintContext) -> str:
        """Personalize hint based on user's learning style."""
        
        personalizations = {
            LearningStyle.INDEPENDENT: self._add_independent_elements,
            LearningStyle.GUIDED: self._add_guided_elements,
            LearningStyle.VISUAL: self._add_visual_elements,
            LearningStyle.ANALYTICAL: self._add_analytical_elements,
            LearningStyle.PRACTICAL: self._add_practical_elements
        }
        
        personalizer = personalizations.get(learning_style, lambda x, y: x)
        return personalizer(base_hint, context)
    
    def _predict_hint_effectiveness(self, hint_content: str, context: HintContext, 
                                  challenge: Dict[str, Any]) -> float:
        """Predict the effectiveness of the generated hint."""
        
        # Base effectiveness from historical data
        base_effectiveness = 0.6
        
        # Adjust based on hint level appropriateness
        level_appropriateness = self._calculate_level_appropriateness(context)
        
        # Adjust based on content quality
        content_quality = self._assess_hint_content_quality(hint_content, challenge)
        
        # Adjust based on user's learning style match
        style_match = self._calculate_learning_style_match(hint_content, context.user_learning_style)
        
        # Adjust based on timing
        timing_factor = self._calculate_timing_factor(context)
        
        # Combined effectiveness prediction
        effectiveness = base_effectiveness * (
            (level_appropriateness * 0.3) +
            (content_quality * 0.3) +
            (style_match * 0.2) +
            (timing_factor * 0.2)
        )
        
        return min(max(effectiveness, 0.1), 0.95)  # Clamp between 0.1 and 0.95
    
    def _generate_follow_up_suggestions(self, context: HintContext, 
                                      challenge: Dict[str, Any], 
                                      hint_level: HintLevel) -> List[str]:
        """Generate follow-up suggestions based on hint level and context."""
        
        suggestions = []
        
        if hint_level == HintLevel.SUBTLE:
            suggestions.append("If you're still stuck, ask for a more detailed hint")
            suggestions.append("Try thinking about the core vulnerability type")
        elif hint_level == HintLevel.GUIDING:
            suggestions.append("Focus on the specific technique mentioned")
            suggestions.append("Consider how the application processes your input")
        elif hint_level == HintLevel.DETAILED:
            suggestions.append("Try the approach step by step")
            suggestions.append("Pay attention to the syntax and structure")
        elif hint_level == HintLevel.EXPLICIT:
            suggestions.append("Apply the exact technique described")
            suggestions.append("Take time to understand why this works")
        
        # Add category-specific suggestions
        category_suggestions = self._get_category_follow_ups(context.challenge_category)
        suggestions.extend(category_suggestions[:2])  # Add up to 2 category suggestions
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _build_hint_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Build comprehensive hint template database."""
        return {
            'sql_injection': {
                'subtle': [
                    "Think about how SQL queries are constructed and what happens when user input is included.",
                    "Consider what special characters might change the behavior of a SQL query.",
                    "What would happen if you could modify the WHERE clause of a query?"
                ],
                'guiding': [
                    "Look for ways to manipulate the SQL query structure using operators like OR.",
                    "Try using SQL comments (-- or #) to ignore parts of the original query.",
                    "Consider using UNION statements to combine your data with the existing query."
                ],
                'detailed': [
                    "Use the OR operator to make a condition always true: ' OR '1'='1' --",
                    "Try a UNION attack to extract data: ' UNION SELECT username, password FROM users --",
                    "Use comment syntax to bypass authentication: admin'--"
                ],
                'explicit': [
                    "Enter this exact payload: ' OR '1'='1' -- to bypass authentication",
                    "For data extraction, use: ' UNION SELECT table_name FROM information_schema.tables --",
                    "To dump user data: ' UNION SELECT username, password FROM users WHERE '1'='1"
                ]
            },
            'xss': {
                'subtle': [
                    "Think about how the application displays user input on the page.",
                    "Consider what HTML tags or JavaScript might be executed by the browser.",
                    "What happens when the application doesn't sanitize user input?"
                ],
                'guiding': [
                    "Try injecting JavaScript code using <script> tags.",
                    "Look for HTML attributes that can execute JavaScript, like onclick or onerror.",
                    "Consider using different HTML elements that support event handlers."
                ],
                'detailed': [
                    "Use a basic script tag: <script>alert('XSS')</script>",
                    "Try an image with error event: <img src='x' onerror='alert(1)'>",
                    "Use SVG with onload: <svg onload='alert(1)'>"
                ],
                'explicit': [
                    "Enter this payload: <script>alert('XSS Attack')</script>",
                    "For bypassing filters try: <img src=x onerror=alert(document.cookie)>",
                    "Use this SVG payload: <svg onload=alert('XSS')></svg>"
                ]
            },
            'command_injection': {
                'subtle': [
                    "Think about how the application might be executing system commands.",
                    "Consider what characters are used to separate or chain commands in a shell.",
                    "What would happen if you could add additional commands to the existing one?"
                ],
                'guiding': [
                    "Try using command separators like ; or && to chain commands.",
                    "Look for ways to use command substitution with $() or backticks.",
                    "Consider using pipe operators | to redirect output."
                ],
                'detailed': [
                    "Use semicolon to chain commands: ; ls -la",
                    "Try command substitution: $(whoami) or `id`",
                    "Use logical operators: && cat /etc/passwd"
                ],
                'explicit': [
                    "Enter: ; cat /etc/passwd to read system files",
                    "Try: && whoami to see current user",
                    "Use: | ls -la to list directory contents"
                ]
            },
            'generic': {
                'subtle': [
                    "Think about the type of vulnerability you're trying to exploit.",
                    "Consider how the application processes and handles user input.",
                    "What security mechanisms might be in place, and how could you bypass them?"
                ],
                'guiding': [
                    "Focus on the specific attack vector for this vulnerability type.",
                    "Look for common patterns and techniques used in these attacks.",
                    "Try different approaches if your first attempt doesn't work."
                ],
                'detailed': [
                    "Use the standard techniques for this vulnerability category.",
                    "Pay attention to syntax and structure of your payload.",
                    "Consider the context where your input will be processed."
                ],
                'explicit': [
                    "Apply the exact technique described in the challenge.",
                    "Use the provided example as a template for your solution.",
                    "Follow the step-by-step approach outlined in the hint."
                ]
            }
        }
    
    def _build_learning_patterns(self) -> Dict[str, Any]:
        """Build learning pattern recognition database."""
        return {
            'hint_escalation_patterns': {
                'rapid_escalation': ['subtle', 'detailed'],
                'gradual_progression': ['subtle', 'guiding', 'detailed'],
                'help_dependent': ['guiding', 'detailed', 'explicit', 'explicit']
            },
            'success_indicators': {
                'time_improvement': 'User completing challenges faster',
                'hint_reduction': 'User requiring fewer hints over time',
                'difficulty_progression': 'User advancing to harder challenges'
            }
        }
    
    def _build_struggle_detectors(self) -> Dict[str, callable]:
        """Build struggle pattern detectors."""
        return {
            'time_struggle': lambda context: context.time_spent > 300,
            'hint_dependency': lambda context: len(context.previous_hints) > 2,
            'repeated_failures': lambda context: context.attempt_count > 3,
            'category_weakness': lambda context: context.skill_level < 0.4
        }
    
    # Helper methods for hint personalization
    def _add_independent_elements(self, hint: str, context: HintContext) -> str:
        """Add elements for independent learners."""
        prefixes = [
            "Here's a subtle clue: ",
            "Consider this approach: ",
            "Think about: "
        ]
        suffixes = [
            " Try to figure out the details yourself.",
            " Experiment with variations of this idea.",
            " Use this as a starting point for your exploration."
        ]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        return f"{prefix}{hint}{suffix}"
    
    def _add_guided_elements(self, hint: str, context: HintContext) -> str:
        """Add elements for guided learners."""
        return f"Step-by-step guidance: {hint} Follow this approach carefully and let me know if you need more detailed instructions."
    
    def _add_visual_elements(self, hint: str, context: HintContext) -> str:
        """Add elements for visual learners."""
        return f"{hint}\n\nExample structure: [Your input] → [Application processing] → [Result]"
    
    def _add_analytical_elements(self, hint: str, context: HintContext) -> str:
        """Add elements for analytical learners."""
        return f"Technical explanation: {hint}\n\nThis works because the application processes input without proper validation, allowing manipulation of the underlying system."
    
    def _add_practical_elements(self, hint: str, context: HintContext) -> str:
        """Add elements for practical learners."""
        return f"Hands-on approach: {hint}\n\nTry this technique now and observe what happens. Practice makes perfect!"
    
    def _generate_fallback_hint(self, challenge: Dict[str, Any], context: HintContext) -> GeneratedHint:
        """Generate fallback hint for error cases."""
        fallback_content = f"Consider the {context.challenge_category} vulnerability and how user input might be exploited."
        
        return GeneratedHint(
            content=fallback_content,
            level=HintLevel.GUIDING,
            reasoning="Fallback hint due to generation error",
            effectiveness_prediction=0.5,
            follow_up_suggestions=["Try researching this vulnerability type", "Ask for a more specific hint"],
            estimated_success_increase=0.2
        )
    
    def _record_hint_generation(self, context: HintContext, hint: GeneratedHint, 
                              challenge: Dict[str, Any]) -> None:
        """Record hint generation for analytics and learning."""
        try:
            if self.db:
                record = {
                    'user_id': context.user_id,
                    'challenge_id': challenge.get('id'),
                    'hint_content': hint.content,
                    'hint_level': hint.level.level_name,
                    'attempt_count': context.attempt_count,
                    'time_spent': context.time_spent,
                    'learning_style': context.user_learning_style.value,
                    'effectiveness_prediction': hint.effectiveness_prediction,
                    'timestamp': datetime.now()
                }
                
                self.db.hint_generations.insert_one(record)
                
        except Exception as e:
            logger.error(f"Error recording hint generation: {e}")
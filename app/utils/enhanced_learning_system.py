"""
Enhanced Learning Page System with Robust Error Handling and Performance Optimization
Addresses loading issues and provides seamless educational experience
"""

import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache, wraps
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentCache:
    """Content caching system for learning materials."""
    content: Any
    timestamp: datetime
    expires_at: datetime
    access_count: int = 0
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def refresh_access(self):
        self.access_count += 1

class LearningContentManager:
    """Enhanced learning content management with caching and error handling."""
    
    def __init__(self):
        self.content_cache = {}
        self.cache_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.error_cache = {}
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'error_count': 0,
            'average_response_time': 0.0,
            'total_requests': 0
        }
        self.fallback_content = self._initialize_fallback_content()
        logger.info("Enhanced Learning Content Manager initialized")
    
    def get_content_with_fallback(self, module_id: str, user_context: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Get learning content with comprehensive error handling and fallback mechanisms.
        
        Args:
            module_id: Module identifier
            user_context: User-specific context for personalization
            
        Returns:
            Tuple of (success, content_data)
        """
        start_time = time.time()
        
        try:
            self.performance_metrics['total_requests'] += 1
            
            # Try cache first
            cached_content = self._get_cached_content(module_id)
            if cached_content:
                self.performance_metrics['cache_hits'] += 1
                return True, cached_content
            
            self.performance_metrics['cache_misses'] += 1
            
            # Try primary content source
            try:
                content = self._load_primary_content(module_id, user_context)
                if content:
                    self._cache_content(module_id, content)
                    return True, content
            except Exception as primary_error:
                logger.warning(f"Primary content load failed for {module_id}: {primary_error}")
                self._record_error(module_id, 'primary_load_failure', str(primary_error))
            
            # Try database content source
            try:
                content = self._load_database_content(module_id, user_context)
                if content:
                    self._cache_content(module_id, content)
                    return True, content
            except Exception as db_error:
                logger.warning(f"Database content load failed for {module_id}: {db_error}")
                self._record_error(module_id, 'database_load_failure', str(db_error))
            
            # Use fallback content
            fallback_content = self._get_fallback_content(module_id)
            if fallback_content:
                logger.info(f"Using fallback content for module {module_id}")
                return True, fallback_content
            
            # Last resort - generic error content
            error_content = self._generate_error_content(module_id)
            return False, error_content
            
        except Exception as e:
            logger.error(f"Critical error in content loading for {module_id}: {e}")
            self.performance_metrics['error_count'] += 1
            return False, self._generate_critical_error_content(module_id, str(e))
        
        finally:
            # Update performance metrics
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time)
    
    def _get_cached_content(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get content from cache if available and not expired."""
        with self.cache_lock:
            if module_id in self.content_cache:
                cache_entry = self.content_cache[module_id]
                if not cache_entry.is_expired():
                    cache_entry.refresh_access()
                    return cache_entry.content
                else:
                    # Remove expired content
                    del self.content_cache[module_id]
        return None
    
    def _cache_content(self, module_id: str, content: Dict[str, Any]):
        """Cache content with expiration."""
        with self.cache_lock:
            expires_at = datetime.now() + timedelta(minutes=30)  # 30-minute cache
            self.content_cache[module_id] = ContentCache(
                content=content,
                timestamp=datetime.now(),
                expires_at=expires_at
            )
    
    def _load_primary_content(self, module_id: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Load content from primary source (original learning.py logic)."""
        try:
            from app.routes.learning import LEARNING_CONTENT
            
            if module_id not in LEARNING_CONTENT:
                return None
            
            content = LEARNING_CONTENT[module_id].copy()
            
            # Add user-specific enhancements if context provided
            if user_context and 'user_id' in user_context:
                try:
                    progress = self._get_user_progress_safe(user_context['user_id'], module_id)
                    if progress:
                        content['user_progress'] = progress
                except Exception as progress_error:
                    logger.warning(f"Failed to load user progress: {progress_error}")
                    content['user_progress'] = {
                        'completed_sections': [],
                        'progress_percentage': 0,
                        'time_spent': 0
                    }
            
            # Add performance optimizations
            content['loading_optimized'] = True
            content['cache_timestamp'] = datetime.now().isoformat()
            
            return content
            
        except Exception as e:
            logger.error(f"Error loading primary content: {e}")
            raise
    
    def _load_database_content(self, module_id: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Load content from database as fallback."""
        try:
            from app.models.user_model import get_db
            
            db = get_db()
            if not db:
                return None
            
            # Try to get content from database
            stored_content = db.learning_content.find_one({'module_id': module_id})
            
            if stored_content:
                # Convert MongoDB document to dict
                content = dict(stored_content)
                content.pop('_id', None)  # Remove MongoDB ObjectId
                
                # Add fallback progress if user context provided
                if user_context and 'user_id' in user_context:
                    content['user_progress'] = {
                        'completed_sections': [],
                        'progress_percentage': 0,
                        'time_spent': 0,
                        'fallback_mode': True
                    }
                
                return content
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading database content: {e}")
            raise
    
    def _get_fallback_content(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get fallback content for offline scenarios."""
        return self.fallback_content.get(module_id)
    
    def _get_user_progress_safe(self, user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Safely get user progress with error handling."""
        try:
            from app.routes.learning import get_user_learning_progress
            
            progress = get_user_learning_progress(user_id)
            if progress and module_id in progress.get('modules', {}):
                return progress['modules'][module_id]
            
            return {
                'completed_sections': [],
                'progress_percentage': 0,
                'time_spent': 0
            }
            
        except Exception as e:
            logger.warning(f"Error getting user progress: {e}")
            return None
    
    def _record_error(self, module_id: str, error_type: str, error_message: str):
        """Record error for analysis and debugging."""
        error_key = f"{module_id}_{error_type}"
        
        if error_key not in self.error_cache:
            self.error_cache[error_key] = []
        
        self.error_cache[error_key].append({
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'module_id': module_id,
            'error_type': error_type
        })
        
        # Keep only last 10 errors per type
        if len(self.error_cache[error_key]) > 10:
            self.error_cache[error_key] = self.error_cache[error_key][-10:]
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance metrics."""
        total = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_response_time']
        
        # Calculate running average
        new_avg = ((current_avg * (total - 1)) + response_time) / total
        self.performance_metrics['average_response_time'] = new_avg
    
    def _generate_error_content(self, module_id: str) -> Dict[str, Any]:
        """Generate user-friendly error content."""
        return {
            'id': module_id,
            'title': 'Content Temporarily Unavailable',
            'description': "We're experiencing technical difficulties loading this content.",
            'error_mode': True,
            'sections': [{
                'id': 'error_message',
                'title': 'Service Notice',
                'type': 'text',
                'content': (
                    'This learning module is temporarily unavailable due to a technical issue. '
                    'Our team has been notified and is working to resolve this. '
                    'Please try again in a few minutes or contact support if the problem persists.'
                ),
                'estimated_time': 1
            }],
            'user_progress': {
                'completed_sections': [],
                'progress_percentage': 0,
                'time_spent': 0
            },
            'fallback_actions': [
                'Try refreshing the page',
                'Check your internet connection',
                'Contact support if issue persists'
            ]
        }
    
    def _generate_critical_error_content(self, module_id: str, error_details: str) -> Dict[str, Any]:
        """Generate content for critical system errors."""
        return {
            'id': module_id,
            'title': 'System Error',
            'description': 'A system error occurred while loading content.',
            'critical_error': True,
            'sections': [{
                'id': 'critical_error',
                'title': 'System Error',
                'type': 'text',
                'content': (
                    'A critical system error has occurred. Our technical team has been '
                    'automatically notified. Please contact support with the timestamp '
                    f'{datetime.now().isoformat()} for assistance.'
                ),
                'estimated_time': 1
            }],
            'error_details': error_details,
            'support_info': {
                'timestamp': datetime.now().isoformat(),
                'module_id': module_id,
                'error_type': 'critical_system_error'
            }
        }
    
    def _initialize_fallback_content(self) -> Dict[str, Dict[str, Any]]:
        """Initialize offline fallback content."""
        return {
            'intro': {
                'id': 'intro',
                'title': 'Introduction to Cybersecurity (Offline)',
                'description': 'Basic cybersecurity concepts available offline',
                'offline_mode': True,
                'sections': [{
                    'id': 'offline_intro',
                    'title': 'Cybersecurity Basics',
                    'type': 'text',
                    'content': (
                        'Cybersecurity is the practice of protecting digital information, '
                        'systems, and networks from digital attacks. Key principles include '
                        'confidentiality, integrity, and availability of information.'
                    ),
                    'estimated_time': 10
                }]
            },
            'sql': {
                'id': 'sql',
                'title': 'SQL Injection (Offline)',
                'description': 'SQL injection fundamentals available offline',
                'offline_mode': True,
                'sections': [{
                    'id': 'offline_sql',
                    'title': 'SQL Injection Overview',
                    'type': 'text',
                    'content': (
                        'SQL injection occurs when untrusted data is sent to an interpreter '
                        'as part of a command or query. The attacker\'s hostile data can trick '
                        'the interpreter into executing unintended commands.'
                    ),
                    'estimated_time': 15
                }]
            },
            'resources': {
                'id': 'resources',
                'title': 'Offline Resources',
                'description': 'Resources available offline',
                'offline_mode': True,
                'sections': [{
                    'id': 'offline_resources',
                    'title': 'Offline Checklists',
                    'type': 'text',
                    'content': 'Please connect to the internet to download the latest security checklists and tools.',
                    'estimated_time': 1
                }]
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        total_requests = self.performance_metrics['total_requests']
        cache_hit_rate = (
            (self.performance_metrics['cache_hits'] / total_requests * 100) 
            if total_requests > 0 else 0
        )
        
        return {
            'total_requests': total_requests,
            'cache_hits': self.performance_metrics['cache_hits'],
            'cache_misses': self.performance_metrics['cache_misses'],
            'cache_hit_rate': round(cache_hit_rate, 2),
            'error_count': self.performance_metrics['error_count'],
            'average_response_time': round(self.performance_metrics['average_response_time'], 3),
            'cached_modules': len(self.content_cache),
            'error_types': len(self.error_cache)
        }
    
    def clear_cache(self):
        """Clear all cached content."""
        with self.cache_lock:
            self.content_cache.clear()
        logger.info("Content cache cleared")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        error_summary = {}
        
        for error_key, errors in self.error_cache.items():
            module_id, error_type = error_key.rsplit('_', 1)
            
            if module_id not in error_summary:
                error_summary[module_id] = {}
            
            error_summary[module_id][error_type] = {
                'count': len(errors),
                'latest_error': errors[-1] if errors else None,
                'first_occurrence': errors[0]['timestamp'] if errors else None
            }
        
        return error_summary

# Global content manager instance
learning_content_manager = LearningContentManager()

def get_enhanced_learning_content(module_id: str, user_context: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
    """Enhanced content retrieval with error handling and performance optimization."""
    return learning_content_manager.get_content_with_fallback(module_id, user_context)

def get_learning_performance_metrics() -> Dict[str, Any]:
    """Get learning system performance metrics."""
    return learning_content_manager.get_performance_metrics()

def clear_learning_cache():
    """Clear learning content cache."""
    learning_content_manager.clear_cache()

def get_learning_error_summary() -> Dict[str, Any]:
    """Get summary of learning system errors."""
    return learning_content_manager.get_error_summary()
"""
Database Manager for SecureTrainer
Provides robust MongoDB connectivity with fallback mechanisms and error handling.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from contextlib import contextmanager
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """
    Robust database connection manager with automatic failover,
    connection pooling, and health monitoring.
    """
    
    def __init__(self, mongo_uri: str = None, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize database connection manager.
        
        Args:
            mongo_uri: MongoDB connection URI
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.mongo_uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Connection state
        self.client: Optional[MongoClient] = None
        self.db = None
        self.is_connected = False
        self.last_health_check = None
        self.connection_errors = []
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Health check interval (5 minutes)
        self.health_check_interval = timedelta(minutes=5)
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self) -> bool:
        """Initialize database connection with retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting database connection (attempt {attempt + 1}/{self.max_retries})")
                
                # Create MongoDB client with optimized settings
                self.client = MongoClient(
                    self.mongo_uri,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=10000,         # 10 second connection timeout
                    socketTimeoutMS=20000,          # 20 second socket timeout
                    maxPoolSize=50,                 # Connection pool size
                    minPoolSize=5,                  # Minimum connections
                    maxIdleTimeMS=30000,           # Max idle time
                    waitQueueTimeoutMS=5000        # Queue timeout
                )
                
                # Test the connection
                self.client.admin.command('ping')
                
                # Get database
                db_name = self.mongo_uri.split('/')[-1] or 'securetrainer'
                self.db = self.client[db_name]
                
                # Test database access
                self.db.list_collection_names()
                
                self.is_connected = True
                self.last_health_check = datetime.now()
                
                logger.info(f"✅ Successfully connected to MongoDB: {db_name}")
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                self.connection_errors.append({
                    'timestamp': datetime.now(),
                    'error': str(e),
                    'attempt': attempt + 1
                })
                
                logger.warning(f"❌ Database connection failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    logger.info(f"⏳ Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"❌ Unexpected database error: {e}")
                self.connection_errors.append({
                    'timestamp': datetime.now(),
                    'error': f"Unexpected error: {str(e)}",
                    'attempt': attempt + 1
                })
                break
        
        self.is_connected = False
        logger.error("❌ Failed to establish database connection after all retries")
        return False
    
    def get_database(self):
        """
        Get database connection with automatic health checking.
        
        Returns:
            Database object or None if connection failed
        """
        with self._lock:
            # Check if health check is needed
            if (self.last_health_check is None or 
                datetime.now() - self.last_health_check > self.health_check_interval):
                
                if not self._health_check():
                    logger.warning("Health check failed, attempting reconnection...")
                    self._initialize_connection()
            
            return self.db if self.is_connected else None
    
    def _health_check(self) -> bool:
        """
        Perform database health check.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            if self.client and self.db:
                # Simple ping to test connection
                self.client.admin.command('ping')
                self.last_health_check = datetime.now()
                return True
                
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            self.is_connected = False
            
        return False
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute database operation with automatic retry on failure.
        
        Args:
            operation: Database operation function
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Operation result or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                db = self.get_database()
                if db is None:
                    raise ConnectionFailure("Database not available")
                
                return operation(db, *args, **kwargs)
                
            except (ConnectionFailure, ServerSelectionTimeoutError, OperationFailure) as e:
                logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Try to reconnect
                    self._initialize_connection()
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Database operation failed after {self.max_retries} attempts")
                    return None
                    
            except Exception as e:
                logger.error(f"Unexpected error in database operation: {e}")
                return None
        
        return None
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database operations.
        
        Usage:
            with db_manager.get_connection() as db:
                result = db.collection.find_one({})
        """
        db = self.get_database()
        try:
            yield db
        except Exception as e:
            logger.error(f"Error in database context: {e}")
            raise
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status and metrics.
        
        Returns:
            Dictionary with connection status information
        """
        return {
            'is_connected': self.is_connected,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'mongo_uri': self.mongo_uri.split('@')[-1] if '@' in self.mongo_uri else self.mongo_uri,  # Hide credentials
            'database_name': self.db.name if self.db is not None else None,
            'connection_errors_count': len(self.connection_errors),
            'recent_errors': self.connection_errors[-3:] if self.connection_errors else [],
            'health_check_interval': str(self.health_check_interval)
        }
    
    def force_reconnect(self) -> bool:
        """
        Force database reconnection.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        logger.info("🔄 Forcing database reconnection...")
        
        # Close existing connection
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.warning(f"Error closing existing connection: {e}")
        
        self.client = None
        self.db = None
        self.is_connected = False
        
        # Reinitialize
        return self._initialize_connection()
    
    def close(self):
        """Close database connection."""
        if self.client:
            logger.info("Closing database connection...")
            self.client.close()
            self.client = None
            self.db = None
            self.is_connected = False

# Global database manager instance
db_manager = None

def initialize_database_manager(mongo_uri: str = None) -> DatabaseConnectionManager:
    """
    Initialize global database manager.
    
    Args:
        mongo_uri: MongoDB connection URI
        
    Returns:
        DatabaseConnectionManager instance
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseConnectionManager(mongo_uri)
    return db_manager

def get_database():
    """
    Get database connection using global manager.
    
    Returns:
        Database object or None if not available
    """
    global db_manager
    if db_manager is None:
        db_manager = initialize_database_manager()
    
    return db_manager.get_database()

def execute_db_operation(operation, *args, **kwargs):
    """
    Execute database operation with retry logic.
    
    Args:
        operation: Function that takes database as first argument
        *args: Additional arguments for the operation
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Operation result or None if failed
    """
    global db_manager
    if db_manager is None:
        db_manager = initialize_database_manager()
    
    return db_manager.execute_with_retry(operation, *args, **kwargs)

# Convenience functions for common operations
def find_user_by_id(user_id):
    """Find user by ID with fallback handling."""
    def _find_operation(db, uid):
        from bson import ObjectId
        
        # Try ObjectId first
        try:
            if ObjectId.is_valid(str(uid)):
                user = db.users.find_one({'_id': ObjectId(str(uid))})
                if user:
                    return user
        except:
            pass
        
        # Try as string
        return db.users.find_one({'_id': str(uid)})
    
    return execute_db_operation(_find_operation, user_id)

def update_user_score(user_id, score_delta):
    """Update user score with error handling."""
    def _update_operation(db, uid, delta):
        from bson import ObjectId
        
        # Get current user
        user = find_user_by_id(uid)
        if not user:
            return False
        
        new_score = user.get('score', 0) + delta
        new_level = (new_score // 1000) + 1
        
        # Update user
        result = db.users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'score': new_score,
                    'level': new_level,
                    'last_activity': datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    return execute_db_operation(_update_operation, user_id, score_delta)

def get_database_status():
    """Get database connection status."""
    global db_manager
    if db_manager is None:
        return {'status': 'not_initialized'}
    
    status = db_manager.get_connection_status()
    status['status'] = 'connected' if status['is_connected'] else 'disconnected'
    return status
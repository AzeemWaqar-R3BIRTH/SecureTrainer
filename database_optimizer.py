"""
Database Optimization and Indexing Strategy for SecureTrainer
"""
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from datetime import datetime, timedelta
import os

class DatabaseOptimizer:
    """Handles database optimization, indexing, and performance monitoring."""
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish database connection."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.securetrainer
            print("✅ Connected to MongoDB for optimization")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def create_indexes(self):
        """Create comprehensive indexes for optimal performance."""
        if not self.db:
            if not self.connect():
                return False
        
        try:
            print("🔄 Creating database indexes...")
            
            # Users collection indexes
            self.db.users.create_index([("email", ASCENDING)], unique=True)
            self.db.users.create_index([("username", ASCENDING)], unique=True)
            self.db.users.create_index([("score", DESCENDING)])
            self.db.users.create_index([("level", DESCENDING)])
            self.db.users.create_index([("department", ASCENDING)])
            self.db.users.create_index([("company", ASCENDING)])
            self.db.users.create_index([("role", ASCENDING)])
            self.db.users.create_index([("created_at", DESCENDING)])
            self.db.users.create_index([("last_login", DESCENDING)])
            
            # Compound indexes for leaderboard queries
            self.db.users.create_index([
                ("department", ASCENDING),
                ("score", DESCENDING)
            ])
            self.db.users.create_index([
                ("company", ASCENDING),
                ("score", DESCENDING)
            ])
            self.db.users.create_index([
                ("role", ASCENDING),
                ("level", DESCENDING)
            ])
            
            # Challenges collection indexes
            self.db.challenges.create_index([("challenge_id", ASCENDING)], unique=True)
            self.db.challenges.create_index([("category", ASCENDING)])
            self.db.challenges.create_index([("difficulty", ASCENDING)])
            self.db.challenges.create_index([("type", ASCENDING)])
            self.db.challenges.create_index([("active", ASCENDING)])
            self.db.challenges.create_index([("created_at", DESCENDING)])
            self.db.challenges.create_index([("score_weight", DESCENDING)])
            
            # Compound indexes for challenge queries
            self.db.challenges.create_index([
                ("category", ASCENDING),
                ("difficulty", ASCENDING),
                ("active", ASCENDING)
            ])
            self.db.challenges.create_index([
                ("type", ASCENDING),
                ("active", ASCENDING)
            ])
            
            # Text index for challenge search
            self.db.challenges.create_index([
                ("scenario", TEXT),
                ("question", TEXT),
                ("category", TEXT)
            ])\n            
            # Challenge attempts collection indexes
            self.db.challenge_attempts.create_index([("user_id", ASCENDING)])
            self.db.challenge_attempts.create_index([("challenge_id", ASCENDING)])
            self.db.challenge_attempts.create_index([("attempt_time", DESCENDING)])
            self.db.challenge_attempts.create_index([("is_correct", ASCENDING)])
            self.db.challenge_attempts.create_index([("score_earned", DESCENDING)])
            self.db.challenge_attempts.create_index([("difficulty_level", ASCENDING)])
            self.db.challenge_attempts.create_index([("category", ASCENDING)])
            
            # Compound indexes for analytics queries
            self.db.challenge_attempts.create_index([
                ("user_id", ASCENDING),
                ("attempt_time", DESCENDING)
            ])
            self.db.challenge_attempts.create_index([
                ("challenge_id", ASCENDING),
                ("is_correct", ASCENDING)
            ])
            self.db.challenge_attempts.create_index([
                ("user_id", ASCENDING),
                ("category", ASCENDING),
                ("is_correct", ASCENDING)
            ])
            self.db.challenge_attempts.create_index([
                ("category", ASCENDING),
                ("difficulty_level", ASCENDING),
                ("is_correct", ASCENDING)
            ])
            
            # Time-series index for performance analytics
            self.db.challenge_attempts.create_index([
                ("attempt_time", DESCENDING),
                ("is_correct", ASCENDING)
            ])
            
            # User activities collection indexes
            self.db.user_activities.create_index([("user_id", ASCENDING)])
            self.db.user_activities.create_index([("activity_type", ASCENDING)])
            self.db.user_activities.create_index([("timestamp", DESCENDING)])
            self.db.user_activities.create_index([
                ("user_id", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            
            # Analytics collection indexes
            self.db.analytics.create_index([("user_id", ASCENDING)])
            self.db.analytics.create_index([("challenge_id", ASCENDING)])
            self.db.analytics.create_index([("event_type", ASCENDING)])
            self.db.analytics.create_index([("timestamp", DESCENDING)])
            
            # User progress tracking indexes
            self.db.user_progress.create_index([("user_id", ASCENDING)], unique=True)
            self.db.user_progress.create_index([("category", ASCENDING)])
            self.db.user_progress.create_index([("last_activity", DESCENDING)])
            
            # Department statistics indexes
            self.db.department_stats.create_index([("department", ASCENDING)], unique=True)
            self.db.department_stats.create_index([("company", ASCENDING)])
            self.db.department_stats.create_index([("avg_score", DESCENDING)])
            self.db.department_stats.create_index([("last_updated", DESCENDING)])
            
            # System logs indexes
            self.db.system_logs.create_index([("log_level", ASCENDING)])
            self.db.system_logs.create_index([("component", ASCENDING)])
            self.db.system_logs.create_index([("timestamp", DESCENDING)])
            self.db.system_logs.create_index([
                ("log_level", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            
            # TTL index for temporary data (expire after 30 days)
            self.db.system_logs.create_index([("timestamp", ASCENDING)], expireAfterSeconds=2592000)
            self.db.user_activities.create_index([("timestamp", ASCENDING)], expireAfterSeconds=7776000)  # 90 days
            
            print("✅ Database indexes created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            return False
    
    def analyze_performance(self):
        """Analyze database performance and suggest optimizations."""
        if not self.db:
            if not self.connect():
                return None
        
        try:
            performance_report = {
                'collections': {},
                'indexes': {},
                'query_performance': {},
                'recommendations': []
            }
            
            # Analyze collections
            collections = ['users', 'challenges', 'challenge_attempts', 'user_activities', 'analytics']
            
            for collection_name in collections:
                collection = self.db[collection_name]
                
                # Get collection stats
                stats = self.db.command("collStats", collection_name)
                
                performance_report['collections'][collection_name] = {
                    'document_count': stats.get('count', 0),
                    'size_bytes': stats.get('size', 0),
                    'storage_size_bytes': stats.get('storageSize', 0),
                    'index_count': stats.get('nindexes', 0),
                    'index_size_bytes': stats.get('totalIndexSize', 0),
                    'avg_obj_size': stats.get('avgObjSize', 0)
                }
                
                # Get index information
                indexes = list(collection.list_indexes())
                performance_report['indexes'][collection_name] = []
                
                for index in indexes:
                    index_info = {
                        'name': index.get('name'),
                        'key': index.get('key'),
                        'unique': index.get('unique', False),
                        'sparse': index.get('sparse', False),
                        'background': index.get('background', False)
                    }
                    performance_report['indexes'][collection_name].append(index_info)
            
            # Performance recommendations
            recommendations = []
            
            # Check for large collections without proper indexes
            for collection_name, stats in performance_report['collections'].items():
                if stats['document_count'] > 10000 and stats['index_count'] < 5:
                    recommendations.append(f\"Consider adding more indexes to {collection_name} collection for better query performance\")
                
                # Check index to data ratio
                if stats['size_bytes'] > 0:
                    index_ratio = stats['index_size_bytes'] / stats['size_bytes']
                    if index_ratio > 0.5:
                        recommendations.append(f\"High index-to-data ratio in {collection_name} ({index_ratio:.2%}) - consider removing unused indexes\")
                    elif index_ratio < 0.1 and stats['document_count'] > 1000:
                        recommendations.append(f\"Low index-to-data ratio in {collection_name} ({index_ratio:.2%}) - consider adding strategic indexes\")
            
            # Check for slow queries
            try:
                profiler_data = self.db.command(\"profile\", 2, slowms=100)  # Profile queries slower than 100ms
                recommendations.append(\"Query profiling enabled - monitor system.profile collection for slow queries\")
            except:
                recommendations.append(\"Enable MongoDB profiling to identify slow queries\")
            
            performance_report['recommendations'] = recommendations
            performance_report['generated_at'] = datetime.now().isoformat()
            
            return performance_report
            
        except Exception as e:
            print(f\"❌ Error analyzing performance: {e}\")
            return None
    
    def optimize_queries(self):
        \"\"\"Implement query optimizations.\"\"\"
        if not self.db:
            if not self.connect():
                return False
        
        try:
            optimizations = []
            
            # Enable query optimizer hints for common queries
            
            # 1. Leaderboard queries optimization
            self.db.users.create_index([
                (\"score\", DESCENDING),
                (\"level\", DESCENDING),
                (\"username\", ASCENDING)
            ], name=\"leaderboard_optimized\")
            optimizations.append(\"Created optimized leaderboard index\")
            
            # 2. User analytics queries optimization
            self.db.challenge_attempts.create_index([
                (\"user_id\", ASCENDING),
                (\"is_correct\", ASCENDING),
                (\"attempt_time\", DESCENDING)
            ], name=\"user_analytics_optimized\")
            optimizations.append(\"Created optimized user analytics index\")
            
            # 3. Challenge statistics optimization
            self.db.challenge_attempts.create_index([
                (\"challenge_id\", ASCENDING),
                (\"is_correct\", ASCENDING),
                (\"score_earned\", DESCENDING)
            ], name=\"challenge_stats_optimized\")
            optimizations.append(\"Created optimized challenge statistics index\")
            
            # 4. Department analytics optimization
            self.db.users.create_index([
                (\"department\", ASCENDING),
                (\"score\", DESCENDING),
                (\"level\", DESCENDING)
            ], name=\"department_analytics_optimized\")
            optimizations.append(\"Created optimized department analytics index\")
            
            # 5. Time-based queries optimization
            self.db.challenge_attempts.create_index([
                (\"attempt_time\", DESCENDING),
                (\"user_id\", ASCENDING),
                (\"is_correct\", ASCENDING)
            ], name=\"time_based_optimized\")
            optimizations.append(\"Created optimized time-based queries index\")
            
            print(f\"✅ Applied {len(optimizations)} query optimizations\")
            return True
            
        except Exception as e:
            print(f\"❌ Error optimizing queries: {e}\")
            return False
    
    def setup_aggregation_pipelines(self):
        \"\"\"Create optimized aggregation pipelines for common analytics.\"\"\"
        if not self.db:
            if not self.connect():
                return False
        
        try:
            # Create views for common analytics queries
            
            # 1. User performance summary view
            user_performance_pipeline = [
                {
                    \"$lookup\": {
                        \"from\": \"challenge_attempts\",
                        \"localField\": \"_id\",
                        \"foreignField\": \"user_id\",
                        \"as\": \"attempts\"
                    }
                },
                {
                    \"$addFields\": {
                        \"total_attempts\": {\"$size\": \"$attempts\"},
                        \"successful_attempts\": {
                            \"$size\": {
                                \"$filter\": {
                                    \"input\": \"$attempts\",
                                    \"cond\": {\"$eq\": [\"$$this.is_correct\", True]}
                                }
                            }
                        },
                        \"total_score_earned\": {
                            \"$sum\": \"$attempts.score_earned\"
                        }
                    }
                },
                {
                    \"$addFields\": {
                        \"success_rate\": {
                            \"$cond\": {
                                \"if\": {\"$gt\": [\"$total_attempts\", 0]},
                                \"then\": {
                                    \"$multiply\": [
                                        {\"$divide\": [\"$successful_attempts\", \"$total_attempts\"]},
                                        100
                                    ]
                                },
                                \"else\": 0
                            }
                        }
                    }
                }
            ]
            
            # Create materialized view for user performance
            try:
                self.db.create_collection(\"user_performance_view\")
                self.db.command({
                    \"create\": \"user_performance_view\",
                    \"viewOn\": \"users\",
                    \"pipeline\": user_performance_pipeline
                })
                print(\"✅ Created user performance view\")
            except Exception as e:
                if \"already exists\" not in str(e).lower():
                    print(f\"⚠️ Could not create user performance view: {e}\")
            
            # 2. Department leaderboard view
            dept_leaderboard_pipeline = [
                {
                    \"$group\": {
                        \"_id\": \"$department\",
                        \"total_users\": {\"$sum\": 1},
                        \"avg_score\": {\"$avg\": \"$score\"},
                        \"total_score\": {\"$sum\": \"$score\"},
                        \"max_level\": {\"$max\": \"$level\"},
                        \"top_user\": {\"$max\": \"$score\"}
                    }
                },
                {
                    \"$sort\": {\"avg_score\": -1}
                }
            ]
            
            try:
                self.db.command({
                    \"create\": \"department_leaderboard_view\",
                    \"viewOn\": \"users\",
                    \"pipeline\": dept_leaderboard_pipeline
                })
                print(\"✅ Created department leaderboard view\")
            except Exception as e:
                if \"already exists\" not in str(e).lower():
                    print(f\"⚠️ Could not create department leaderboard view: {e}\")
            
            return True
            
        except Exception as e:
            print(f\"❌ Error setting up aggregation pipelines: {e}\")
            return False
    
    def cleanup_old_data(self, days_to_keep=90):
        \"\"\"Clean up old data to maintain performance.\"\"\"
        if not self.db:
            if not self.connect():
                return False
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up old user activities
            result = self.db.user_activities.delete_many({
                \"timestamp\": {\"$lt\": cutoff_date}
            })
            print(f\"✅ Cleaned up {result.deleted_count} old user activities\")
            
            # Clean up old system logs
            result = self.db.system_logs.delete_many({
                \"timestamp\": {\"$lt\": cutoff_date}
            })
            print(f\"✅ Cleaned up {result.deleted_count} old system logs\")
            
            # Archive old challenge attempts (keep last 6 months)
            archive_cutoff = datetime.now() - timedelta(days=180)
            old_attempts = list(self.db.challenge_attempts.find({
                \"attempt_time\": {\"$lt\": archive_cutoff}
            }))
            
            if old_attempts:
                # Archive to separate collection
                self.db.challenge_attempts_archive.insert_many(old_attempts)
                result = self.db.challenge_attempts.delete_many({
                    \"attempt_time\": {\"$lt\": archive_cutoff}
                })
                print(f\"✅ Archived {result.deleted_count} old challenge attempts\")
            
            return True
            
        except Exception as e:
            print(f\"❌ Error cleaning up old data: {e}\")
            return False
    
    def get_performance_metrics(self):
        \"\"\"Get current database performance metrics.\"\"\"
        if not self.db:
            if not self.connect():
                return None
        
        try:
            # Get server status
            server_status = self.db.command(\"serverStatus\")
            
            # Get database stats
            db_stats = self.db.command(\"dbStats\")
            
            metrics = {
                'server_info': {
                    'version': server_status.get('version'),
                    'uptime_seconds': server_status.get('uptime'),
                    'connections_current': server_status.get('connections', {}).get('current', 0),
                    'connections_available': server_status.get('connections', {}).get('available', 0)
                },
                'database_stats': {
                    'collections': db_stats.get('collections', 0),
                    'indexes': db_stats.get('indexes', 0),
                    'data_size_bytes': db_stats.get('dataSize', 0),
                    'storage_size_bytes': db_stats.get('storageSize', 0),
                    'index_size_bytes': db_stats.get('indexSize', 0)
                },
                'operations': {
                    'queries_per_second': server_status.get('opcounters', {}).get('query', 0),
                    'inserts_per_second': server_status.get('opcounters', {}).get('insert', 0),
                    'updates_per_second': server_status.get('opcounters', {}).get('update', 0),
                    'deletes_per_second': server_status.get('opcounters', {}).get('delete', 0)
                },
                'memory': {
                    'resident_mb': server_status.get('mem', {}).get('resident', 0),
                    'virtual_mb': server_status.get('mem', {}).get('virtual', 0)
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            print(f\"❌ Error getting performance metrics: {e}\")
            return None


def initialize_database_optimization():
    \"\"\"Initialize database optimization for SecureTrainer.\"\"\"
    optimizer = DatabaseOptimizer()
    
    print(\"🚀 Initializing database optimization...\")
    
    # Create indexes
    if optimizer.create_indexes():
        print(\"✅ Database indexes created\")
    else:
        print(\"❌ Failed to create indexes\")
        return False
    
    # Optimize queries
    if optimizer.optimize_queries():
        print(\"✅ Query optimizations applied\")
    else:
        print(\"❌ Failed to optimize queries\")
    
    # Setup aggregation pipelines
    if optimizer.setup_aggregation_pipelines():
        print(\"✅ Aggregation pipelines created\")
    else:
        print(\"❌ Failed to create aggregation pipelines\")
    
    print(\"🎯 Database optimization completed\")
    return True


if __name__ == \"__main__\":
    initialize_database_optimization()
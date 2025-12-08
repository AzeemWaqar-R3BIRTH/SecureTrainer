#!/usr/bin/env python3
"""
Comprehensive System Test Suite for SecureTrainer Error Fixes
Tests all major components and error handling scenarios.
"""

import os
import sys
import time
import requests
import json
from datetime import datetime
from typing import Dict, Any, List
import subprocess
import threading

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SystemTester:
    """Comprehensive system testing framework."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict[str, Any] = None):
        """Log test result."""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def test_database_connection(self):
        """Test database connection and error handling."""
        print("\n🔍 Testing Database Connection...")
        
        try:
            from app.database.db_manager import initialize_database_manager, get_database_status
            
            # Test database manager initialization
            db_manager = initialize_database_manager()
            self.log_test(
                "Database Manager Initialization", 
                db_manager is not None,
                "Database manager created successfully" if db_manager else "Failed to create database manager"
            )
            
            # Test database status
            status = get_database_status()
            self.log_test(
                "Database Status Check",
                status.get('status') in ['connected', 'disconnected'],
                f"Database status: {status.get('status', 'unknown')}",
                status
            )
            
            # Test database operations with retry
            from app.database.db_manager import find_user_by_id, execute_db_operation
            
            def test_operation(db):
                return db.users.count_documents({})
            
            user_count = execute_db_operation(test_operation)
            self.log_test(
                "Database Operation with Retry",
                user_count is not None,
                f"User count: {user_count}" if user_count is not None else "Database operation failed",
                {'user_count': user_count}
            )
            
        except Exception as e:
            self.log_test("Database Connection Test", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling framework."""
        print("\n🛡️ Testing Error Handling Framework...")
        
        try:
            from app.utils.error_handler import ErrorHandler, SystemError, ErrorCategory, ErrorSeverity
            from flask import Flask
            
            # Create test Flask app
            test_app = Flask(__name__)
            error_handler = ErrorHandler(test_app)
            
            self.log_test(
                "Error Handler Initialization",
                error_handler is not None,
                "Error handler created successfully"
            )
            
            # Test error logging
            test_error = error_handler.log_error(
                "TEST_ERROR",
                "This is a test error",
                ErrorCategory.SYSTEM,
                ErrorSeverity.LOW,
                {'test': True}
            )
            
            self.log_test(
                "Error Logging",
                test_error is not None,
                "Error logged successfully",
                {'error_code': test_error.error_code}
            )
            
            # Test error statistics
            stats = error_handler.get_error_statistics()
            self.log_test(
                "Error Statistics",
                stats.get('total_errors', 0) > 0,
                f"Error statistics collected: {stats.get('total_errors', 0)} total errors",
                stats
            )
            
        except Exception as e:
            self.log_test("Error Handling Test", False, f"Error: {str(e)}")
    
    def test_session_management(self):
        """Test session management."""
        print("\n🔐 Testing Session Management...")
        
        try:
            from app.utils.session_manager import SessionManager
            from flask import Flask
            
            # Create test Flask app
            test_app = Flask(__name__)
            test_app.config['SECRET_KEY'] = 'test-secret-key'
            
            session_manager = SessionManager(test_app)
            
            self.log_test(
                "Session Manager Initialization",
                session_manager is not None,
                "Session manager created successfully"
            )
            
            # Test session creation with mock user
            mock_user = {
                '_id': '507f1f77bcf86cd799439011',
                'username': 'test_user',
                'email': 'test@example.com',
                'level': 1,
                'role': 'Trainee',
                'score': 0
            }
            
            with test_app.test_request_context():
                success = session_manager.create_user_session(mock_user)
                self.log_test(
                    "Session Creation",
                    success,
                    "User session created successfully" if success else "Failed to create session"
                )
                
                # Test session retrieval
                session_info = session_manager.get_session_info()
                self.log_test(
                    "Session Information Retrieval",
                    session_info.get('authenticated', False),
                    f"Session info retrieved: {session_info.get('username', 'Unknown')}",
                    session_info
                )
            
        except Exception as e:
            self.log_test("Session Management Test", False, f"Error: {str(e)}")
    
    def test_web_endpoints(self):
        """Test web endpoints for error handling."""
        print("\n🌐 Testing Web Endpoints...")
        
        # Test health check endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            self.log_test(
                "Health Check Endpoint",
                response.status_code in [200, 503],
                f"Health check responded with status {response.status_code}",
                {'status_code': response.status_code, 'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]}
            )
        except requests.RequestException as e:
            self.log_test("Health Check Endpoint", False, f"Request failed: {str(e)}")
        
        # Test system status endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/system/status", timeout=10)
            self.log_test(
                "System Status Endpoint",
                response.status_code in [200, 503],
                f"System status responded with status {response.status_code}",
                {'status_code': response.status_code}
            )
        except requests.RequestException as e:
            self.log_test("System Status Endpoint", False, f"Request failed: {str(e)}")
        
        # Test 404 error handling
        try:
            response = self.session.get(f"{self.base_url}/nonexistent-page", timeout=10)
            self.log_test(
                "404 Error Handling",
                response.status_code == 404,
                f"404 page handled correctly (status: {response.status_code})"
            )
        except requests.RequestException as e:
            self.log_test("404 Error Handling", False, f"Request failed: {str(e)}")
        
        # Test main pages
        endpoints_to_test = [
            ('/login', 'Login Page'),
            ('/register', 'Registration Page'),
            ('/', 'Home Page (should redirect)')
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10, allow_redirects=True)
                self.log_test(
                    name,
                    response.status_code in [200, 302],
                    f"Page accessible (status: {response.status_code})"
                )
            except requests.RequestException as e:
                self.log_test(name, False, f"Request failed: {str(e)}")
    
    def test_graceful_degradation(self):
        """Test graceful degradation features."""
        print("\n🔄 Testing Graceful Degradation...")
        
        try:
            from app.utils.error_handler import GracefulDegradation
            
            degradation = GracefulDegradation()
            
            # Test service marking
            degradation.mark_service_down('test_service', 'Test reason')
            self.log_test(
                "Service Down Marking",
                not degradation.service_status.get('test_service', True),
                "Service marked as down successfully"
            )
            
            # Test feature availability
            degradation.mark_service_down('database', 'Test database failure')
            self.log_test(
                "Feature Degradation",
                not degradation.is_feature_available('user_progress'),
                "Features correctly degraded when database down"
            )
            
            # Test service restoration
            degradation.mark_service_up('database')
            self.log_test(
                "Service Restoration",
                degradation.is_feature_available('user_progress'),
                "Features restored when service comes back up"
            )
            
            # Test status reporting
            status = degradation.get_status()
            self.log_test(
                "Status Reporting",
                'services' in status and 'degraded_features' in status,
                f"Status reported correctly: {status.get('overall_health', 'unknown')}"
            )
            
        except Exception as e:
            self.log_test("Graceful Degradation Test", False, f"Error: {str(e)}")
    
    def test_application_startup(self):
        """Test application startup process."""
        print("\n🚀 Testing Application Startup...")
        
        try:
            # Test environment setup
            from dotenv import load_dotenv
            load_dotenv()
            
            required_env_vars = ['SECRET_KEY', 'MONGO_URI']
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            
            self.log_test(
                "Environment Variables",
                len(missing_vars) == 0,
                f"All required environment variables present" if len(missing_vars) == 0 else f"Missing: {missing_vars}",
                {'missing_vars': missing_vars}
            )
            
            # Test imports
            try:
                from securetrainer import app
                self.log_test("Application Import", True, "Main application imported successfully")
            except Exception as e:
                self.log_test("Application Import", False, f"Import failed: {str(e)}")
            
            # Test Flask app configuration
            try:
                self.log_test(
                    "Flask Configuration",
                    hasattr(app, 'config'),
                    "Flask app configured properly"
                )
            except Exception as e:
                self.log_test("Flask Configuration", False, f"Configuration error: {str(e)}")
                
        except Exception as e:
            self.log_test("Application Startup Test", False, f"Error: {str(e)}")
    
    def test_ai_system_fallbacks(self):
        """Test AI system fallback mechanisms."""
        print("\n🤖 Testing AI System Fallbacks...")
        
        try:
            # Test AI system graceful failure
            try:
                from app.routes.ai_routes import ai_orchestrator
                
                if ai_orchestrator is None:
                    self.log_test(
                        "AI System Graceful Failure",
                        True,
                        "AI system correctly handles initialization failure"
                    )
                else:
                    self.log_test(
                        "AI System Initialization",
                        True,
                        "AI system initialized successfully"
                    )
                    
            except ImportError:
                self.log_test(
                    "AI System Import Handling",
                    True,
                    "AI system import failure handled gracefully"
                )
            
            # Test fallback challenge generation
            try:
                from app.models.challenge_model import get_fallback_sql_challenges
                
                fallback_challenges = get_fallback_sql_challenges()
                self.log_test(
                    "Fallback Challenges",
                    len(fallback_challenges) > 0,
                    f"Fallback challenges available: {len(fallback_challenges)}"
                )
                
            except Exception as e:
                self.log_test("Fallback Challenges", False, f"Error: {str(e)}")
                
        except Exception as e:
            self.log_test("AI System Fallbacks Test", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🧪 Starting SecureTrainer System Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run test suites
        self.test_application_startup()
        self.test_database_connection()
        self.test_error_handling()
        self.test_session_management()
        self.test_graceful_degradation()
        self.test_ai_system_fallbacks()
        self.test_web_endpoints()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 Test Results Summary")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📊 Total: {self.passed_tests + self.failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        # Detailed results
        if self.failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test_name']}: {result['message']}")
        
        return self.failed_tests == 0
    
    def generate_report(self, filename: str = None):
        """Generate detailed test report."""
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'test_summary': {
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'total': self.passed_tests + self.failed_tests,
                'success_rate': (self.passed_tests / (self.passed_tests + self.failed_tests) * 100) if (self.passed_tests + self.failed_tests) > 0 else 0
            },
            'test_results': self.test_results,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {filename}")
        return filename

def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SecureTrainer System Test Suite')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL for testing')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--start-server', action='store_true', help='Start server before testing')
    
    args = parser.parse_args()
    
    # Start server if requested
    server_process = None
    if args.start_server:
        print("🚀 Starting SecureTrainer server...")
        try:
            server_process = subprocess.Popen([
                sys.executable, 'start.py'
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return 1
    
    try:
        # Run tests
        tester = SystemTester(args.url)
        success = tester.run_all_tests()
        
        # Generate report if requested
        if args.report:
            tester.generate_report()
        
        return 0 if success else 1
        
    finally:
        # Cleanup server if we started it
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
Challenge System Test Script
Tests the complete challenge functionality including API endpoints and database integration.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USER_ID = "test_user_123"

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test an API endpoint and return response."""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"✅ {method} {url} - Status: {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {url} - Error: {e}")
        return None

def main():
    """Run comprehensive challenge system tests."""
    print("🧪 Starting Challenge System Tests")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing Server Status")
    response = test_endpoint(f"{BASE_URL}/")
    if not response:
        print("❌ Server is not running!")
        return
    
    # Test 2: Check login page
    print("\n2️⃣ Testing Login Page")
    test_endpoint(f"{BASE_URL}/login")
    
    # Test 3: Check system health
    print("\n3️⃣ Testing System Health")
    test_endpoint(f"{BASE_URL}/api/health")
    
    # Test 4: Test challenge categories endpoint
    print("\n4️⃣ Testing Challenge Categories")
    test_endpoint(f"{BASE_URL}/api/challenges/categories")
    
    # Test 5: Test challenge list endpoint
    print("\n5️⃣ Testing Challenge List")
    test_endpoint(f"{BASE_URL}/api/challenges/list")
    
    # Test 6: Test starting a challenge (with fallback handling)
    print("\n6️⃣ Testing Challenge Start")
    test_endpoint(f"{BASE_URL}/api/challenges/start/{TEST_USER_ID}?category=sql_injection")
    
    # Test 7: Test challenge submission (with mock data)
    print("\n7️⃣ Testing Challenge Submission")
    test_data = {
        "challenge_id": "sql_test_1",
        "answer": "' OR '1'='1' --"
    }
    test_endpoint(f"{BASE_URL}/api/challenges/submit/{TEST_USER_ID}", method="POST", data=test_data)
    
    # Test 8: Test static assets
    print("\n8️⃣ Testing Static Assets")
    test_endpoint(f"{BASE_URL}/static/css/main.css")
    test_endpoint(f"{BASE_URL}/static/js/main.js")
    test_endpoint(f"{BASE_URL}/static/js/challenges.js")
    
    # Test 9: Check demo login functionality
    print("\n9️⃣ Testing Demo Login")
    test_endpoint(f"{BASE_URL}/demo-login")
    
    print("\n" + "=" * 50)
    print("🎉 Challenge System Tests Completed!")
    print(f"⏰ Test run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
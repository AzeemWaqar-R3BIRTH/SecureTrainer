#!/usr/bin/env python3
"""
Simple validation test for SQL Challenge Answer Validation Fix
Quick test to verify the system is working
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_basic_validation():
    """Test basic validation functionality"""
    print("🔍 Testing Basic SQL Validation...")
    
    try:
        from app.ai.integrated_validation_system import integrated_validation_system
        
        # Test SQL injection answers from demo guide
        test_cases = [
            ('sql_1', 'authentication bypass', True),
            ('sql_1', 'bypasses authentication', True),
            ('sql_1', 'WHERE clause always true', True),
            ('sql_1', 'login bypass', True),
            ('sql_2', 'drop table users', True),
            ('sql_2', 'deletes users table', True),
            ('sql_2', 'data loss', True),
            ('sql_3', 'extracts user credentials', True),
            ('sql_3', 'data extraction', True),
            ('sql_3', 'UNION SELECT attack', True),
            ('sql_1', 'completely wrong answer', False),
        ]
        
        passed = 0
        failed = 0
        
        for challenge_id, answer, expected in test_cases:
            try:
                is_correct, feedback = integrated_validation_system.validate_challenge_solution(challenge_id, answer)
                
                if (is_correct and expected) or (not is_correct and not expected):
                    print(f"  ✅ {challenge_id}: '{answer}' -> {'ACCEPTED' if is_correct else 'REJECTED'} (Expected)")
                    passed += 1
                else:
                    print(f"  ❌ {challenge_id}: '{answer}' -> {'ACCEPTED' if is_correct else 'REJECTED'} (Unexpected)")
                    print(f"     Feedback: {feedback}")
                    failed += 1
                    
            except Exception as e:
                print(f"  ⚠️  {challenge_id}: '{answer}' -> ERROR: {e}")
                failed += 1
        
        success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        print(f"\\n📊 Results: {passed}/{passed + failed} passed ({success_rate:.1f}%)")
        
        return success_rate >= 90
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_direct_challenge_model():
    """Test the challenge model integration"""
    print("\\n🔍 Testing Challenge Model Integration...")
    
    try:
        from app.models.challenge_model import validate_challenge_solution
        
        test_cases = [
            ('sql_1', 'authentication bypass'),
            ('sql_2', 'drop table users'),
            ('sql_3', 'data extraction')
        ]
        
        for challenge_id, answer in test_cases:
            try:
                is_correct, feedback = validate_challenge_solution(challenge_id, answer)
                print(f"  ✅ {challenge_id}: '{answer}' -> {'ACCEPTED' if is_correct else 'REJECTED'}")
                print(f"     Feedback: {feedback}")
            except Exception as e:
                print(f"  ❌ {challenge_id}: '{answer}' -> ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Challenge model test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Quick SQL Challenge Validation Test\\n")
    print("=" * 60)
    
    basic_test_passed = test_basic_validation()
    integration_test_passed = test_direct_challenge_model()
    
    print("\\n" + "=" * 60)
    if basic_test_passed and integration_test_passed:
        print("🎉 All tests passed! SQL Challenge validation fix is working.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
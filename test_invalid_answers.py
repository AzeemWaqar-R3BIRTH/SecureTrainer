#!/usr/bin/env python3
"""
Test script to verify that invalid answers like "I don't know" are correctly rejected
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_invalid_answers():
    """Test that invalid/generic answers are rejected"""
    print("🧪 Testing Invalid Answer Rejection\n")
    print("="*60)
    
    try:
        from app.ai.comprehensive_validation_engine import comprehensive_validator
        
        # Test cases: invalid answers that should be rejected
        test_cases = [
            ("sql_1", "I don't know"),
            ("sql_1", "idk"),
            ("sql_2", "I dunno"),
            ("sql_3", "no idea"),
            ("xss_1", "not sure"),
            ("cmd_1", "unknown"),
            ("auth_1", "nothing"),
            ("sql_1", "help"),
            ("sql_2", "what"),
            ("sql_3", "skip"),
            ("sql_1", "test"),
            ("sql_2", "random"),
            ("sql_3", "asdf"),
            ("sql_1", "123"),
            ("sql_2", "a"),  # Too short
            ("sql_3", "ab"),  # Too short
            ("sql_1", "aaaa"),  # Repeated chars
        ]
        
        print("\n📋 Testing Invalid Answers (should all be rejected):\n")
        
        passed = 0
        failed = 0
        
        for challenge_id, invalid_answer in test_cases:
            result = comprehensive_validator.validate_answer(challenge_id, invalid_answer, None)
            
            status = "✅ PASS" if not result.is_correct else "❌ FAIL"
            if not result.is_correct:
                passed += 1
            else:
                failed += 1
                
            print(f"  {status} - Challenge: {challenge_id:8s} | Answer: '{invalid_answer:20s}' | "
                  f"Rejected: {not result.is_correct} | Tier: {result.tier_used.name}")
        
        print("\n" + "="*60)
        print(f"\n📊 Results: {passed}/{len(test_cases)} correctly rejected")
        
        if failed > 0:
            print(f"\n⚠️  WARNING: {failed} invalid answer(s) were incorrectly accepted!")
            print("This indicates the validation is too permissive.")
        else:
            print("\n✅ SUCCESS: All invalid answers were correctly rejected!")
            
        # Now test that valid answers are still accepted
        print("\n" + "="*60)
        print("\n📋 Testing Valid Answers (should all be accepted):\n")
        
        valid_test_cases = [
            ("sql_1", "authentication bypass"),
            ("sql_2", "drop table users"),
            ("sql_3", "extracts user credentials"),
            ("xss_1", "executes JavaScript"),
            ("cmd_1", "ping and list directory"),
            ("auth_1", "password"),
        ]
        
        valid_passed = 0
        valid_failed = 0
        
        for challenge_id, valid_answer in valid_test_cases:
            result = comprehensive_validator.validate_answer(challenge_id, valid_answer, None)
            
            status = "✅ PASS" if result.is_correct else "❌ FAIL"
            if result.is_correct:
                valid_passed += 1
            else:
                valid_failed += 1
                
            print(f"  {status} - Challenge: {challenge_id:8s} | Answer: '{valid_answer:30s}' | "
                  f"Accepted: {result.is_correct} | Tier: {result.tier_used.name} | "
                  f"Confidence: {result.confidence:.2f}")
        
        print("\n" + "="*60)
        print(f"\n📊 Results: {valid_passed}/{len(valid_test_cases)} correctly accepted")
        
        if valid_failed > 0:
            print(f"\n⚠️  WARNING: {valid_failed} valid answer(s) were incorrectly rejected!")
            print("This indicates the validation is too strict.")
        else:
            print("\n✅ SUCCESS: All valid answers were correctly accepted!")
        
        # Final summary
        print("\n" + "="*60)
        print("\n🎯 FINAL SUMMARY:")
        print(f"  Invalid Answers: {passed}/{len(test_cases)} correctly rejected")
        print(f"  Valid Answers:   {valid_passed}/{len(valid_test_cases)} correctly accepted")
        
        if failed == 0 and valid_failed == 0:
            print("\n🌟 PERFECT! Validation system is working correctly!")
            return True
        else:
            print("\n⚠️  Issues detected. Please review validation logic.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_invalid_answers()
    sys.exit(0 if success else 1)

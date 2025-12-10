#!/usr/bin/env python3
"""
Test script to verify that hint answers for SQL challenges are correctly validated
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_hint_answers():
    """Test that hint answers for SQL challenges are accepted"""
    print("🧪 Testing SQL Challenge Hint Answer Validation\n")
    print("="*60)
    
    try:
        from app.ai.comprehensive_validation_engine import comprehensive_validator
        
        # Test cases: (challenge_id, hint_answer)
        test_cases = [
            ('sql_3', "This payload uses UNION to combine results and extract user credentials."),
            ('sql_4', "Time-based Blind SQL Injection uses time delays to infer database information."),
            ('sql_5', "Boolean-based Blind SQL Injection extracts data by asking true/false questions."),
            ('cmd_1', "This payload would ping localhost and then list directory contents."),
            ('csrf_1', "CSRF allows attackers to perform actions on behalf of authenticated users."),
            ('csrf_2', "CSRF tokens are unique values that verify requests come from legitimate sources."),
            ('csrf_3', "This payload uses an image tag to force the browser to make a GET request to a sensitive endpoint."),
            ('csrf_4', "This payload creates an auto-submitting form that performs unauthorized POST requests."),
            ('csrf_5', "CSRF can bypass Content-Type restrictions if the backend accepts multiple formats or has lenient parsing."),
            ('csrf_6', "SameSite cookie attribute prevents CSRF by restricting cookie transmission on cross-site requests."),
            ('csrf_7', "WebSocket CSRF occurs when servers accept connections without validating the Origin header."),
            ('csrf_8', "CSRF file upload attacks allow attackers to upload malicious files on behalf of authenticated users."),
            ('csrf_9', "Logout CSRF forces users to logout by triggering the logout endpoint via GET requests."),
            ('csrf_10', "Custom headers provide CSRF protection because browsers prevent cross-origin custom headers without CORS.")
        ]
        
        results = []
        
        for challenge_id, hint_answer in test_cases:
            print(f"\n📝 Testing {challenge_id.upper()}: '{hint_answer}'\n")
            
            # Validate the hint answer
            result = comprehensive_validator.validate_answer(challenge_id, hint_answer, None)
            
            print("="*60)
            print(f"\n📊 VALIDATION RESULT for {challenge_id.upper()}:")
            print(f"  ✅ Is Correct: {result.is_correct}")
            print(f"  📈 Confidence: {result.confidence:.2%}")
            print(f"  🎯 Tier Used: {result.tier_used.name}")
            print(f"  💬 Feedback: {result.feedback}")
            if result.matched_answer:
                print(f"  🔗 Matched Answer: '{result.matched_answer}'")
            print("="*60)
            
            results.append((challenge_id, result.is_correct))
            
            if result.is_correct:
                print(f"\n🎉 SUCCESS! {challenge_id.upper()} hint answer is correctly validated!")
            else:
                print(f"\n❌ FAILURE! {challenge_id.upper()} hint answer is still being rejected!")
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY:")
        print("="*60)
        
        all_passed = True
        for challenge_id, is_correct in results:
            status = "✅ PASSED" if is_correct else "❌ FAILED"
            print(f"  {challenge_id.upper()}: {status}")
            if not is_correct:
                all_passed = False
        
        print("="*60)
        
        return all_passed
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hint_answers()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED - Hint answer validation is working!")
    else:
        print("❌ SOME TESTS FAILED - Review validation logic!")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)

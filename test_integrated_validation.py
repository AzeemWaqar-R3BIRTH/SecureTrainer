#!/usr/bin/env python3
"""
Test script to verify integrated validation system with hint answers
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_integrated_system():
    """Test the integrated validation system with hint answers"""
    print("🧪 Testing Integrated Validation System\n")
    print("="*60)
    
    try:
        from app.ai.integrated_validation_system import integrated_validation_system
        
        # Test cases: (challenge_id, hint_answer)
        test_cases = [
            ('sql_3', "This payload uses UNION to combine results and extract user credentials."),
            ('sql_4', "Time-based Blind SQL Injection uses time delays to infer database information."),
            ('sql_5', "Boolean-based Blind SQL Injection extracts data by asking true/false questions.")
        ]
        
        results = []
        
        for challenge_id, hint_answer in test_cases:
            print(f"\n📝 Testing {challenge_id.upper()}: '{hint_answer}'\n")
            
            # Validate using integrated system
            is_correct, feedback = integrated_validation_system.validate_challenge_solution(
                challenge_id, hint_answer
            )
            
            print("="*60)
            print(f"\n📊 VALIDATION RESULT for {challenge_id.upper()}:")
            print(f"  ✅ Is Correct: {is_correct}")
            print(f"  💬 Feedback: {feedback}")
            print("="*60)
            
            results.append((challenge_id, is_correct))
            
            if is_correct:
                print(f"\n🎉 SUCCESS! {challenge_id.upper()} hint answer validated!")
            else:
                print(f"\n❌ FAILURE! {challenge_id.upper()} hint answer rejected!")
        
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
    success = test_integrated_system()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED - Integrated system working!")
    else:
        print("❌ SOME TESTS FAILED - Server restart may be needed!")
        print("\n💡 If tests fail, restart your Flask application:")
        print("   1. Stop the current server (Ctrl+C)")
        print("   2. Restart it: python securetrainer.py")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)

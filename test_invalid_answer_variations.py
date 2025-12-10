#!/usr/bin/env python3
"""
Test script to verify "i dont know the answer" and similar phrases are rejected
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_invalid_answer_variations():
    """Test that various invalid answer formats are rejected"""
    print("🧪 Testing Invalid Answer Variations\n")
    print("="*60)
    
    try:
        from app.ai.comprehensive_validation_engine import comprehensive_validator
        
        # Test cases: variations of "I don't know" that should be rejected
        test_cases = [
            ("xss_7", "i dont know the answer"),  # Original failing case
            ("xss_7", "I don't know the answer"),
            ("xss_7", "i dont know"),
            ("xss_7", "I don't know"),
            ("xss_7", "idk the answer"),
            ("xss_7", "idk"),
            ("xss_7", "no idea what this is"),
            ("xss_7", "no idea"),
            ("xss_7", "not sure about this"),
            ("xss_7", "not sure"),
            ("xss_7", "i dunno the answer"),
            ("xss_7", "dont know the answer"),
            ("xss_7", "i need help with this"),
            ("auth_7", "help me"),  # NEW: Second failing case
            ("auth_7", "help"),
            ("auth_7", "please help me"),
            ("auth_7", "i need help"),
        ]
        
        print("\n📋 Testing Invalid Answer Variations (should all be REJECTED):\n")
        
        passed = 0
        failed = 0
        failed_cases = []
        
        for challenge_id, answer in test_cases:
            result = comprehensive_validator.validate_answer(challenge_id, answer, None)
            
            if not result.is_correct:
                print(f"  ✅ '{answer}' -> CORRECTLY REJECTED")
                passed += 1
            else:
                print(f"  ❌ '{answer}' -> WRONGLY ACCEPTED (Tier: {result.tier_used.name}, Confidence: {result.confidence:.2f})")
                failed += 1
                failed_cases.append(answer)
        
        # Summary
        print("\n" + "="*60)
        print(f"\n📊 RESULTS:")
        print(f"  ✅ Correctly Rejected: {passed}/{len(test_cases)}")
        print(f"  ❌ Wrongly Accepted:   {failed}/{len(test_cases)}")
        
        if failed > 0:
            print(f"\n⚠️  FAILED CASES:")
            for case in failed_cases:
                print(f"    - '{case}'")
            print("\n❌ VALIDATION FIX DID NOT WORK COMPLETELY")
            return False
        else:
            print("\n✅ SUCCESS! All invalid answer variations are correctly rejected!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_invalid_answer_variations()
    sys.exit(0 if success else 1)

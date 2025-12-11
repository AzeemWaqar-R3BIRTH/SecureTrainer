"""
Comprehensive Test Suite for Trivial Answer Rejection
Tests all 50 challenges to ensure they properly reject trivial/invalid answers

This test suite verifies that the AI validation engine correctly rejects
non-informative answers across all challenge categories:
- SQL Injection (10 challenges)
- XSS (10 challenges)
- Command Injection (10 challenges)
- Authentication (10 challenges)
- CSRF (10 challenges)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_trivial_answer_rejection():
    """Comprehensive test for all 50 challenges rejecting trivial answers"""
    print("[TEST] COMPREHENSIVE TRIVIAL ANSWER REJECTION TEST SUITE")
    print("="*80)
    print("Testing all 50 challenges across 5 categories")
    print("="*80)
    
    try:
        from app.ai.comprehensive_validation_engine import comprehensive_validator
        
        # All 50 challenge IDs organized by category
        all_challenges = {
            'SQL Injection': [
                'sql_1', 'sql_2', 'sql_3', 'sql_4', 'sql_5',
                'sql_6', 'sql_7', 'sql_8', 'sql_9', 'sql_10'
            ],
            'XSS': [
                'xss_1', 'xss_2', 'xss_3', 'xss_4', 'xss_5',
                'xss_6', 'xss_7', 'xss_8', 'xss_9', 'xss_10'
            ],
            'Command Injection': [
                'cmd_1', 'cmd_2', 'cmd_3', 'cmd_4', 'cmd_5',
                'cmd_6', 'cmd_7', 'cmd_8', 'cmd_9', 'cmd_10'
            ],
            'Authentication': [
                'auth_1', 'auth_2', 'auth_3', 'auth_4', 'auth_5',
                'auth_6', 'auth_7', 'auth_8', 'auth_9', 'auth_10'
            ],
            'CSRF': [
                'csrf_1', 'csrf_2', 'csrf_3', 'csrf_4', 'csrf_5',
                'csrf_6', 'csrf_7', 'csrf_8', 'csrf_9', 'csrf_10'
            ]
        }
        
        # Comprehensive list of trivial/invalid answers that should ALWAYS be rejected
        trivial_answers = [
            # Direct "I don't know" variations
            "I don't know",
            "i dont know",
            "idk",
            "I dunno",
            "no idea",
            "not sure",
            "dont know",
            
            # Generic responses
            "unknown",
            "nothing",
            "none",
            "na",
            "n/a",
            "N/A",
            
            # Help requests
            "help",
            "I need help",
            "help me",
            
            # Confused/unclear responses
            "what",
            "huh",
            "confused",
            "?",
            "???",
            
            # Skip/pass responses
            "skip",
            "pass",
            "next",
            
            # Test/random inputs
            "test",
            "testing",
            "random",
            "asdf",
            "asdfjkl",
            "qwerty",
            "123",
            "1234",
            "12345",
            "abc",
            "abcdef",
            
            # Very short/useless answers
            "a",
            "ok",
            "yes",
            "no",
            "maybe",
            "sure",
            
            # Empty or whitespace
            "",
            "   ",
            "\t",
            "\n",
            
            # Other generic non-answers
            "anything",
            "something",
            "whatever",
            "stuff",
            "things",
            "error",
            "wrong",
            "correct",
            "true",
            "false",
            
            # Common spam patterns
            "aaaaa",
            "zzzzz",
            "11111",
            "00000",
            "xxxxx",
        ]
        
        # Track results
        total_tests = 0
        passed_tests = 0
        failed_tests = []
        category_results = {}
        
        # Test each category
        for category, challenge_ids in all_challenges.items():
            print(f"\n{'='*80}")
            print(f"📂 CATEGORY: {category}")
            print(f"{'='*80}")
            
            category_passed = 0
            category_total = 0
            
            for challenge_id in challenge_ids:
                challenge_failed = []
                
                # Test each trivial answer against this challenge
                for trivial_answer in trivial_answers:
                    total_tests += 1
                    category_total += 1
                    
                    # Validate the trivial answer
                    result = comprehensive_validator.validate_answer(
                        challenge_id, 
                        trivial_answer, 
                        None
                    )
                    
                    # Check if it was correctly rejected
                    if result.is_correct:
                        # FAILURE: Trivial answer was accepted!
                        failed_tests.append({
                            'challenge': challenge_id,
                            'answer': trivial_answer,
                            'confidence': result.confidence,
                            'tier': result.tier_used.name
                        })
                        challenge_failed.append(trivial_answer)
                    else:
                        # SUCCESS: Trivial answer was rejected
                        passed_tests += 1
                        category_passed += 1
                
                # Report results for this challenge
                if challenge_failed:
                    print(f"  ❌ {challenge_id.upper()}: FAILED - Accepted {len(challenge_failed)} trivial answers")
                    for ans in challenge_failed[:3]:  # Show first 3 failures
                        print(f"      - '{ans}'")
                    if len(challenge_failed) > 3:
                        print(f"      ... and {len(challenge_failed) - 3} more")
                else:
                    print(f"  ✅ {challenge_id.upper()}: PASSED - Rejected all {len(trivial_answers)} trivial answers")
            
            # Category summary
            category_pass_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            category_results[category] = {
                'passed': category_passed,
                'total': category_total,
                'pass_rate': category_pass_rate
            }
            
            print(f"\n  📊 {category} Summary: {category_passed}/{category_total} tests passed ({category_pass_rate:.1f}%)")
        
        # Overall summary
        print(f"\n{'='*80}")
        print(f"📊 OVERALL TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Pass Rate: {(passed_tests/total_tests*100):.2f}%")
        
        # Category breakdown
        print(f"\n{'='*80}")
        print(f"📈 CATEGORY BREAKDOWN")
        print(f"{'='*80}")
        for category, results in category_results.items():
            status = "✅" if results['pass_rate'] == 100.0 else "⚠️" if results['pass_rate'] >= 95.0 else "❌"
            print(f"{status} {category:20s}: {results['passed']:5d}/{results['total']:5d} ({results['pass_rate']:6.2f}%)")
        
        # Detailed failure report
        if failed_tests:
            print(f"\n{'='*80}")
            print(f"⚠️  DETAILED FAILURE REPORT")
            print(f"{'='*80}")
            print(f"The following trivial answers were INCORRECTLY ACCEPTED:")
            print()
            
            # Group failures by challenge
            failures_by_challenge = {}
            for failure in failed_tests:
                challenge = failure['challenge']
                if challenge not in failures_by_challenge:
                    failures_by_challenge[challenge] = []
                failures_by_challenge[challenge].append(failure)
            
            for challenge, failures in failures_by_challenge.items():
                print(f"\n{challenge.upper()}:")
                for failure in failures[:5]:  # Show first 5 per challenge
                    print(f"  ❌ '{failure['answer']}' (Confidence: {failure['confidence']:.0%}, Tier: {failure['tier']})")
                if len(failures) > 5:
                    print(f"  ... and {len(failures) - 5} more failures")
        
        # Final verdict
        print(f"\n{'='*80}")
        if len(failed_tests) == 0:
            print("✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅")
            print("All 50 challenges correctly reject trivial answers!")
            print("The validation system is working perfectly! 🎉")
        elif len(failed_tests) < total_tests * 0.01:  # Less than 1% failure
            print("⚠️  MOSTLY PASSED - Minor Issues Detected")
            print(f"Only {len(failed_tests)} out of {total_tests} tests failed (<1%)")
            print("The validation system is working well with minor edge cases.")
        elif len(failed_tests) < total_tests * 0.05:  # Less than 5% failure
            print("⚠️  PASSED WITH WARNINGS")
            print(f"{len(failed_tests)} out of {total_tests} tests failed (<5%)")
            print("The validation system needs some improvements.")
        else:
            print("❌ TESTS FAILED - Critical Issues Detected")
            print(f"{len(failed_tests)} out of {total_tests} tests failed (>{(len(failed_tests)/total_tests*100):.1f}%)")
            print("The validation system has significant issues with trivial answer rejection.")
        print(f"{'='*80}\n")
        
        return len(failed_tests) == 0
        
    except Exception as e:
        print(f"\n❌ ERROR: Test suite encountered an exception!")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print(" " * 20 + "TRIVIAL ANSWER REJECTION TEST SUITE" + " " * 25)
    print(" " * 78)
    print(" " * 15 + "Testing All 50 Challenges (SQL, XSS, CMD, AUTH, CSRF)" + " " * 11)
    print(" " * 78)
    print(" " * 10 + "Verifying that trivial answers like 'idk', 'test', etc." + " " * 14)
    print(" " * 15 + "are properly rejected by the AI validation engine" + " " * 16)
    print("=" * 80)
    print("\n")
    
    success = test_trivial_answer_rejection()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

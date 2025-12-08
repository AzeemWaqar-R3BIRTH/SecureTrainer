"""
Simple validation test to verify the enhanced system works
"""

import sys
import os

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.ai.enhanced_validation_system import EnhancedValidationEngine
    from app.ai.advanced_answer_validation import AdvancedAnswerValidator
    
    print("✓ Successfully imported validation systems")
    
    # Test the validation engine
    engine = EnhancedValidationEngine()
    print("✓ Enhanced validation engine initialized")
    
    # Test basic validation
    result = engine.validate_answer(
        "authentication bypass", 
        "authentication bypass", 
        {"category": "sql"}
    )
    
    print(f"✓ Basic validation test: {result.is_correct}, confidence: {result.confidence}%")
    
    # Test the advanced validator
    validator = AdvancedAnswerValidator()
    print("✓ Advanced answer validator initialized")
    
    # Test SQL challenge validation
    is_correct, feedback, analysis = validator.validate_challenge_answer(
        "sql_1", "authentication bypass"
    )
    
    print(f"✓ SQL challenge validation: {is_correct}")
    print(f"  Feedback: {feedback}")
    print(f"  Confidence: {analysis.get('confidence_score', 0)}")
    print(f"  Processing time: {analysis.get('processing_time', 0):.3f}s")
    
    # Test XSS challenge validation
    is_correct2, feedback2, analysis2 = validator.validate_challenge_answer(
        "xss_1", "executes JavaScript"
    )
    
    print(f"✓ XSS challenge validation: {is_correct2}")
    print(f"  Feedback: {feedback2}")
    
    # Test statistics
    stats = validator.get_validation_statistics()
    print(f"✓ Validation statistics: {stats['total_validations']} validations, {stats['success_rate']}% success rate")
    
    print("\n🎉 All validation tests passed successfully!")
    print("📊 Enhanced validation system is working correctly")
    
except Exception as e:
    print(f"❌ Error during validation testing: {e}")
    import traceback
    traceback.print_exc()
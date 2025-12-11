#!/usr/bin/env python3
"""
Quick test to verify QR code upload works
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.qr import QRCodeManager
from PIL import Image
from io import BytesIO
import json

def test_qr_upload():
    """Test QR code generation and upload validation"""
    print("=" * 60)
    print("QR CODE UPLOAD FIX TEST")
    print("=" * 60)
    
    # Initialize QR manager
    qr_manager = QRCodeManager()
    
    # Generate a test QR code
    print("\n1. Generating test QR code...")
    test_user_id = "507f1f77bcf86cd799439011"
    test_email = "test@example.com"
    
    qr_data = qr_manager.generate_qr_code(test_user_id, test_email)
    print(f"   ✅ QR code generated: {qr_data['filepath']}")
    print(f"   Token: {qr_data['token']}")
    print(f"   Expires: {qr_data['expires']}")
    
    # Test 1: Validate from file path
    print("\n2. Testing validation from file path...")
    try:
        with open(qr_data['filepath'], 'rb') as f:
            is_valid, result = qr_manager.validate_qr_code_from_image(f)
            
        if is_valid:
            print(f"   ✅ SUCCESS: QR code validated from file!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Email: {result['email']}")
        else:
            print(f"   ❌ FAILED: {result}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Simulate file upload (BytesIO)
    print("\n3. Testing validation from BytesIO (simulates upload)...")
    try:
        with open(qr_data['filepath'], 'rb') as f:
            file_content = f.read()
        
        file_like = BytesIO(file_content)
        is_valid, result = qr_manager.validate_qr_code_from_image(file_like)
        
        if is_valid:
            print(f"   ✅ SUCCESS: QR code validated from BytesIO!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Email: {result['email']}")
        else:
            print(f"   ❌ FAILED: {result}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Validate with camera-style JSON data
    print("\n4. Testing validation from camera scan data...")
    try:
        qr_json_str = json.dumps(qr_data['qr_data'])
        is_valid, result = qr_manager.validate_qr_code(qr_json_str)
        
        if is_valid:
            print(f"   ✅ SUCCESS: QR code validated from camera data!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Email: {result['email']}")
        else:
            print(f"   ❌ FAILED: {result}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL QR CODE TESTS PASSED!")
    print("=" * 60)
    print("\nBoth upload and scanning methods working correctly!")
    return True

if __name__ == "__main__":
    try:
        success = test_qr_upload()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

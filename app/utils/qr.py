import qrcode
import os
import uuid
from datetime import datetime, timedelta
from PIL import Image
import base64
from io import BytesIO

class QRCodeManager:
    def __init__(self, storage_path="qr_codes"):
        # Use absolute path to ensure directory is found
        if not os.path.isabs(storage_path):
            # Get the project root directory (where securetrainer.py is located)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.storage_path = os.path.join(project_root, storage_path)
        else:
            self.storage_path = storage_path
        
        print(f" QR Code storage path: {self.storage_path}")
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure the QR code storage directory exists."""
        try:
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)
                print(f" Created QR code directory: {self.storage_path}")
            else:
                print(f" QR code directory exists: {self.storage_path}")
        except Exception as e:
            print(f" Failed to create QR code directory: {e}")
            raise
    
    def generate_qr_code(self, user_id, user_email, expires_in_hours=120):  # 5 days
        """Generate a unique QR code for user authentication."""
        # Create unique token
        token = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(hours=expires_in_hours)
        
        # Create QR code data
        qr_data = {
            'user_id': str(user_id),
            'token': token,
            'email': user_email,
            'expires': expiry.isoformat(),
            'created': datetime.now().isoformat()
        }
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Store QR data as JSON string for better compatibility
        import json
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file with proper path handling
        filename = f"{token}_{user_id}.png"
        filepath = os.path.join(self.storage_path, filename)
        
        # Normalize the path to handle special characters
        filepath = os.path.normpath(filepath)
        
        # Ensure directory exists before saving
        os.makedirs(self.storage_path, exist_ok=True)
        
        print(f" Saving QR code to: {filepath}")
        
        # Convert to base64 first (this always works)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_bytes = buffer.getvalue()
        img_str = base64.b64encode(img_bytes).decode()
        
        # Now save to file using binary write
        try:
            # Use pathlib for better path handling
            from pathlib import Path
            file_path_obj = Path(filepath)
            file_path_obj.write_bytes(img_bytes)
            print(f" QR code saved successfully to: {filepath}")
        except Exception as e:
            print(f" Failed to save QR code with pathlib: {e}")
            # Final fallback - direct binary write
            try:
                with open(str(filepath), 'wb') as f:
                    f.write(img_bytes)
                print(f" QR code saved using direct write")
            except Exception as e2:
                print(f" All save methods failed: {e2}")
                # Continue anyway - we have the base64 data for email
        
        return {
            'token': token,
            'filepath': filepath,
            'base64_data': img_str,
            'expires': expiry,
            'qr_data': qr_data
        }
    
    def validate_qr_code(self, qr_data_str):
        """Validate a scanned QR code."""
        try:
            import json
            import ast
            
            print(f" Validating QR data: {qr_data_str[:100]}...")
            
            # Try to parse as JSON first, then as Python literal
            qr_data = None
            try:
                qr_data = json.loads(qr_data_str)
                print(f" Parsed as JSON successfully")
            except json.JSONDecodeError as e:
                print(f" JSON parsing failed: {e}")
                try:
                    qr_data = ast.literal_eval(qr_data_str)
                    print(f" Parsed as Python literal successfully")
                except (ValueError, SyntaxError) as e:
                    print(f" Python literal parsing failed: {e}")
                    return False, "Invalid QR code format - not valid JSON or Python literal"
            
            if not qr_data:
                return False, "QR code data is empty"
            
            print(f" Parsed QR data: {qr_data}")
            
            # Validate required fields
            required_fields = ['user_id', 'token', 'expires']
            for field in required_fields:
                if field not in qr_data:
                    print(f" Missing required field: {field}")
                    return False, f"Invalid QR code - missing {field}"
            
            # Check if expired
            try:
                expiry = datetime.fromisoformat(qr_data['expires'])
                current_time = datetime.now()
                print(f" Expiry: {expiry}, Current: {current_time}")
                
                if current_time > expiry:
                    print(f" QR code expired")
                    return False, "QR code has expired. Please request a new one."
            except Exception as e:
                print(f" Error parsing expiry date: {e}")
                return False, "Invalid QR code expiry format"
            
            # Check if QR file exists (optional validation)
            try:
                filename = f"{qr_data['token']}_{qr_data['user_id']}.png"
                filepath = os.path.join(self.storage_path, filename)
                print(f" Checking QR file: {filepath}")
                
                if not os.path.exists(filepath):
                    print(f" QR file not found, but continuing (file might be cleaned up)")
                    # Don't fail here - file might have been cleaned up but QR is still valid
            except Exception as e:
                print(f" Error checking QR file: {e}")
                # Don't fail here - file validation is optional
            
            print(f" QR code validation successful")
            return True, qr_data
            
        except Exception as e:
            print(f" QR validation error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"QR code validation failed: {str(e)}"
    
    def cleanup_expired_codes(self):
        """Remove expired QR code files."""
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.storage_path, filename)
                    # Check if file is older than 5 days (120 hours)
                    if os.path.getctime(filepath) < (datetime.now() - timedelta(hours=120)).timestamp():
                        os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up expired QR codes: {e}")
    
    def get_qr_code_info(self, token):
        """Get information about a specific QR code."""
        try:
            for filename in os.listdir(self.storage_path):
                if filename.startswith(token):
                    filepath = os.path.join(self.storage_path, filename)
                    return {
                        'filepath': filepath,
                        'filename': filename,
                        'created': datetime.fromtimestamp(os.path.getctime(filepath))
                    }
        except Exception as e:
            print(f"Error getting QR code info: {e}")
        
        return None
    
    def validate_qr_code_from_image(self, image_file):
        """Validate a QR code from an uploaded image file."""
        try:
            from pyzbar import pyzbar
            from PIL import Image
            
            print(f" Processing image file: {image_file.filename}")
            print(f" Image file type: {type(image_file)}")
            
            # Reset file pointer to beginning
            image_file.seek(0)
            
            # Read the image using PIL
            try:
                img_pil = Image.open(image_file)
                print(f" PIL Image size: {img_pil.size}, mode: {img_pil.mode}")
            except Exception as e:
                print(f" PIL Image open error: {e}")
                return False, f"Cannot open image file: {str(e)}"
            
            # Convert to RGB if necessary
            if img_pil.mode != 'RGB':
                img_pil = img_pil.convert('RGB')
                print(f" Converted to RGB")
            
            # Use pyzbar to decode QR codes
            try:
                decoded_objects = pyzbar.decode(img_pil)
                print(f" pyzbar found {len(decoded_objects)} QR codes")
                
                if decoded_objects:
                    qr_data_str = decoded_objects[0].data.decode('utf-8')
                    print(f" QR data (first 100 chars): {qr_data_str[:100]}...")
                    
                    # Validate the QR code data
                    return self.validate_qr_code(qr_data_str)
                else:
                    return False, "No QR code found in image. Please ensure the image contains a clear QR code."
                    
            except Exception as e:
                print(f" pyzbar decoding error: {e}")
                return False, f"Error decoding QR code with pyzbar: {str(e)}"
            
        except ImportError as e:
            print(f" Import error: {e}")
            if 'pyzbar' in str(e):
                return False, "QR code scanning library not available. Please contact support."
            else:
                return False, f"Required library not available: {str(e)}"
        except Exception as e:
            print(f" QR decoding error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error processing QR code image: {str(e)}"

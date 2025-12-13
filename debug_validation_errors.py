#!/usr/bin/env python3
"""
Debug specific form validation errors
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

test_db_path = os.path.join(tempfile.gettempdir(), 'bp_debug_validation.db')
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

def debug_form_validation():
    """Debug specific form validation errors"""
    print("=== Form Validation Debug ===")
    
    from app import app, db, RegisterForm
    
    with app.app_context():
        try:
            db.create_all()
            
            with app.test_client() as client:
                # Get CSRF token
                get_response = client.get('/register')
                content = get_response.get_data(as_text=True)
                csrf_start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                csrf_end = content.find('"', csrf_start)
                csrf_token = content[csrf_start:csrf_end] if csrf_start > 25 else ''
                
                # Test form validation without submitting
                with app.test_request_context('/', method='POST', data={
                    'csrf_token': csrf_token,
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Debug User',
                    'email': 'debug@example.com',
                    'password': 'DebugPass123!',
                    'sobriety_date': '2021-01-01',
                    'gender': 'male',
                    'agreed_guidelines': True
                }):
                    form = RegisterForm()
                    print(f"Form validation result: {form.validate()}")
                    
                    if form.errors:
                        print("Validation errors found:")
                        for field_name, errors in form.errors.items():
                            print(f"  {field_name}: {errors}")
                    else:
                        print("✅ Form validation passed!")
                        
                        # Test the actual submission
                        print("\nTesting actual form submission...")
                        
                        response = client.post('/register', data={
                            'csrf_token': csrf_token,
                            'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                            'display_name': 'Debug User',
                            'email': 'debug@example.com',
                            'password': 'DebugPass123!',
                            'sobriety_date': '2021-01-01',
                            'gender': 'male',
                            'agreed_guidelines': 'y'  # HTML form sends 'y' for checked
                        })
                        
                        print(f"Submission status: {response.status_code}")
                        
                        if response.status_code == 302:
                            print("✅ Submission successful!")
                            
                            # Check database
                            from app import User
                            user = User.query.filter_by(email='debug@example.com').first()
                            if user:
                                print(f"✅ User saved: {user.bp_id}")
                                return True
                            else:
                                print("❌ User not saved to database")
                                return False
                        else:
                            print("❌ Submission failed")
                            return False
                    
        except Exception as e:
            print(f"Debug failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            try:
                if os.path.exists(test_db_path):
                    os.remove(test_db_path)
            except:
                pass

if __name__ == "__main__":
    debug_form_validation()
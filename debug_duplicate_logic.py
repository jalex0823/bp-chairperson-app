#!/usr/bin/env python3
"""
Debug the duplicate email check logic
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

def debug_duplicate_email_logic():
    """Debug the duplicate email check"""
    print("=== Debugging Duplicate Email Logic ===")
    
    test_db_path = os.path.join(tempfile.gettempdir(), 'bp_debug_dup.db')
    os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    from app import app, db, User
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        try:
            db.create_all()
            
            # Create user directly first
            user1 = User(
                display_name="Debug User 1",
                email="debug@test.com",
                is_admin=False,
                agreed_guidelines=True
            )
            user1.set_password("DebugPass123!")
            db.session.add(user1)
            db.session.commit()
            
            print(f"✅ Created user directly: {user1.email}")
            
            # Check if we can find the user
            found_user = User.query.filter_by(email="debug@test.com").first()
            if found_user:
                print(f"✅ Can find user by exact email: {found_user.display_name}")
            else:
                print("❌ Cannot find user by exact email")
            
            # Test the lowercase logic
            found_lower = User.query.filter_by(email="debug@test.com".lower().strip()).first()
            if found_lower:
                print(f"✅ Can find user by lowercase email: {found_lower.display_name}")
            else:
                print("❌ Cannot find user by lowercase email")
            
            # Now try the form registration
            print(f"\nTesting form registration with duplicate email...")
            
            with app.test_client() as client:
                dup_data = {
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Debug User 2',
                    'email': 'debug@test.com',  # Same email
                    'password': 'AnotherPass123!',
                    'gender': 'male',
                    'agreed_guidelines': 'y'
                }
                
                # Enable some debug logging
                import logging
                logging.basicConfig(level=logging.DEBUG)
                
                response = client.post('/register', data=dup_data)
                
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    if 'already exists' in content:
                        print("✅ Duplicate properly detected")
                    else:
                        print("❌ Duplicate not detected")
                        print("Looking for flash messages...")
                        if 'alert-danger' in content:
                            print("Flash message area found")
                        else:
                            print("No flash message area found")
                
                # Check how many users exist now
                all_users = User.query.all()
                print(f"Total users in database: {len(all_users)}")
                for user in all_users:
                    print(f"  - {user.email} ({user.display_name})")
                    
        except Exception as e:
            print(f"❌ Debug failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                if os.path.exists(test_db_path):
                    os.remove(test_db_path)
            except:
                pass

if __name__ == "__main__":
    debug_duplicate_email_logic()
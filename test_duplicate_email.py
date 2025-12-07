#!/usr/bin/env python3
"""
Test duplicate email prevention specifically
"""
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

def test_duplicate_email_prevention():
    """Test duplicate email prevention specifically"""
    print("=== Duplicate Email Prevention Test ===")
    
    test_db_path = os.path.join(tempfile.gettempdir(), 'bp_duplicate_test.db')
    os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    from app import app, db, User
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        try:
            db.create_all()
            
            with app.test_client() as client:
                # First registration
                print("1. Creating first user...")
                
                first_user_data = {
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'First User',
                    'email': 'duplicate@test.com',
                    'password': 'FirstPassword123!',
                    'sobriety_date': '2020-01-01',
                    'gender': 'male',
                    'agreed_guidelines': 'y'
                }
                
                response1 = client.post('/register', data=first_user_data, follow_redirects=False)
                
                if response1.status_code == 302:
                    print("   ✅ First user registration successful")
                else:
                    print(f"   ❌ First user registration failed: {response1.status_code}")
                    return False
                
                # Verify first user is in database
                user1 = User.query.filter_by(email='duplicate@test.com').first()
                if user1:
                    print(f"   ✅ First user in database: {user1.display_name}")
                else:
                    print("   ❌ First user not found in database")
                    return False
                
                # Try to register with same email
                print("\n2. Attempting duplicate email registration...")
                
                duplicate_data = {
                    'access_code': 'BP2025!ChairPersonAccess#Unlock$Key',
                    'display_name': 'Second User', 
                    'email': 'duplicate@test.com',  # Same email
                    'password': 'SecondPassword123!',
                    'sobriety_date': '2021-01-01',
                    'gender': 'female',
                    'agreed_guidelines': 'y'
                }
                
                response2 = client.post('/register', data=duplicate_data)
                
                print(f"   Response status: {response2.status_code}")
                
                if response2.status_code == 200:
                    content = response2.get_data(as_text=True)
                    if 'already exists' in content:
                        print("   ✅ Duplicate email correctly rejected with error message")
                        
                        # Verify only one user exists
                        all_users = User.query.filter_by(email='duplicate@test.com').all()
                        if len(all_users) == 1:
                            print(f"   ✅ Only one user exists: {all_users[0].display_name}")
                            return True
                        else:
                            print(f"   ❌ Multiple users found: {len(all_users)}")
                            return False
                    else:
                        print("   ❌ No 'already exists' error message found")
                        print("   Response preview:")
                        lines = content.split('\n')[:20]
                        for line in lines:
                            if 'alert' in line or 'error' in line.lower():
                                print(f"     {line.strip()}")
                        return False
                elif response2.status_code == 302:
                    print("   ❌ Duplicate registration was accepted (should be rejected)")
                    return False
                else:
                    print(f"   ❌ Unexpected response status: {response2.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
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
    success = test_duplicate_email_prevention()
    
    if success:
        print(f"\n✅ Duplicate email prevention is working correctly!")
    else:
        print(f"\n❌ Duplicate email prevention has issues")
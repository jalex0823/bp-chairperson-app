"""Create or update admin account with preferred email"""
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check for existing admin with jalex0823 email
    admin_emails = [
        'jalex0823@admin.local',
        'jalex0823@gmail.com',
        'admin@backporch.com'
    ]
    
    print("Looking for existing accounts:")
    for email in admin_emails:
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"  Found: {email} (Admin: {user.is_admin})")
    
    # Ask which email to use
    print("\n" + "="*60)
    print("Choose admin login option:")
    print("1. Use jalex0823@admin.local (already set up)")
    print("2. Create/update admin@backporch.com")  
    print("3. Create/update jalex0823@gmail.com")
    print("="*60)
    
    choice = input("Enter choice (1-3) or specific email: ").strip()
    
    if choice == '1':
        email = 'jalex0823@admin.local'
    elif choice == '2':
        email = 'admin@backporch.com'
    elif choice == '3':
        email = 'jalex0823@gmail.com'
    elif '@' in choice:
        email = choice
    else:
        print("❌ Invalid choice")
        exit(1)
    
    # Find or create user
    user = User.query.filter_by(email=email).first()
    
    password = 'admin123'
    
    if user:
        # Update existing user
        user.is_admin = True
        user.password_hash = generate_password_hash(password)
        print(f"\n✅ Updated existing user: {email}")
    else:
        # Create new user
        user = User(
            email=email,
            display_name=email.split('@')[0],
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(user)
        print(f"\n✅ Created new admin user: {email}")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("🎉 ADMIN LOGIN CREDENTIALS")
    print("="*60)
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"🌐 Login URL: http://127.0.0.1:5000/login")
    print("="*60)

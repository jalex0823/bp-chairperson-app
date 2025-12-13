from app import app, db, User

with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print(f"Admin User Found:")
        print(f"  Display Name: {admin.display_name}")
        print(f"  BP ID: {admin.bp_id}")
        print(f"  Email: {admin.email}")
    else:
        print("No admin user found")
        
    # List all users
    all_users = User.query.all()
    print(f"\nTotal users: {len(all_users)}")
    for u in all_users:
        print(f"  - {u.display_name} ({u.bp_id}) - Admin: {u.is_admin}")

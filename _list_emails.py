from app import app, db, User

with app.app_context():
    users = User.query.order_by(User.id).all()
    print(f"\n{'ID':<6} {'Display Name':<25} {'Email':<40} {'Role'}")
    print("-" * 85)
    for u in users:
        role = "ADMIN" if u.is_admin else "user"
        print(f"{u.id:<6} {u.display_name:<25} {u.email:<40} {role}")
    print(f"\nTotal: {len(users)} users")

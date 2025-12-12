"""
Add password_reset_required column to users table
Run this on Heroku with: heroku run python add_password_reset_column.py
"""
from app import app, db

with app.app_context():
    try:
        # Add the column using raw SQL
        with db.engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='password_reset_required'
            """))
            
            if result.fetchone() is None:
                # Column doesn't exist, add it
                conn.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN password_reset_required BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✅ Successfully added password_reset_required column to users table")
            else:
                print("ℹ️  Column password_reset_required already exists")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might mean the column already exists or there's a database issue")

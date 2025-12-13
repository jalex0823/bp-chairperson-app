"""
Simple migration to add profile_image_type column if it doesn't exist.
"""
from app import app, db
from sqlalchemy import text

def add_profile_image_type_column():
    """Add profile_image_type column to users table if it doesn't exist."""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('users')]
            
            if 'profile_image_type' in columns:
                print("✓ profile_image_type column already exists")
                return
            
            print("Adding profile_image_type column...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN profile_image_type VARCHAR(50) NULL
                """))
                conn.commit()
            
            print("✓ Successfully added profile_image_type column")
            
        except Exception as e:
            print(f"✗ Error adding profile_image_type column: {e}")
            # Don't raise - allow deployment to continue

if __name__ == "__main__":
    add_profile_image_type_column()

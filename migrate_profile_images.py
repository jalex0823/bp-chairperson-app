"""
Migration script to update profile_image storage from filename to binary data.
Run this once to update the database schema.
"""
from app import app, db
from sqlalchemy import text

def migrate_profile_images():
    """Migrate profile_image column from String to LargeBinary and add profile_image_type column."""
    with app.app_context():
        try:
            # Check if profile_image_type column already exists
            inspector = db.inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('users')]
            
            if 'profile_image_type' in columns:
                print("✓ Migration already completed - profile_image_type column exists")
                return
            
            print("Starting profile image migration...")
            
            # For MySQL, we need to:
            # 1. Add the new profile_image_type column
            # 2. Modify profile_image to LONGBLOB
            
            with db.engine.connect() as conn:
                # Add profile_image_type column
                print("Adding profile_image_type column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN profile_image_type VARCHAR(50) NULL
                """))
                conn.commit()
                
                # Change profile_image from VARCHAR to LONGBLOB
                # First, clear any existing filename data since we can't convert it
                print("Clearing old filename data...")
                conn.execute(text("""
                    UPDATE users 
                    SET profile_image = NULL 
                    WHERE profile_image IS NOT NULL
                """))
                conn.commit()
                
                print("Converting profile_image column to LONGBLOB...")
                conn.execute(text("""
                    ALTER TABLE users 
                    MODIFY COLUMN profile_image LONGBLOB NULL
                """))
                conn.commit()
            
            print("✓ Migration completed successfully!")
            print("Note: Existing profile images were cleared. Users will need to re-upload their photos.")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate_profile_images()

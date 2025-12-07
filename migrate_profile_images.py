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
            columns = {c['name']: c for c in inspector.get_columns('users')}
            
            # Check if profile_image_type exists
            if 'profile_image_type' in columns:
                # Check if profile_image is already LONGBLOB/BLOB
                profile_image_type = str(columns.get('profile_image', {}).get('type', '')).upper()
                if 'BLOB' in profile_image_type or 'BINARY' in profile_image_type:
                    print("✓ Migration already completed - columns have correct types")
                    return
            
            print("Starting profile image migration...")
            
            with db.engine.connect() as conn:
                # Add profile_image_type column if it doesn't exist
                if 'profile_image_type' not in columns:
                    print("Adding profile_image_type column...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN profile_image_type VARCHAR(50) NULL
                    """))
                    conn.commit()
                else:
                    print("✓ profile_image_type column already exists")
                
                # Clear any existing filename data since we can't convert it
                print("Clearing old filename data...")
                conn.execute(text("""
                    UPDATE users 
                    SET profile_image = NULL 
                    WHERE profile_image IS NOT NULL
                """))
                conn.commit()
                
                # Check current type of profile_image column
                profile_image_type = str(columns.get('profile_image', {}).get('type', '')).upper()
                if 'BLOB' not in profile_image_type and 'BINARY' not in profile_image_type:
                    print(f"Converting profile_image column from {profile_image_type} to LONGBLOB...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        MODIFY COLUMN profile_image LONGBLOB NULL
                    """))
                    conn.commit()
                else:
                    print(f"✓ profile_image column already is {profile_image_type}")
            
            print("✓ Migration completed successfully!")
            print("Note: Existing profile images were cleared. Users will need to re-upload their photos.")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            import traceback
            print(traceback.format_exc())
            # Don't raise - allow deployment to continue
            # raise

if __name__ == "__main__":
    migrate_profile_images()

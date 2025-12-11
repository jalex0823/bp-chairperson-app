"""Test database configuration and connection"""
import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("DATABASE CONFIGURATION TEST")
print("=" * 60)

# Check environment variables
print("\nEnvironment Variables:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'NOT SET'}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Test config import
print("\n" + "=" * 60)
print("Testing Config Import...")
print("=" * 60)

try:
    from config import Config
    print(f"\n✅ Config imported successfully")
    print(f"\nDatabase URI: {Config.SQLALCHEMY_DATABASE_URI[:50]}...")
    
    # Test database connection
    print("\n" + "=" * 60)
    print("Testing Database Connection...")
    print("=" * 60)
    
    from app import app, db
    
    with app.app_context():
        # Try to execute a simple query
        from sqlalchemy import text
        result = db.session.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Try to query a table
        result = db.session.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        print(f"\n✅ Found {len(tables)} tables in database")
        print("Tables:", [table[0] for table in tables[:5]])
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)

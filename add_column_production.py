"""Connect to production MySQL and add password_reset_required column"""
import pymysql

# Production database credentials
HOST = "mysql.therealbackporch.com"
USER = "chairperson"
PASSWORD = "12!Gratitudeee"
DATABASE = "chairameeting"
PORT = 3306

print(f"Connecting to {HOST}...")

try:
    # Connect to database
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        port=PORT
    )
    
    print("✓ Connected successfully")
    
    with connection.cursor() as cursor:
        # Add the column
        sql = "ALTER TABLE users ADD COLUMN password_reset_required BOOLEAN DEFAULT FALSE"
        print(f"Executing: {sql}")
        cursor.execute(sql)
        connection.commit()
        print("✅ Column added successfully!")
        
except pymysql.err.OperationalError as e:
    if "Duplicate column" in str(e):
        print("ℹ️  Column already exists - no action needed")
    else:
        print(f"❌ Database error: {e}")
        raise
except Exception as e:
    print(f"❌ Error: {e}")
    raise
finally:
    if 'connection' in locals():
        connection.close()
        print("Connection closed")

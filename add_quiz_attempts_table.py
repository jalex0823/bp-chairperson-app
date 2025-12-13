"""
Database migration to add quiz_attempts table.

This script adds a new table to track user quiz attempts and scores.

Usage:
    python add_quiz_attempts_table.py
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'chairameeting')
DB_PORT = int(os.getenv('DB_PORT', 3306))

def run_migration():
    """Execute the migration."""
    print("Connecting to database...")
    
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            print("Creating quiz_attempts table...")
            
            # Create quiz_attempts table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                quiz_id VARCHAR(50) NOT NULL,
                score INT NOT NULL,
                total_questions INT NOT NULL,
                correct_answers INT NOT NULL,
                passed TINYINT(1) NOT NULL,
                answers TEXT,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                points_awarded INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_quiz (user_id, quiz_id),
                INDEX idx_completed (completed_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_table_sql)
            connection.commit()
            print("✓ quiz_attempts table created successfully!")
            
            # Check if table was created
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = 'quiz_attempts'
            """, (DB_NAME,))
            
            result = cursor.fetchone()
            if result[0] == 1:
                print("✓ Migration completed successfully!")
            else:
                print("✗ Error: Table was not created")
                
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    print("=" * 60)
    print("Quiz Attempts Table Migration")
    print("=" * 60)
    run_migration()
    print("\nMigration complete!")

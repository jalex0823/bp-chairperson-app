#!/usr/bin/env python3
"""
Check users table schema.
"""

import sqlite3

DB_PATH = 'instance/bp_chair.sqlite3'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print("Users table schema:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()

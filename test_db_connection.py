#!/usr/bin/env python3
"""
Simple script to verify MySQL connectivity using the app's SQLAlchemy config.
"""
import os
from dotenv import load_dotenv
from app import app, db

load_dotenv()

def main():
    with app.app_context():
        try:
            # Print effective SQLAlchemy engine URL for diagnostics
            engine_url = str(db.engine.url)
            print(f"Using engine URL: {engine_url}")
            # Try to get a connection and run a simple query
            result = db.session.execute(db.text("SELECT 1 AS ok"))
            row = result.fetchone()
            print(f"✅ DB connection OK: {row.ok}")
        except Exception as e:
            print(f"❌ DB connection failed: {e}")
            print("Check your DATABASE_URL or DB_* variables in .env and ensure MySQL allows remote connections.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick script to list tables in the connected database to confirm schema presence.
"""
from app import app, db

def main():
    with app.app_context():
        print(f"Engine URL: {db.engine.url}")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if not tables:
            print("No tables found.")
        else:
            print("Tables:")
            for t in tables:
                print(f"- {t}")

if __name__ == "__main__":
    main()
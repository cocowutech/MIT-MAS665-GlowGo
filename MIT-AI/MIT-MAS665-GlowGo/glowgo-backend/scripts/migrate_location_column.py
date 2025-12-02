"""
Migration script to increase location column size from VARCHAR(100) to VARCHAR(255)
Run this script once to update the database schema.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from models.database import engine


def migrate():
    """Increase location column size to support longer place-based locations"""
    print("Starting migration: Increasing location column size...")

    with engine.connect() as conn:
        try:
            # PostgreSQL syntax for altering column type
            conn.execute(text("""
                ALTER TABLE preference_sessions
                ALTER COLUMN location TYPE VARCHAR(255);
            """))
            conn.commit()
            print("Migration successful: location column is now VARCHAR(255)")
        except Exception as e:
            print(f"Migration error: {e}")
            # Column might already be the right size, or table doesn't exist yet
            if "does not exist" in str(e).lower():
                print("Table doesn't exist yet. Will be created with correct size on first run.")
            elif "already" in str(e).lower() or "nothing to alter" in str(e).lower():
                print("Column is already the correct size.")
            else:
                raise


if __name__ == "__main__":
    migrate()

# -*- coding: utf-8 -*-
"""Migration script to add new fields to existing database"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate_database(db_path):
    """Add new fields to calculation table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(calculation)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = [
        ("days_per_month", "INTEGER DEFAULT 22"),
        ("monthly_salary", "REAL DEFAULT 0.0"),
        ("minutes_per_day", "INTEGER DEFAULT 0"),
        ("dev_hours", "REAL DEFAULT 0.0"),
        ("dev_hourly_rate", "REAL DEFAULT 150.0"),
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE calculation ADD COLUMN {col_name} {col_type}")
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"✗ Failed to add {col_name}: {e}")
        else:
            print(f"→ Column {col_name} already exists")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Migration completed for: {db_path}")

if __name__ == "__main__":
    # Migrate production database
    prod_db = Path(__file__).parent.parent / "data" / "calculator.db"
    if prod_db.exists():
        print(f"Migrating production database: {prod_db}")
        migrate_database(str(prod_db))
    else:
        print(f"Production database not found: {prod_db}")

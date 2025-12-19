#!/usr/bin/env python3
"""Small script to verify DB persistence: save a calculation and read it back."""
from src.database.db_manager import DatabaseManager
from datetime import datetime


def main():
    db = DatabaseManager()

    calculation_data = {
        "process_name": "Teste Persistencia - Script",
        "current_time_per_month": 176.0,
        "people_involved": 5,
        "hourly_rate": 23.863636363636363,
        "rpa_implementation_cost": 56000.0,
        "rpa_monthly_cost": 700.0,
        "expected_automation_percentage": 90.0,
        "monthly_savings": 18200.0,
        "annual_savings": 218400.0,
        "payback_period_months": 3.08,
        "roi_first_year": 162400.0,
        "roi_percentage_first_year": 290.0,
    }

    print("Saving calculation to DB...")
    calc = db.save_calculation(calculation_data)
    print(f"Saved: {calc}")

    print("Reading last 5 calculations directly via sqlite3:")
    import sqlite3
    from pathlib import Path
    db_path = Path(__file__).parent.parent / "data" / "calculator.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, process_name, roi_percentage_first_year, created_at FROM Calculation ORDER BY id DESC LIMIT 5")
    rows = cur.fetchall()
    for r in rows:
        print(r)
    conn.close()


if __name__ == "__main__":
    main()

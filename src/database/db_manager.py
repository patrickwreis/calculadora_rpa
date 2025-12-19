# -*- coding: utf-8 -*-
"""Database management"""
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
from typing import List, Optional, TYPE_CHECKING
from config import DATABASE_URL

if TYPE_CHECKING:
    from src.models import Calculation


class DatabaseManager:
    """Manage database operations"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        self._create_tables()
        self._migrate_tables()
    
    def _create_tables(self):
        """Create database tables"""
        # Import here to ensure Calculation is registered with SQLModel
        from src.models import Calculation
        from sqlmodel import SQLModel
        
        # Use the correct metadata with all registered models
        SQLModel.metadata.create_all(self.engine)
    
    def _migrate_tables(self):
        """Add missing columns to existing tables"""
        with self.engine.connect() as connection:
            # Check which columns exist
            cursor = connection.execute(text("PRAGMA table_info(calculation)"))
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # Define columns to add with defaults
            columns_to_add = {
                "department": "TEXT DEFAULT ''",
                "complexity": "TEXT DEFAULT 'Média'",
                "systems_quantity": "INTEGER DEFAULT 1",
                "daily_transactions": "INTEGER DEFAULT 100",
                "error_rate": "REAL DEFAULT 0.0",
                "exception_rate": "REAL DEFAULT 0.0",
                "maintenance_percentage": "REAL DEFAULT 10.0",
                "infra_license_cost": "REAL DEFAULT 0.0",
                "other_costs": "REAL DEFAULT 0.0",
                "fines_avoided": "REAL DEFAULT 0.0",
                "sql_savings": "REAL DEFAULT 0.0",
            }
            
            # Add missing columns
            for col_name, col_def in columns_to_add.items():
                if col_name not in existing_columns:
                    try:
                        connection.execute(text(f"ALTER TABLE calculation ADD COLUMN {col_name} {col_def}"))
                        connection.commit()
                    except Exception as e:
                        print(f"Column {col_name} might already exist or error: {e}")
    
    def save_calculation(self, calculation_data: dict) -> "Calculation":
        """Save a calculation to the database"""
        from src.models import Calculation
        calculation = Calculation(**calculation_data)
        with Session(self.engine) as session:
            session.add(calculation)
            session.commit()
            session.refresh(calculation)
        return calculation
    
    def get_all_calculations(self) -> List["Calculation"]:
        """Get all calculations"""
        from src.models import Calculation
        with Session(self.engine) as session:
            statement = select(Calculation)
            calculations = session.exec(statement).all()
        # Ensure a concrete list type is returned to satisfy type checkers
        return list(calculations)
    
    def get_calculation(self, calc_id: int) -> Optional["Calculation"]:
        """Get a specific calculation by ID"""
        from src.models import Calculation
        with Session(self.engine) as session:
            statement = select(Calculation).where(Calculation.id == calc_id)
            calculation = session.exec(statement).first()
        return calculation
    
    def update_calculation(self, calc_id: int, calculation_data: dict) -> Optional["Calculation"]:
        """Update a calculation"""
        from src.models import Calculation
        with Session(self.engine) as session:
            statement = select(Calculation).where(Calculation.id == calc_id)
            calculation = session.exec(statement).first()
            if calculation:
                for key, value in calculation_data.items():
                    if hasattr(calculation, key):
                        setattr(calculation, key, value)
                session.add(calculation)
                session.commit()
                session.refresh(calculation)
                return calculation
        return None
    
    def delete_calculation(self, calc_id: int) -> bool:
        """Delete a calculation"""
        from src.models import Calculation
        with Session(self.engine) as session:
            statement = select(Calculation).where(Calculation.id == calc_id)
            calculation = session.exec(statement).first()
            if calculation:
                session.delete(calculation)
                session.commit()
                return True
        return False

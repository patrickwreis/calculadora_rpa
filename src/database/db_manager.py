# -*- coding: utf-8 -*-
"""Database management"""
from sqlalchemy import create_engine
from sqlmodel import Session, select
from typing import List, Optional
from config import DATABASE_URL
from src.models import Calculation
from src.database.base import SQLModel


class DatabaseManager:
    """Manage database operations"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        SQLModel.metadata.create_all(self.engine)
    
    def save_calculation(self, calculation_data: dict) -> Calculation:
        """Save a calculation to the database"""
        calculation = Calculation(**calculation_data)
        with Session(self.engine) as session:
            session.add(calculation)
            session.commit()
            session.refresh(calculation)
        return calculation
    
    def get_all_calculations(self) -> List[Calculation]:
        """Get all calculations"""
        with Session(self.engine) as session:
            statement = select(Calculation)
            calculations = session.exec(statement).all()
        # Ensure a concrete list type is returned to satisfy type checkers
        return list(calculations)
    
    def get_calculation(self, calc_id: int) -> Optional[Calculation]:
        """Get a specific calculation by ID"""
        with Session(self.engine) as session:
            statement = select(Calculation).where(Calculation.id == calc_id)
            calculation = session.exec(statement).first()
        return calculation
    
    def delete_calculation(self, calc_id: int) -> bool:
        """Delete a calculation"""
        with Session(self.engine) as session:
            statement = select(Calculation).where(Calculation.id == calc_id)
            calculation = session.exec(statement).first()
            if calculation:
                session.delete(calculation)
                session.commit()
                return True
        return False

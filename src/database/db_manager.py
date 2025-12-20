# -*- coding: utf-8 -*-
"""Database management"""
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
from typing import List, Optional, TYPE_CHECKING, Callable, Any
from config import DATABASE_URL
import functools
import time

if TYPE_CHECKING:
    from src.models import Calculation


class CacheManager:
    """Simple cache manager for database queries"""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache manager
        
        Args:
            ttl: Time to live for cached items in seconds (default 5 minutes)
        """
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if still valid"""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.ttl:
                return self._cache[key]
            else:
                # Cache expired, remove it
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()
        self._timestamps.clear()
    
    def clear_key(self, key: str) -> None:
        """Clear specific cache key"""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]


class DatabaseManager:
    """Manage database operations"""
    
    _cache_manager = CacheManager(ttl=300)  # 5 minute cache
    
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
        
        # Invalidate cache when saving
        self._cache_manager.clear_key("all_calculations")
        
        return calculation
    
    def get_all_calculations(self, use_cache: bool = True) -> List["Calculation"]:
        """
        Get all calculations
        
        Args:
            use_cache: Whether to use cached results (default True)
        """
        cache_key = "all_calculations"
        
        # Try cache first
        if use_cache:
            cached = self._cache_manager.get(cache_key)
            if cached is not None:
                return cached
        
        from src.models import Calculation
        with Session(self.engine) as session:
            statement = select(Calculation)
            calculations = session.exec(statement).all()
        
        # Convert to concrete list
        result = list(calculations)
        
        # Cache the result
        if use_cache:
            self._cache_manager.set(cache_key, result)
        
        return result
    
    def get_calculation(self, calc_id: int, use_cache: bool = True) -> Optional["Calculation"]:
        """
        Get a specific calculation by ID
        
        Args:
            calc_id: The calculation ID
            use_cache: Whether to use cached results (default True)
        """
        cache_key = f"calculation_{calc_id}"
        
        # Try cache first
        if use_cache:
            cached = self._cache_manager.get(cache_key)
            if cached is not None:
                return cached
        
        from src.models import Calculation
        with Session(self.engine) as session:
            statement = select(Calculation).where(Calculation.id == calc_id)
            calculation = session.exec(statement).first()
        
        # Cache the result
        if use_cache and calculation:
            self._cache_manager.set(cache_key, calculation)
        
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
                
                # Invalidate cache
                self._cache_manager.clear_key("all_calculations")
                self._cache_manager.clear_key(f"calculation_{calc_id}")
                
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
                
                # Invalidate cache
                self._cache_manager.clear_key("all_calculations")
                self._cache_manager.clear_key(f"calculation_{calc_id}")
                
                return True
        return False
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached data"""
        DatabaseManager._cache_manager.clear()

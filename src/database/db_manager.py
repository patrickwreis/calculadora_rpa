# -*- coding: utf-8 -*-
"""Database management"""
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
from typing import List, Optional, TYPE_CHECKING, Tuple, Any
from config import DATABASE_URL
import functools
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.models import Calculation


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


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
    
    def save_calculation(self, calculation_data: dict) -> Tuple[bool, Optional["Calculation"], Optional[str]]:
        """
        Save a calculation to the database
        
        Args:
            calculation_data: Dictionary with calculation data
            
        Returns:
            Tuple of (success: bool, calculation: Calculation or None, error_message: str or None)
        """
        try:
            from src.models import Calculation
            calculation = Calculation(**calculation_data)
            with Session(self.engine) as session:
                try:
                    session.add(calculation)
                    session.commit()
                    session.refresh(calculation)
                    logger.info(f"Calculation saved: {calculation.id} - {calculation.process_name}")
                except Exception as e:
                    session.rollback()
                    error_msg = f"Database commit failed: {str(e)}"
                    logger.error(error_msg)
                    return False, None, error_msg
            
            # Invalidate cache when saving
            self._cache_manager.clear_key("all_calculations")
            
            return True, calculation, None
        except ValueError as e:
            error_msg = f"Invalid calculation data: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error saving calculation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def get_all_calculations(self, use_cache: bool = True) -> Tuple[bool, List["Calculation"], Optional[str]]:
        """
        Get all calculations
        
        Args:
            use_cache: Whether to use cached results (default True)
            
        Returns:
            Tuple of (success: bool, calculations: list, error_message: str or None)
        """
        try:
            cache_key = "all_calculations"
            
            # Try cache first
            if use_cache:
                cached = self._cache_manager.get(cache_key)
                if cached is not None:
                    logger.debug("Cache hit for all_calculations")
                    return True, cached, None
            
            from src.models import Calculation
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation)
                    calculations = session.exec(statement).all()
                    result = list(calculations)
                    logger.info(f"Retrieved {len(result)} calculations from database")
                except Exception as e:
                    error_msg = f"Database query failed: {str(e)}"
                    logger.error(error_msg)
                    return False, [], error_msg
            
            # Cache the result
            if use_cache:
                self._cache_manager.set(cache_key, result)
            
            return True, result, None
        except Exception as e:
            error_msg = f"Unexpected error getting calculations: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    def get_calculation(self, calc_id: int, use_cache: bool = True) -> Tuple[bool, Optional["Calculation"], Optional[str]]:
        """
        Get a specific calculation by ID
        
        Args:
            calc_id: The calculation ID
            use_cache: Whether to use cached results (default True)
            
        Returns:
            Tuple of (success: bool, calculation: Calculation or None, error_message: str or None)
        """
        try:
            cache_key = f"calculation_{calc_id}"
            
            # Try cache first
            if use_cache:
                cached = self._cache_manager.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache hit for calculation {calc_id}")
                    return True, cached, None
            
            from src.models import Calculation
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation).where(Calculation.id == calc_id)
                    calculation = session.exec(statement).first()
                except Exception as e:
                    error_msg = f"Database query failed: {str(e)}"
                    logger.error(error_msg)
                    return False, None, error_msg
            
            if not calculation:
                logger.warning(f"Calculation {calc_id} not found")
                return True, None, None  # Not an error, just not found
            
            # Cache the result
            if use_cache:
                self._cache_manager.set(cache_key, calculation)
            
            return True, calculation, None
        except Exception as e:
            error_msg = f"Unexpected error getting calculation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def update_calculation(self, calc_id: int, calculation_data: dict) -> Tuple[bool, Optional["Calculation"], Optional[str]]:
        """
        Update a calculation
        
        Args:
            calc_id: The calculation ID to update
            calculation_data: Dictionary with fields to update
            
        Returns:
            Tuple of (success: bool, calculation: Calculation or None, error_message: str or None)
        """
        try:
            from src.models import Calculation
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation).where(Calculation.id == calc_id)
                    calculation = session.exec(statement).first()
                    
                    if not calculation:
                        logger.warning(f"Calculation {calc_id} not found for update")
                        return True, None, None  # Not an error, just not found
                    
                    for key, value in calculation_data.items():
                        if hasattr(calculation, key):
                            setattr(calculation, key, value)
                    
                    session.add(calculation)
                    session.commit()
                    session.refresh(calculation)
                    logger.info(f"Calculation updated: {calc_id}")
                    
                    # Invalidate cache
                    self._cache_manager.clear_key("all_calculations")
                    self._cache_manager.clear_key(f"calculation_{calc_id}")
                    
                    return True, calculation, None
                except Exception as e:
                    session.rollback()
                    error_msg = f"Database transaction failed: {str(e)}"
                    logger.error(error_msg)
                    return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error updating calculation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def delete_calculation(self, calc_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a calculation
        
        Args:
            calc_id: The calculation ID to delete
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            from src.models import Calculation
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation).where(Calculation.id == calc_id)
                    calculation = session.exec(statement).first()
                    
                    if not calculation:
                        logger.warning(f"Calculation {calc_id} not found for deletion")
                        return True, None  # Not an error, just not found
                    
                    session.delete(calculation)
                    session.commit()
                    logger.info(f"Calculation deleted: {calc_id}")
                    
                    # Invalidate cache
                    self._cache_manager.clear_key("all_calculations")
                    self._cache_manager.clear_key(f"calculation_{calc_id}")
                    
                    return True, None
                except Exception as e:
                    session.rollback()
                    error_msg = f"Database transaction failed: {str(e)}"
                    logger.error(error_msg)
                    return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error deleting calculation: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached data"""
        DatabaseManager._cache_manager.clear()
        logger.info("Cache cleared")
    
    # ========== LEGACY METHODS FOR BACKWARD COMPATIBILITY ==========
    
    def save_calculation_legacy(self, calculation_data: dict) -> Optional["Calculation"]:
        """Legacy wrapper for save_calculation"""
        success, calc, _ = self.save_calculation(calculation_data)
        return calc if success else None
    
    def get_all_calculations_legacy(self, use_cache: bool = True) -> List["Calculation"]:
        """Legacy wrapper for get_all_calculations"""
        success, calcs, _ = self.get_all_calculations(use_cache)
        return calcs if success else []
    
    def get_calculation_legacy(self, calc_id: int, use_cache: bool = True) -> Optional["Calculation"]:
        """Legacy wrapper for get_calculation"""
        success, calc, _ = self.get_calculation(calc_id, use_cache)
        return calc if success else None
    
    def update_calculation_legacy(self, calc_id: int, calculation_data: dict) -> Optional["Calculation"]:
        """Legacy wrapper for update_calculation"""
        success, calc, _ = self.update_calculation(calc_id, calculation_data)
        return calc if success else None
    
    def delete_calculation_legacy(self, calc_id: int) -> bool:
        """Legacy wrapper for delete_calculation"""
        success, _ = self.delete_calculation(calc_id)
        return success

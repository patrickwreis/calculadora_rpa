# -*- coding: utf-8 -*-
"""Tests for database manager"""
import pytest
import os
import tempfile
from sqlalchemy import create_engine
from src.database.db_manager import DatabaseManager
from src.models import Calculation


@pytest.fixture
def temp_db():
    """Create a temporary test database"""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def db(temp_db, monkeypatch):
    """Create a test database manager"""
    # Override the DATABASE_URL config
    import config
    original_url = config.DATABASE_URL
    config.DATABASE_URL = f"sqlite:///{temp_db}"
    
    # Create new manager with temp db
    db_manager = DatabaseManager()
    db_manager._cache_manager.clear()  # Ensure no cached data leaks between tests
    
    yield db_manager
    
    # Restore original
    config.DATABASE_URL = original_url


@pytest.fixture
def sample_calculation_data():
    """Sample calculation data for testing"""
    return {
        "process_name": "Test Process",
        "department": "IT",
        "people_involved": 2,
        "current_time_per_month": 40,
        "hourly_rate": 100,
        "complexity": "Media",
        "systems_quantity": 2,
        "daily_transactions": 500,
        "error_rate": 5.0,
        "exception_rate": 2.0,
        "expected_automation_percentage": 80,
        "rpa_implementation_cost": 10000,
        "maintenance_percentage": 10,
        "infra_license_cost": 500,
        "other_costs": 1000,
        "rpa_monthly_cost": 500,
        "fines_avoided": 100,
        "sql_savings": 200,
        "monthly_savings": 5000,
        "annual_savings": 60000,
        "payback_period_months": 2,
        "roi_first_year": 50000,
        "roi_percentage_first_year": 500,
    }


class TestDatabaseSave:
    """Test saving calculations"""
    
    def test_save_calculation(self, db, sample_calculation_data):
        """Test saving a calculation"""
        calc = db.save_calculation_legacy(sample_calculation_data)
        
        assert calc.id is not None
        assert calc.process_name == "Test Process"
        assert calc.department == "IT"
        assert calc.annual_savings == 60000
    
    def test_save_calculation_with_defaults(self, db):
        """Test saving with default values"""
        data = {
            "process_name": "Simple Process",
            "people_involved": 1,
            "current_time_per_month": 20,
            "hourly_rate": 50,
            "expected_automation_percentage": 50,
            "rpa_implementation_cost": 5000,
            "rpa_monthly_cost": 200,
            "monthly_savings": 1000,
            "annual_savings": 12000,
            "payback_period_months": 5,
            "roi_first_year": 7000,
            "roi_percentage_first_year": 140,
        }
        
        calc = db.save_calculation_legacy(data)
        
        assert calc.department == ""  # Default empty string
        assert calc.complexity == "Média"
        assert calc.systems_quantity == 1
        assert calc.daily_transactions == 100
        assert calc.error_rate == 0.0
        assert calc.exception_rate == 0.0
    
    def test_save_and_retrieve_all(self, db, sample_calculation_data):
        """Test saving multiple calculations and retrieving all"""
        # Save first
        calc1 = db.save_calculation_legacy(sample_calculation_data)
        
        # Save second with modified name
        data2 = {**sample_calculation_data, "process_name": "Process 2"}
        calc2 = db.save_calculation_legacy(data2)
        
        # Get all
        all_calcs = db.get_all_calculations_legacy()
        assert len(all_calcs) >= 2
        process_names = [c.process_name for c in all_calcs]
        assert "Test Process" in process_names
        assert "Process 2" in process_names


class TestDatabaseGet:
    """Test retrieving calculations"""
    
    def test_get_calculation_by_id(self, db, sample_calculation_data):
        """Test getting a specific calculation by ID"""
        saved = db.save_calculation_legacy(sample_calculation_data)
        
        calc = db.get_calculation_legacy(saved.id)
        assert calc is not None
        assert calc.id == saved.id
        assert calc.process_name == "Test Process"
        assert calc.department == "IT"
    
    def test_get_calculation_not_found(self, db):
        """Test getting a calculation that doesn't exist"""
        calc = db.get_calculation_legacy(999)
        assert calc is None


class TestDatabaseUpdate:
    """Test updating calculations"""
    
    def test_update_calculation(self, db, sample_calculation_data):
        """Test updating a calculation"""
        saved = db.save_calculation_legacy(sample_calculation_data)
        
        update_data = {
            "process_name": "Updated Process",
            "department": "Finance",
            "annual_savings": 70000,
        }
        
        updated = db.update_calculation_legacy(saved.id, update_data)
        
        assert updated is not None
        assert updated.process_name == "Updated Process"
        assert updated.department == "Finance"
        assert updated.annual_savings == 70000
    
    def test_update_calculation_not_found(self, db):
        """Test updating a calculation that doesn't exist"""
        update_data = {"process_name": "Updated"}
        result = db.update_calculation_legacy(999, update_data)
        
        assert result is None
    
    def test_update_calculation_partial(self, db, sample_calculation_data):
        """Test updating only some fields"""
        saved = db.save_calculation_legacy(sample_calculation_data)
        original_savings = saved.annual_savings
        
        # Update only department
        updated = db.update_calculation_legacy(saved.id, {"department": "HR"})
        
        assert updated.department == "HR"
        assert updated.process_name == "Test Process"  # Unchanged
        assert updated.annual_savings == original_savings  # Unchanged
    
    def test_update_calculation_with_invalid_field(self, db, sample_calculation_data):
        """Test updating with a field that doesn't exist"""
        saved = db.save_calculation_legacy(sample_calculation_data)
        
        # This should not raise an error, just ignore the invalid field
        updated = db.update_calculation_legacy(saved.id, {
            "process_name": "Updated",
            "invalid_field": "should_be_ignored"
        })
        
        assert updated is not None
        assert updated.process_name == "Updated"
        # Invalid field should not be added


class TestDatabaseDelete:
    """Test deleting calculations"""
    
    def test_delete_calculation(self, db, sample_calculation_data):
        """Test deleting a calculation"""
        saved = db.save_calculation_legacy(sample_calculation_data)
        
        result = db.delete_calculation_legacy(saved.id)
        assert result is True
        
        # Verify it's deleted
        calc = db.get_calculation_legacy(saved.id)
        assert calc is None
    
    def test_delete_calculation_not_found(self, db):
        """Test deleting a calculation that doesn't exist (idempotent operation)"""
        result = db.delete_calculation_legacy(999)
        # Should return True because delete is idempotent - no error deleting non-existent record
        assert result is True


class TestUserFiltering:
    """Test user_id filtering functionality"""
    
    def test_save_with_user_id(self, db, sample_calculation_data):
        """Test saving calculation with specific user_id"""
        data = {**sample_calculation_data, "user_id": 1}
        success, calc, error = db.save_calculation(data)
        
        assert success is True
        assert calc is not None
        assert calc.user_id == 1
        assert error is None
    
    def test_get_all_calculations_default_user(self, db, sample_calculation_data):
        """Test retrieving calculations defaults to user_id=1"""
        # Clear cache first
        db._cache_manager.clear()
        
        # Save for user 1
        data1 = {**sample_calculation_data, "user_id": 1, "process_name": "User1_Process_Unique"}
        success1, calc1, _ = db.save_calculation(data1)
        
        # Get all for user 1 (default)
        success, calcs, error = db.get_all_calculations(user_id=1, use_cache=False)
        
        assert success is True
        assert error is None
        assert len(calcs) >= 1
        
        # Verify all are for user 1
        for calc in calcs:
            assert calc.user_id == 1
    
    def test_get_all_calculations_by_user_id(self, db, sample_calculation_data):
        """Test filtering calculations by specific user_id"""
        # Clear cache first
        db._cache_manager.clear()
        
        # Save for user 1
        data_user1 = {**sample_calculation_data, "user_id": 1, "process_name": "UniqueUser1"}
        success1, calc1, _ = db.save_calculation(data_user1)
        
        # Save for user 2
        data_user2 = {**sample_calculation_data, "user_id": 2, "process_name": "UniqueUser2"}
        success2, calc2, _ = db.save_calculation(data_user2)
        
        # Get all for user 1
        success, calcs_user1, error = db.get_all_calculations(user_id=1, use_cache=False)
        assert success is True
        user1_names = [c.process_name for c in calcs_user1]
        assert "UniqueUser1" in user1_names
        
        # Get all for user 2
        success, calcs_user2, error = db.get_all_calculations(user_id=2, use_cache=False)
        assert success is True
        user2_names = [c.process_name for c in calcs_user2]
        assert "UniqueUser2" in user2_names
    
    def test_user_isolation(self, db, sample_calculation_data):
        """Test that users cannot see each other's calculations"""
        # Clear cache first
        db._cache_manager.clear()
        
        # Save for user 1
        data_user1 = {**sample_calculation_data, "user_id": 1, "process_name": "Secret_User_1_Private"}
        success1, calc1, _ = db.save_calculation(data_user1)
        
        # Save for user 2
        data_user2 = {**sample_calculation_data, "user_id": 2, "process_name": "Secret_User_2_Private"}
        success2, calc2, _ = db.save_calculation(data_user2)
        
        # User 1 should only see their own
        success, calcs_user1, error = db.get_all_calculations(user_id=1, use_cache=False)
        user1_names = [c.process_name for c in calcs_user1]
        assert "Secret_User_1_Private" in user1_names
        assert "Secret_User_2_Private" not in user1_names
        
        # User 2 should only see their own
        success, calcs_user2, error = db.get_all_calculations(user_id=2, use_cache=False)
        user2_names = [c.process_name for c in calcs_user2]
        assert "Secret_User_2_Private" in user2_names
        assert "Secret_User_1_Private" not in user2_names
    
    def test_default_user_id_is_one(self, db, sample_calculation_data):
        """Test that calculations default to user_id=1 if not specified"""
        # Save without specifying user_id (should default to 1)
        success, calc, error = db.save_calculation(sample_calculation_data)
        
        assert success is True
        assert calc.user_id == 1
    
    def test_classification_with_user_id(self, db, sample_calculation_data):
        """Test that classification works with user_id"""
        data = {
            **sample_calculation_data,
            "user_id": 1,
            "roi_percentage_first_year": 100,
            "payback_period_months": 6,
        }
        success, calc, error = db.save_calculation(data)
        
        assert success is True
        assert calc.classification == "QUICK WIN"
        assert calc.user_id == 1

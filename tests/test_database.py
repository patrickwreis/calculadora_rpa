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
        calc = db.save_calculation(sample_calculation_data)
        
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
        
        calc = db.save_calculation(data)
        
        assert calc.department == ""  # Default empty string
        assert calc.complexity == "Média"
        assert calc.systems_quantity == 1
        assert calc.daily_transactions == 100
        assert calc.error_rate == 0.0
        assert calc.exception_rate == 0.0
    
    def test_save_and_retrieve_all(self, db, sample_calculation_data):
        """Test saving multiple calculations and retrieving all"""
        # Save first
        calc1 = db.save_calculation(sample_calculation_data)
        
        # Save second with modified name
        data2 = {**sample_calculation_data, "process_name": "Process 2"}
        calc2 = db.save_calculation(data2)
        
        # Get all
        all_calcs = db.get_all_calculations()
        assert len(all_calcs) >= 2
        process_names = [c.process_name for c in all_calcs]
        assert "Test Process" in process_names
        assert "Process 2" in process_names


class TestDatabaseGet:
    """Test retrieving calculations"""
    
    def test_get_calculation_by_id(self, db, sample_calculation_data):
        """Test getting a specific calculation by ID"""
        saved = db.save_calculation(sample_calculation_data)
        
        calc = db.get_calculation(saved.id)
        assert calc is not None
        assert calc.id == saved.id
        assert calc.process_name == "Test Process"
        assert calc.department == "IT"
    
    def test_get_calculation_not_found(self, db):
        """Test getting a calculation that doesn't exist"""
        calc = db.get_calculation(999)
        assert calc is None


class TestDatabaseUpdate:
    """Test updating calculations"""
    
    def test_update_calculation(self, db, sample_calculation_data):
        """Test updating a calculation"""
        saved = db.save_calculation(sample_calculation_data)
        
        update_data = {
            "process_name": "Updated Process",
            "department": "Finance",
            "annual_savings": 70000,
        }
        
        updated = db.update_calculation(saved.id, update_data)
        
        assert updated is not None
        assert updated.process_name == "Updated Process"
        assert updated.department == "Finance"
        assert updated.annual_savings == 70000
    
    def test_update_calculation_not_found(self, db):
        """Test updating a calculation that doesn't exist"""
        update_data = {"process_name": "Updated"}
        result = db.update_calculation(999, update_data)
        
        assert result is None
    
    def test_update_calculation_partial(self, db, sample_calculation_data):
        """Test updating only some fields"""
        saved = db.save_calculation(sample_calculation_data)
        original_savings = saved.annual_savings
        
        # Update only department
        updated = db.update_calculation(saved.id, {"department": "HR"})
        
        assert updated.department == "HR"
        assert updated.process_name == "Test Process"  # Unchanged
        assert updated.annual_savings == original_savings  # Unchanged
    
    def test_update_calculation_with_invalid_field(self, db, sample_calculation_data):
        """Test updating with a field that doesn't exist"""
        saved = db.save_calculation(sample_calculation_data)
        
        # This should not raise an error, just ignore the invalid field
        updated = db.update_calculation(saved.id, {
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
        saved = db.save_calculation(sample_calculation_data)
        
        result = db.delete_calculation(saved.id)
        assert result is True
        
        # Verify it's deleted
        calc = db.get_calculation(saved.id)
        assert calc is None
    
    def test_delete_calculation_not_found(self, db):
        """Test deleting a calculation that doesn't exist"""
        result = db.delete_calculation(999)
        assert result is False


class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_crud_workflow(self, db, sample_calculation_data):
        """Test complete CRUD workflow"""
        # Create
        saved = db.save_calculation(sample_calculation_data)
        assert saved.id is not None
        
        # Read
        retrieved = db.get_calculation(saved.id)
        assert retrieved.process_name == "Test Process"
        
        # Update
        updated = db.update_calculation(saved.id, {"process_name": "Updated"})
        assert updated.process_name == "Updated"
        
        # Verify update
        re_retrieved = db.get_calculation(saved.id)
        assert re_retrieved.process_name == "Updated"
        
        # Delete
        deleted = db.delete_calculation(saved.id)
        assert deleted is True
        
        # Verify deletion
        final = db.get_calculation(saved.id)
        assert final is None

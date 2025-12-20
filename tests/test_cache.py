# -*- coding: utf-8 -*-
"""Tests for Database Caching"""
import pytest
from src.database.db_manager import DatabaseManager, CacheManager


class TestCacheManager:
    """Test suite for CacheManager"""
    
    def test_cache_set_and_get(self):
        """Test setting and getting cache"""
        cache = CacheManager(ttl=300)
        cache.set("test_key", "test_value")
        
        result = cache.get("test_key")
        assert result == "test_value"
    
    def test_cache_get_nonexistent(self):
        """Test getting nonexistent cache key"""
        cache = CacheManager(ttl=300)
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = CacheManager(ttl=0)  # Immediate expiration
        cache.set("test_key", "test_value")
        
        # Wait a tiny bit to ensure expiration
        import time
        time.sleep(0.01)
        
        result = cache.get("test_key")
        assert result is None
    
    def test_cache_clear(self):
        """Test clearing all cache"""
        cache = CacheManager(ttl=300)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_clear_specific_key(self):
        """Test clearing specific cache key"""
        cache = CacheManager(ttl=300)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear_key("key1")
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestDatabaseManagerCache:
    """Test suite for DatabaseManager caching"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance"""
        return DatabaseManager()
    
    def test_get_all_calculations_uses_cache(self, db_manager):
        """Test that get_all_calculations uses cache"""
        # First call should query database
        success1, result1, err1 = db_manager.get_all_calculations(use_cache=True)
        
        # Second call should use cache
        success2, result2, err2 = db_manager.get_all_calculations(use_cache=True)
        
        # Results should be successful and same length
        assert success1 is True
        assert success2 is True
        assert len(result1) == len(result2)
    
    def test_get_all_calculations_bypass_cache(self, db_manager):
        """Test bypassing cache"""
        success1, result1, _ = db_manager.get_all_calculations(use_cache=False)
        success2, result2, _ = db_manager.get_all_calculations(use_cache=False)
        
        # Both should work correctly even without cache
        assert success1 is True
        assert success2 is True
        assert isinstance(result1, list)
        assert isinstance(result2, list)
    
    def test_cache_invalidation_on_save(self, db_manager):
        """Test that cache is invalidated on save"""
        # Clear cache to start fresh
        db_manager.clear_cache()
        
        # Get all calculations (fills cache)
        success1, result1, _ = db_manager.get_all_calculations(use_cache=True)
        count1 = len(result1) if success1 else 0
        
        # Save a new calculation
        calculation_data = {
            'process_name': 'Cache Test Process New',
            'current_time_per_month': 100.0,
            'people_involved': 1,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'monthly_savings': 1000.0,
            'annual_savings': 12000.0,
            'payback_period_months': 5.0,
            'roi_first_year': 7000.0,
            'roi_percentage_first_year': 140.0,
        }
        
        success_save, saved_calc, error_save = db_manager.save_calculation(calculation_data)
        
        # Save should succeed
        assert success_save is True
        assert saved_calc is not None
        
        # Get all calculations again (should query database, not use old cache)
        success2, result2, _ = db_manager.get_all_calculations(use_cache=True)
        count2 = len(result2) if success2 else count1
        
        # Count should increase
        assert count2 > count1
    
    def test_cache_invalidation_on_update(self, db_manager):
        """Test that cache is invalidated on update"""
        db_manager.clear_cache()
        
        # Create a calculation
        calculation_data = {
            'process_name': 'Update Cache Test New',
            'current_time_per_month': 100.0,
            'people_involved': 1,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'monthly_savings': 1000.0,
            'annual_savings': 12000.0,
            'payback_period_months': 5.0,
            'roi_first_year': 7000.0,
            'roi_percentage_first_year': 140.0,
        }
        
        success_save, calc, _ = db_manager.save_calculation(calculation_data)
        assert success_save is True
        calc_id = calc.id
        
        # Get and cache it
        success1, result1, _ = db_manager.get_calculation(calc_id, use_cache=True)
        assert success1 is True
        assert result1.process_name == 'Update Cache Test New'
        
        # Update it
        success_upd, result_upd, _ = db_manager.update_calculation(calc_id, {'process_name': 'Updated Name New'})
        assert success_upd is True
        
        # Get it again (should reflect update)
        success2, result2, _ = db_manager.get_calculation(calc_id, use_cache=True)
        assert success2 is True
        assert result2.process_name == 'Updated Name New'
    
    def test_cache_invalidation_on_delete(self, db_manager):
        """Test that cache is invalidated on delete"""
        db_manager.clear_cache()
        
        # Create a calculation
        calculation_data = {
            'process_name': 'Delete Cache Test New',
            'current_time_per_month': 100.0,
            'people_involved': 1,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'monthly_savings': 1000.0,
            'annual_savings': 12000.0,
            'payback_period_months': 5.0,
            'roi_first_year': 7000.0,
            'roi_percentage_first_year': 140.0,
        }
        
        success_save, calc, _ = db_manager.save_calculation(calculation_data)
        assert success_save is True
        calc_id = calc.id
        
        # Cache it
        success1, result1, _ = db_manager.get_all_calculations(use_cache=True)
        count1 = len(result1) if success1 else 0
        
        # Delete it
        success_del, error_del = db_manager.delete_calculation(calc_id)
        assert success_del is True
        
        # Get all calculations again (should reflect deletion)
        success2, result2, _ = db_manager.get_all_calculations(use_cache=True)
        count2 = len(result2) if success2 else 0
        
        # Count should decrease
        assert count2 < count1
    
    def test_clear_cache_static_method(self, db_manager):
        """Test static clear_cache method"""
        db_manager.clear_cache()
        
        # Cache should be empty, get should still work
        success, result, _ = db_manager.get_all_calculations(use_cache=True)
        assert success is True
        assert isinstance(result, list)
